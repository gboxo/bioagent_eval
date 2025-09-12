#!/usr/bin/env python3
"""
Script to create codon alignment using pal2nal.pl.

This script uses pal2nal.pl to generate a codon-correct nucleotide alignment
in PAML format from protein MSA and nucleotide CDS sequences.
"""

import os
import sys
import subprocess
import argparse
import shutil
import tempfile


def download_pal2nal(script_dir):
    """
    Download pal2nal.pl script if not available.
    """
    pal2nal_dir = os.path.join(script_dir, "pal2nal")
    pal2nal_script = os.path.join(pal2nal_dir, "pal2nal.pl")
    
    # Check if already downloaded
    if os.path.exists(pal2nal_script):
        return pal2nal_script
    
    pal2nal_url = "http://www.bork.embl.de/pal2nal/distribution/pal2nal.v14.tar.gz"
    
    try:
        import urllib.request
        import tarfile
        
        # Create directory for pal2nal
        os.makedirs(pal2nal_dir, exist_ok=True)
        
        # Download and extract pal2nal
        print("Downloading pal2nal.pl...")
        tar_path = os.path.join(pal2nal_dir, "pal2nal.tar.gz")
        urllib.request.urlretrieve(pal2nal_url, tar_path)
        
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=pal2nal_dir)
        
        # Find the perl script
        for root, dirs, files in os.walk(pal2nal_dir):
            for file in files:
                if file == "pal2nal.pl":
                    pal2nal_path = os.path.join(root, file)
                    # Make executable
                    os.chmod(pal2nal_path, 0o755)
                    print(f"pal2nal.pl downloaded and installed at: {pal2nal_path}")
                    return pal2nal_path
        
    except Exception as e:
        print(f"Error downloading pal2nal.pl: {e}")
    
    return None


def create_codon_alignment_fallback(protein_msa: str, cds_file: str, output_file: str) -> bool:
    """
    Create a simple codon alignment when pal2nal.pl is not available.
    """
    try:
        # Read protein MSA
        protein_seqs = {}
        with open(protein_msa, 'r') as f:
            current_id = None
            current_seq = ""
            
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        protein_seqs[current_id] = current_seq
                    current_id = line[1:]
                    current_seq = ""
                else:
                    current_seq += line
            
            if current_id:
                protein_seqs[current_id] = current_seq
        
        # Read CDS sequences
        cds_seqs = {}
        with open(cds_file, 'r') as f:
            current_id = None
            current_seq = ""
            
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        cds_seqs[current_id] = current_seq
                    current_id = line[1:]
                    current_seq = ""
                else:
                    current_seq += line
            
            if current_id:
                cds_seqs[current_id] = current_seq
        
        # Create codon alignment
        codon_alignment = {}
        
        for seq_id in protein_seqs:
            if seq_id not in cds_seqs:
                print(f"Warning: No CDS found for {seq_id}")
                continue
            
            protein_aligned = protein_seqs[seq_id]
            cds_seq = cds_seqs[seq_id]
            
            # Remove gaps from protein to match with CDS
            protein_nogaps = protein_aligned.replace('-', '')
            
            # Create codon alignment
            codon_aligned = ""
            cds_pos = 0
            
            for aa in protein_aligned:
                if aa == '-':
                    codon_aligned += "---"
                else:
                    if cds_pos + 3 <= len(cds_seq):
                        codon_aligned += cds_seq[cds_pos:cds_pos+3]
                        cds_pos += 3
                    else:
                        codon_aligned += "NNN"
            
            codon_alignment[seq_id] = codon_aligned
        
        # Write PAML format
        with open(output_file, 'w') as f:
            # Write header
            f.write(f"   {len(codon_alignment)}   {len(list(codon_alignment.values())[0])}\n")
            
            # Write sequences
            for seq_id, seq in codon_alignment.items():
                f.write(f"{seq_id}\n{seq}\n")
        
        print(f"Fallback codon alignment created: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error creating fallback codon alignment: {e}")
        return False


def run_pal2nal(protein_msa: str, cds_file: str, output_file: str) -> bool:
    """
    Run pal2nal.pl to create codon alignment.
    """
    # Look for pal2nal.pl in various locations
    pal2nal_paths = [
        'pal2nal.pl',
        './pal2nal.pl',
        '/usr/local/bin/pal2nal.pl',
        '/usr/bin/pal2nal.pl'
    ]
    
    pal2nal_path = None
    for path in pal2nal_paths:
        if shutil.which(path) or os.path.isfile(path):
            pal2nal_path = path
            break
    
    # Try to download if not found
    if not pal2nal_path:
        print("pal2nal.pl not found. Attempting to download...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pal2nal_path = download_pal2nal(script_dir)
    
    if not pal2nal_path:
        print("pal2nal.pl not available. Using fallback method...")
        return create_codon_alignment_fallback(protein_msa, cds_file, output_file)
    
    try:
        # Run pal2nal.pl
        cmd = ['perl', pal2nal_path, protein_msa, cds_file, '-output', 'paml', '-nomismatch']
        
        with open(output_file, 'w') as outf:
            result = subprocess.run(cmd, stdout=outf, stderr=subprocess.PIPE, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"pal2nal codon alignment completed: {output_file}")
            return True
        else:
            print(f"pal2nal error: {result.stderr}")
            print("Using fallback method...")
            return create_codon_alignment_fallback(protein_msa, cds_file, output_file)
            
    except Exception as e:
        print(f"Error running pal2nal: {e}")
        print("Using fallback method...")
        return create_codon_alignment_fallback(protein_msa, cds_file, output_file)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Create codon alignment using pal2nal.pl')
    parser.add_argument('protein_msa', help='Input protein MSA file')
    parser.add_argument('cds_file', help='Input CDS FASTA file')
    parser.add_argument('output_file', help='Output codon alignment file (PAML format)')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.protein_msa):
        print(f"Error: Protein MSA file {args.protein_msa} not found")
        sys.exit(1)
    
    if not os.path.isfile(args.cds_file):
        print(f"Error: CDS file {args.cds_file} not found")
        sys.exit(1)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output_file) or '.', exist_ok=True)
    
    # Run codon alignment
    success = run_pal2nal(args.protein_msa, args.cds_file, args.output_file)
    
    if success:
        print("Codon alignment creation completed successfully.")
    else:
        print("Failed to create codon alignment.")
        sys.exit(1)


if __name__ == "__main__":
    main()