#!/usr/bin/env python3
"""
Script to generate Docker compose.yaml files for each task based on their dependencies.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


def generate_compose_yaml(task_name: str, task_info: Dict[str, Any]) -> str:
    """Generate a Docker compose.yaml content for a specific task."""
    
    # Base compose structure
    compose_content = [
        "services:",
        "  default:",
        '    image: "aisiuk/inspect-tool-support"'
    ]
    
    # Build the command
    command_parts = ["sh -c \""]
    
    # Update apt
    if task_info['apt_packages'] or task_info['python_packages']:
        command_parts.append("apt-get update && ")
    
    # Install APT packages
    if task_info['apt_packages']:
        apt_install = "apt-get install -y " + " ".join(task_info['apt_packages']) + " && "
        command_parts.append(apt_install)
    
    # Install Python packages
    if task_info['python_packages']:
        pip_packages = []
        for package in task_info['python_packages']:
            # Handle special cases
            if package == 'pyTMHMM':
                # pyTMHMM might need special handling
                pip_packages.append('pyTMHMM')
            elif package == 'analyze_rmsf':
                # This might be a local module, skip for now
                continue
            else:
                pip_packages.append(package)
        
        if pip_packages:
            pip_install = "pip install " + " ".join(pip_packages) + " && "
            command_parts.append(pip_install)
    
    # Add success message and keep container running
    success_msg = f"echo '{task_name} environment ready' && "
    command_parts.append(success_msg)
    
    # Show installed package versions for verification
    if 'mafft' in task_info['apt_packages']:
        command_parts.append("mafft --version && ")
    if 'fpocket' in task_info['apt_packages']:
        command_parts.append("fpocket -v && ")
    if 'dssp' in task_info['apt_packages']:
        command_parts.append("mkdssp --version && ")
    
    # Keep container running
    command_parts.append("tail -f /dev/null\"")
    
    # Join the command
    full_command = "".join(command_parts)
    
    # Format the command with proper YAML indentation
    compose_content.extend([
        "    command: >",
        "        " + full_command
    ])
    
    # Add other Docker settings
    compose_content.extend([
        "    init: true",
        "    network_mode: bridge  # Enables internet access",
        "    dns:",
        "      - 8.8.8.8        # Google DNS", 
        "      - 1.1.1.1        # Cloudflare DNS",
        "    dns_opt:",
        "      - ndots:2",
        "      - edns0",
        "    stop_grace_period: 1s"
    ])
    
    # Add volumes
    if task_info['mount_volumes']:
        compose_content.append("    volumes:")
        for volume in task_info['mount_volumes']:
            compose_content.append(f"    - {volume}")
    
    return "\n".join(compose_content)


def create_task_compose_files(dependencies_file: str, output_dir: str = "compose_files"):
    """Create compose.yaml files for each task."""
    
    # Load dependencies
    with open(dependencies_file, 'r') as f:
        dependencies = json.load(f)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate compose files
    created_files = []
    
    for task_name, task_info in dependencies.items():
        print(f"Generating compose.yaml for {task_name}...")
        
        # Generate compose content
        compose_content = generate_compose_yaml(task_name, task_info)
        
        # Save to file
        compose_file = output_path / f"{task_name}_compose.yaml"
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        created_files.append(compose_file)
        
        # Show summary
        packages_summary = []
        if task_info['python_packages']:
            packages_summary.append(f"Python: {', '.join(task_info['python_packages'])}")
        if task_info['apt_packages']:
            packages_summary.append(f"APT: {', '.join(task_info['apt_packages'])}")
        
        if packages_summary:
            print(f"  Dependencies: {' | '.join(packages_summary)}")
        else:
            print(f"  Dependencies: None")
        
        print(f"  Volumes: {len(task_info['mount_volumes'])}")
    
    print(f"\n✅ Generated {len(created_files)} compose files in {output_path}")
    return created_files


def create_unified_compose_file(dependencies_file: str, output_file: str = "all_tasks_compose.yaml"):
    """Create a single compose file with all tasks as separate services."""
    
    with open(dependencies_file, 'r') as f:
        dependencies = json.load(f)
    
    compose_content = ["services:"]
    
    for task_name, task_info in dependencies.items():
        print(f"Adding service for {task_name}...")
        
        # Service name (replace special chars)
        service_name = task_name.lower().replace('_', '-').replace(' ', '-')
        
        compose_content.extend([
            f"  {service_name}:",
            '    image: "aisiuk/inspect-tool-support"'
        ])
        
        # Build command similar to single file generation
        command_parts = ["sh -c \""]
        
        if task_info['apt_packages'] or task_info['python_packages']:
            command_parts.append("apt-get update && ")
        
        if task_info['apt_packages']:
            apt_install = "apt-get install -y " + " ".join(task_info['apt_packages']) + " && "
            command_parts.append(apt_install)
        
        if task_info['python_packages']:
            pip_packages = [pkg for pkg in task_info['python_packages'] if pkg not in ['analyze_rmsf']]
            if pip_packages:
                pip_install = "pip install " + " ".join(pip_packages) + " && "
                command_parts.append(pip_install)
        
        command_parts.append(f"echo '{task_name} ready' && tail -f /dev/null\"")
        
        full_command = "".join(command_parts)
        
        compose_content.extend([
            "    command: >",
            "        " + full_command,
            "    init: true",
            "    network_mode: bridge",
            "    dns:",
            "      - 8.8.8.8",
            "      - 1.1.1.1",
            "    dns_opt:",
            "      - ndots:2",
            "      - edns0",
            "    stop_grace_period: 1s"
        ])
        
        if task_info['mount_volumes']:
            compose_content.append("    volumes:")
            for volume in task_info['mount_volumes']:
                compose_content.append(f"      - {volume}")
        
        compose_content.append("")  # Empty line between services
    
    # Write unified compose file
    with open(output_file, 'w') as f:
        f.write("\n".join(compose_content))
    
    print(f"✅ Generated unified compose file: {output_file}")


def main():
    """Main function to generate compose files."""
    script_dir = Path(__file__).parent
    dependencies_file = script_dir / 'task_dependencies.json'
    
    if not dependencies_file.exists():
        print(f"Dependencies file not found: {dependencies_file}")
        print("Please run analyze_task_dependencies.py first.")
        return
    
    print("Generating Docker compose files for all tasks...")
    print("=" * 60)
    
    # Create individual compose files
    created_files = create_task_compose_files(str(dependencies_file))
    
    print("\n" + "=" * 60)
    
    # Create unified compose file
    create_unified_compose_file(str(dependencies_file))
    
    print(f"\nFiles created:")
    print(f"- Individual task compose files: {len(created_files)} files in compose_files/")
    print(f"- Unified compose file: all_tasks_compose.yaml")
    
    # Show usage example
    print(f"\nUsage examples:")
    print(f"1. Run a specific task:")
    print(f"   docker compose -f compose_files/E1_PDB_Cysteine_Count_compose.yaml up")
    print(f"2. Run all tasks:")
    print(f"   docker compose -f all_tasks_compose.yaml up")


if __name__ == '__main__':
    main()