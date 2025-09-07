#!/usr/bin/env python3
"""
Script to analyze all tasks and extract their dependencies for Docker compose files.
Analyzes Python imports, system commands, and file requirements.
"""

import os
import re
import json
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


def extract_python_imports(file_path: str) -> Set[str]:
    """Extract Python package imports from a Python file."""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to find imports
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get the top-level package
                        package = alias.name.split('.')[0]
                        imports.add(package)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package = node.module.split('.')[0]
                        imports.add(package)
        except SyntaxError:
            # Fallback to regex parsing if AST fails
            import_patterns = [
                r'^from\s+(\w+)',
                r'^import\s+(\w+)'
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.update(matches)
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return imports


def extract_system_commands(file_path: str) -> Set[str]:
    """Extract system commands called from subprocess or shell."""
    commands = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for subprocess calls
        subprocess_patterns = [
            r"subprocess\.run\(\s*\['([^']+)'",
            r"subprocess\.call\(\s*\['([^']+)'",
            r"subprocess\.Popen\(\s*\['([^']+)'",
            r"os\.system\(['\"]([^'\"]+)['\"]",
            r"os\.popen\(['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in subprocess_patterns:
            matches = re.findall(pattern, content)
            commands.update(matches)
            
        # Look for shell command strings
        shell_patterns = [
            r"['\"](mafft|fpocket|mkdssp|blast|clustalw|muscle|dssp)[^'\"]*['\"]",
        ]
        
        for pattern in shell_patterns:
            matches = re.findall(pattern, content)
            commands.update(matches)
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return commands


def extract_file_dependencies(task_folder: Path) -> Dict[str, List[str]]:
    """Extract file dependencies for a task."""
    dependencies = {
        'input_files': [],
        'data_files': []
    }
    
    # Check what files are in variant folders
    variant_files = set()
    for variant_dir in task_folder.glob('variant_*'):
        if variant_dir.is_dir():
            for file_path in variant_dir.glob('*'):
                if file_path.is_file():
                    variant_files.add(file_path.suffix.lower())
    
    # Check for other data dependencies
    data_patterns = ['*.pdb', '*.fasta', '*.json', '*.csv', '*.txt', '*.dat']
    for pattern in data_patterns:
        if list(task_folder.glob(pattern)):
            dependencies['data_files'].append(pattern)
    
    # Map file extensions to likely external data needs
    if '.pdb' in variant_files:
        dependencies['input_files'].append('../pdb_files/*.pdb')
    if '.fasta' in variant_files:
        dependencies['input_files'].append('../uniprot_files/*.fasta')
    if '.json' in variant_files and 'UniProt' in task_folder.name:
        dependencies['input_files'].append('../uniprot_files/*.json')
    
    return dependencies


def map_imports_to_packages(imports: Set[str]) -> List[str]:
    """Map Python imports to pip package names."""
    # Common import -> package mappings
    package_mapping = {
        'Bio': 'biopython',
        'scipy': 'scipy',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'sklearn': 'scikit-learn',
        'requests': 'requests',
        'beautifulsoup4': 'beautifulsoup4',
        'bs4': 'beautifulsoup4',
        'lxml': 'lxml',
        'xml': 'lxml',
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'torch': 'torch',
        'tensorflow': 'tensorflow',
        'keras': 'keras'
    }
    
    packages = []
    for imp in imports:
        if imp in package_mapping:
            packages.append(package_mapping[imp])
        elif imp not in ['os', 'sys', 'subprocess', 'json', 'csv', 'math', 
                        'random', 're', 'time', 'datetime', 'pathlib', 
                        'collections', 'itertools', 'functools', 'typing',
                        'tempfile', 'glob', 'shutil', 'urllib', 'http']:
            # Assume non-standard library imports need to be installed
            packages.append(imp)
    
    return sorted(list(set(packages)))


def map_commands_to_packages(commands: Set[str]) -> List[str]:
    """Map system commands to apt packages."""
    command_mapping = {
        'mafft': 'mafft',
        'fpocket': 'fpocket',
        'mkdssp': 'dssp',
        'dssp': 'dssp',
        'blast': 'blast2',
        'blastp': 'blast2',
        'blastn': 'blast2',
        'blastx': 'blast2',
        'clustalw': 'clustalw',
        'muscle': 'muscle'
    }
    
    packages = []
    for cmd in commands:
        if cmd in command_mapping:
            packages.append(command_mapping[cmd])
    
    return sorted(list(set(packages)))


def analyze_task(task_folder: Path) -> Dict[str, Any]:
    """Analyze a single task folder for all dependencies."""
    result = {
        'task_name': task_folder.name,
        'python_imports': set(),
        'system_commands': set(),
        'file_dependencies': {},
        'python_packages': [],
        'apt_packages': [],
        'mount_volumes': []
    }
    
    # Analyze Python files
    for py_file in task_folder.glob('*.py'):
        imports = extract_python_imports(str(py_file))
        commands = extract_system_commands(str(py_file))
        result['python_imports'].update(imports)
        result['system_commands'].update(commands)
    
    # Analyze shell scripts
    for sh_file in task_folder.glob('*.sh'):
        commands = extract_system_commands(str(sh_file))
        result['system_commands'].update(commands)
    
    # Extract file dependencies
    result['file_dependencies'] = extract_file_dependencies(task_folder)
    
    # Convert to package lists
    result['python_packages'] = map_imports_to_packages(result['python_imports'])
    result['apt_packages'] = map_commands_to_packages(result['system_commands'])
    
    # Convert sets to lists for JSON serialization
    result['python_imports'] = sorted(list(result['python_imports']))
    result['system_commands'] = sorted(list(result['system_commands']))
    
    # Create mount volumes
    volumes = []
    
    # Mount the task folder itself
    volumes.append(f"./data/{task_folder.name}:/app/task")
    
    # Mount external data files
    for file_pattern in result['file_dependencies']['input_files']:
        if 'pdb_files' in file_pattern:
            volumes.append("./data/pdb_files:/app/data/pdb_files")
        elif 'uniprot_files' in file_pattern:
            volumes.append("./data/uniprot_files:/app/data/uniprot_files")
        elif 'blast_files' in file_pattern:
            volumes.append("./data/blast_files:/app/data/blast_files")
    
    # Remove duplicates
    result['mount_volumes'] = sorted(list(set(volumes)))
    
    return result


def main():
    """Main function to analyze all tasks."""
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data'
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return
    
    # Find all task folders
    task_folders = []
    pattern = re.compile(r'^[EMH]\d+_')
    
    for item in data_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            task_folders.append(item)
    
    task_folders = sorted(task_folders)
    print(f"Found {len(task_folders)} task folders")
    
    # Analyze each task
    all_results = {}
    
    for task_folder in task_folders:
        print(f"Analyzing {task_folder.name}...")
        result = analyze_task(task_folder)
        all_results[task_folder.name] = result
    
    # Save results to JSON
    output_file = script_dir / 'task_dependencies.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete. Results saved to {output_file}")
    
    # Print summary
    all_python_packages = set()
    all_apt_packages = set()
    
    for task_data in all_results.values():
        all_python_packages.update(task_data['python_packages'])
        all_apt_packages.update(task_data['apt_packages'])
    
    print(f"\nSummary:")
    print(f"Total unique Python packages: {len(all_python_packages)}")
    print(f"Python packages: {sorted(all_python_packages)}")
    print(f"Total unique APT packages: {len(all_apt_packages)}")
    print(f"APT packages: {sorted(all_apt_packages)}")


if __name__ == '__main__':
    main()