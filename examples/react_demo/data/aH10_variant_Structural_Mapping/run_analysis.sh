#!/bin/bash
"""
Main script to run the structural mapping analysis in the correct order.
This script coordinates the execution of DSSP calculation and Python analysis.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if required tools are available
check_dependencies() {
    print_status $YELLOW "Checking dependencies..."
    
    # Check for mkdssp
    if ! command -v mkdssp &> /dev/null; then
        print_status $RED "Error: mkdssp is not installed or not in PATH"
        print_status $YELLOW "Please install DSSP (Dictionary of Secondary Structure of Proteins)"
        print_status $YELLOW "On macOS: brew install brewsci/bio/dssp"
        print_status $YELLOW "On Ubuntu: sudo apt-get install dssp"
        exit 1
    fi
    
    # Check for Python and Biopython
    if ! python3 -c "import Bio.PDB" &> /dev/null; then
        print_status $RED "Error: Biopython is not installed"
        print_status $YELLOW "Please install Biopython: pip install biopython"
        exit 1
    fi
    
    print_status $GREEN "All dependencies are available."
}

# Function to process a single variant
process_variant() {
    local variant_folder="$1"
    
    if [[ ! -d "$variant_folder" ]]; then
        print_status $RED "Error: Variant folder not found: $variant_folder"
        return 1
    fi
    
    print_status $YELLOW "Processing variant: $(basename $variant_folder)"
    
    # Step 1: Run DSSP calculation
    print_status $YELLOW "Step 1: Running DSSP calculation..."
    ./run_dssp.sh "$variant_folder"
    
    # Step 2: Run Python analysis
    print_status $YELLOW "Step 2: Running structural analysis..."
    python3 analyze_structure.py "$variant_folder"
    
    print_status $GREEN "Variant $(basename $variant_folder) processing completed."
}

# Main function
main() {
    print_status $GREEN "Starting Structural Mapping Analysis"
    print_status $GREEN "======================================"
    
    # Check dependencies
    check_dependencies
    
    # Make scripts executable
    chmod +x run_dssp.sh
    chmod +x analyze_structure.py
    
    # Process variant_1 as specified in the task
    if [[ $# -eq 0 ]]; then
        # Default: process variant_1
        variant_folder="variant_1"
        if [[ -d "$variant_folder" ]]; then
            process_variant "$variant_folder"
        else
            print_status $RED "Error: Default variant folder 'variant_1' not found"
            print_status $YELLOW "Usage: $0 [variant_folder]"
            exit 1
        fi
    else
        # Process specified variant folder
        process_variant "$1"
    fi
    
    print_status $GREEN "Analysis completed successfully!"
}

# Change to the script directory
cd "$(dirname "$0")"

# Run main function with all arguments
main "$@"