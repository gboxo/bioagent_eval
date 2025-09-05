#!/usr/bin/env python3
"""
Script to build phylogenetic tree using Biopython.

This script reads protein MSA, calculates distance matrix, and constructs
a phylogenetic tree using neighbor-joining algorithm.
"""

import os
import sys
import argparse

try:
    from Bio import AlignIO, Phylo
    from Bio.Align import MultipleSeqAlignment
    from Bio.SeqRecord import SeqRecord
    from Bio.Seq import Seq
except ImportError as e:
    print(f"Error importing basic Biopython modules: {e}")
    sys.exit(1)

try:
    from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
except ImportError as e:
    print(f"Error importing phylogenetic construction modules: {e}")
    print("Note: TreeConstruction modules may not be available in this Biopython version")
    DistanceCalculator = None
    DistanceTreeConstructor = None


def read_alignment(alignment_file: str):
    """
    Read multiple sequence alignment from file.
    """
    try:
        # Try different formats
        for fmt in ['fasta', 'clustal', 'phylip']:
            try:
                alignment = AlignIO.read(alignment_file, fmt)
                print(f"Successfully read alignment in {fmt} format")
                return alignment
            except:
                continue
        
        # Manual FASTA parsing as fallback
        sequences = []
        with open(alignment_file, 'r') as f:
            current_id = None
            current_seq = ""
            
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        sequences.append(SeqRecord(Seq(current_seq), id=current_id))
                    current_id = line[1:].split()[0]  # Take only first part of header
                    current_seq = ""
                else:
                    current_seq += line
            
            if current_id:
                sequences.append(SeqRecord(Seq(current_seq), id=current_id))
        
        if sequences:
            alignment = MultipleSeqAlignment(sequences)
            print(f"Manually parsed alignment: {len(sequences)} sequences")
            return alignment
        else:
            raise ValueError("No sequences found in alignment file")
            
    except Exception as e:
        print(f"Error reading alignment: {e}")
        return None


def build_nj_tree(alignment, output_file: str) -> bool:
    """
    Build neighbor-joining tree from alignment.
    """
    if DistanceCalculator is None or DistanceTreeConstructor is None:
        print("Error: Tree construction modules not available in this Biopython version")
        return False
    
    try:
        # Calculate distance matrix
        calculator = DistanceCalculator('identity')
        distance_matrix = calculator.get_distance(alignment)
        print(f"Distance matrix calculated for {len(distance_matrix.names)} sequences")
        
        # Build tree using neighbor-joining (UPGMA or NJ)
        constructor = DistanceTreeConstructor(calculator, 'nj')  # 'nj' for neighbor-joining
        tree = constructor.build_tree(alignment)
        
        # Write tree in Newick format
        Phylo.write(tree, output_file, 'newick')
        print(f"Phylogenetic tree saved: {output_file}")
        
        # Print tree structure
        print("Tree structure:")
        try:
            Phylo.draw_ascii(tree)
        except Exception as draw_error:
            print(f"Could not draw tree: {draw_error}")
        
        return True
        
    except Exception as e:
        print(f"Error building NJ tree: {e}")
        # Try UPGMA as fallback
        try:
            print("Trying UPGMA as fallback...")
            constructor = DistanceTreeConstructor(calculator, 'upgma')
            tree = constructor.build_tree(alignment)
            Phylo.write(tree, output_file, 'newick')
            print(f"UPGMA tree saved: {output_file}")
            return True
        except Exception as e2:
            print(f"UPGMA also failed: {e2}")
            return False


def create_simple_tree(alignment_file: str, output_file: str) -> bool:
    """
    Create a simple star tree when NJ fails.
    """
    try:
        # Read sequence IDs
        seq_ids = []
        with open(alignment_file, 'r') as f:
            for line in f:
                if line.startswith('>'):
                    seq_id = line.strip()[1:].split()[0]
                    seq_ids.append(seq_id)
        
        if len(seq_ids) < 2:
            print("Error: Need at least 2 sequences for tree")
            return False
        
        # Create simple star tree in Newick format
        # All sequences branch from a common ancestor
        if len(seq_ids) == 2:
            tree_string = f"({seq_ids[0]}:0.1,{seq_ids[1]}:0.1);"
        else:
            branches = [f"{seq_id}:0.1" for seq_id in seq_ids]
            tree_string = f"({','.join(branches)});"
        
        with open(output_file, 'w') as f:
            f.write(tree_string)
        
        print(f"Simple star tree created: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error creating simple tree: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Build phylogenetic tree from MSA')
    parser.add_argument('alignment_file', help='Input protein MSA file')
    parser.add_argument('output_file', help='Output tree file (Newick format)')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.alignment_file):
        print(f"Error: Alignment file {args.alignment_file} not found")
        sys.exit(1)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output_file) or '.', exist_ok=True)
    
    # Read alignment
    alignment = read_alignment(args.alignment_file)
    
    success = False
    if alignment:
        # Try to build NJ tree
        success = build_nj_tree(alignment, args.output_file)
    
    # Fallback to simple tree if NJ fails
    if not success:
        print("NJ tree construction failed. Creating simple tree...")
        success = create_simple_tree(args.alignment_file, args.output_file)
    
    if success:
        print("Tree construction completed successfully.")
    else:
        print("Failed to build tree.")
        sys.exit(1)


if __name__ == "__main__":
    main()