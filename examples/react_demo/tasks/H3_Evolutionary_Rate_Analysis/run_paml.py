#!/usr/bin/env python3
"""
Script to setup and run PAML analysis.

This script creates the control file for PAML codeml and runs the analysis
to estimate dN/dS ratios for each branch.
"""

import os
import sys
import subprocess
import argparse
import shutil


def create_codeml_control_file(alignment_file: str, tree_file: str, control_file: str) -> None:
    """
    Create codeml control file for branch model analysis.
    """
    control_content = f"""      seqfile = {alignment_file}   * sequence data file name
     treefile = {tree_file}      * tree structure file name
      outfile = mlc           * main result file name

        noisy = 9  * 0,1,2,3,9: how much rubbish on the screen
      verbose = 1  * 1: detailed output, 0: concise output
      runmode = 0  * 0: user tree;  1: semi-automatic;  2: automatic
                   * 3: StepwiseAddition; (4,5):PerturbationNNI

      seqtype = 1  * 1:codons; 2:AAs; 3:codons-->AAs
    CodonFreq = 2  * 0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table

        model = 2  * models for codons:
                   * 0:one, 1:b, 2:2 or more dN/dS ratios for branches

      NSsites = 0  * 0:one w;1:neutral;2:selection; 3:discrete;4:freqs;
                   * 5:gamma;6:2gamma;7:beta;8:beta&w;9:beta&gamma;
                   * 10:beta&gamma+1; 11:beta&normal>1; 12:0&2normal>1;
                   * 13:3normal>0

        icode = 0  * 0:universal code; 1:mammalian mt; 2-10:see below

    fix_kappa = 0  * 1: kappa fixed, 0: kappa to be estimated
        kappa = 2  * initial or fixed kappa

    fix_omega = 0  * 1: omega or omega_1 fixed, 0: estimate
        omega = 1  * initial or fixed omega, for codons or codon-based AAs

    fix_alpha = 1  * 0: estimate gamma shape parameter; 1: fix it at alpha
        alpha = 0  * initial or fixed alpha, 0:infinity (constant rate)
       Malpha = 0  * different alphas for genes
        ncatG = 8  * # of categories in dG of NSsites models

        getSE = 0  * 0: don't want them, 1: want S.E.s of estimates
 RateAncestor = 0  * (0,1,2): rates (alpha>0) or ancestral states (1 or 2)

   Small_Diff = .5e-6
    cleandata = 1  * remove sites with ambiguity data (1:yes, 0:no)?
*        fix_blength = 0  * 0: ignore, -1: random, 1: initial, 2: fixed
       method = 0  * Optimization method 0: simultaneous; 1: one branch a time
"""

    with open(control_file, 'w') as f:
        f.write(control_content)

    print(f"PAML control file created: {control_file}")


def run_codeml(control_file: str) -> bool:
    """
    Run codeml program.
    """
    try:
        # Check if codeml is available
        if not shutil.which('codeml'):
            print("Error: codeml not found in PATH. Please install PAML.")
            return False

        # Run codeml
        result = subprocess.run(['codeml', control_file],
                              capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            print("PAML codeml analysis completed successfully.")
            print("Output files generated:")
            if os.path.exists('mlc'):
                print("  - mlc (main results)")
            if os.path.exists('2ML.dN'):
                print("  - 2ML.dN (dN estimates)")
            if os.path.exists('2ML.dS'):
                print("  - 2ML.dS (dS estimates)")
            if os.path.exists('2ML.t'):
                print("  - 2ML.t (tree with branch lengths)")
            return True
        else:
            print(f"codeml failed with error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("codeml analysis timed out")
        return False
    except Exception as e:
        print(f"Error running codeml: {e}")
        return False


def create_mock_results(output_dir: str) -> bool:
    """
    Create mock PAML results for testing when codeml is not available.
    """
    try:
        mlc_content = """CODON model: branch model
dN/dS (w) for branches:  0 1 2 3 4 5 6 7 8 9 10

branch          t       N       S   dN/dS      dN      dS  N*dN  S*dS

   2..1       0.012   123.4    45.6   0.234   0.003   0.013   0.4   0.6
   2..3       0.018   123.4    45.6   1.567   0.008   0.005   1.0   0.2
   3..4       0.022   123.4    45.6   0.445   0.007   0.016   0.9   0.7
   3..5       0.015   123.4    45.6   2.134   0.009   0.004   1.1   0.2
   5..6       0.019   123.4    45.6   0.789   0.006   0.008   0.7   0.4
   5..7       0.021   123.4    45.6   1.234   0.008   0.006   1.0   0.3
   7..8       0.016   123.4    45.6   0.567   0.005   0.009   0.6   0.4
   7..9       0.020   123.4    45.6   1.678   0.009   0.005   1.1   0.2

Tree with branch labels for method branch:
"""

        with open('mlc', 'w') as f:
            f.write(mlc_content)

        print("Mock PAML results created for testing.")
        return True

    except Exception as e:
        print(f"Error creating mock results: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run PAML codeml analysis')
    parser.add_argument('alignment_file', help='Input codon alignment file (PAML format)')
    parser.add_argument('tree_file', help='Input tree file (Newick format)')
    parser.add_argument('--control-file', default='codeml.ctl', help='Control file name')

    args = parser.parse_args()


    # Create control file
    create_codeml_control_file(args.alignment_file, args.tree_file, args.control_file)


    success = run_codeml(args.control_file)




if __name__ == "__main__":
    main()
