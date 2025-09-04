# ReAct Agent Demo - PDB File Download

This demo showcases a ReAct agent that downloads and analyzes protein structure files from the Protein Data Bank (PDB).

## Overview

The demo features:
- ReAct agent with bash, python, and file I/O tools
- Docker container with internet access
- Automated download and analysis of PDB file 1BAG
- Step-by-step reasoning and action execution

## Usage

### Basic Usage
```bash
inspect eval react_demo.py --model gpt-4
```

### With Custom Model
```bash
inspect eval react_demo.py --model claude-3-sonnet-20240229
```

### View Results
```bash
inspect view
```

## What the Agent Does

1. **Downloads** the 1BAG.pdb file from RCSB PDB database
2. **Verifies** the download was successful
3. **Analyzes** the protein structure using available tools
4. **Reports** findings about the protein characteristics

## Docker Configuration

The demo runs in a Docker sandbox with:
- Internet access enabled via `network_mode: bridge`
- DNS resolution using Google (8.8.8.8) and Cloudflare (1.1.1.1) DNS
- Python environment for data analysis
- Standard Unix tools (curl, wget, etc.)

The `compose.yaml` file configures:
- Network bridge mode for internet connectivity
- Custom DNS servers to resolve DNS issues
- Proper DNS options for reliable resolution

## Expected Output

The agent should successfully:
- Download the 1BAG.pdb file (≈4KB)
- Parse basic structural information
- Provide insights about the protein structure

## File Structure

- `react_demo.py` - Main demo implementation
- `compose.yaml` - Docker configuration with internet access
- `README.md` - This documentation file

## Troubleshooting

### DNS Issues
If you encounter DNS resolution problems:
1. The `compose.yaml` includes Google (8.8.8.8) and Cloudflare (1.1.1.1) DNS servers
2. Ensure `network_mode: bridge` is set for internet access
3. Try alternative DNS servers if needed (e.g., 8.8.4.4, 1.0.0.1)