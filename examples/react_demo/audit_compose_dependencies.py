#!/usr/bin/env python3
"""
Audit script to verify that all dependencies from task_dependencies.json
are properly installed in the compose files
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Set, List
from collections import defaultdict

def load_task_dependencies():
    """Load task dependencies from JSON file."""
    deps_file = Path(__file__).parent / 'task_dependencies.json'
    with open(deps_file, 'r') as f:
        return json.load(f)

def load_compose_file():
    """Load the unified compose file."""
    compose_file = Path(__file__).parent / 'all_tasks_compose.yaml'
    with open(compose_file, 'r') as f:
        return yaml.safe_load(f)

def extract_service_dependencies(service_config):
    """Extract dependencies from a compose service configuration."""
    command = service_config.get('command', '')
    
    # Extract pip packages
    pip_packages = []
    pip_matches = re.findall(r'pip install ([^&]+)', command)
    for match in pip_matches:
        packages = match.strip().split()
        pip_packages.extend(packages)
    
    # Extract apt packages
    apt_packages = []
    apt_matches = re.findall(r'apt-get install -y ([^&]+)', command)
    for match in apt_matches:
        packages = match.strip().split()
        apt_packages.extend(packages)
    
    return pip_packages, apt_packages

def normalize_task_name(task_name):
    """Convert task name to compose service name format."""
    return task_name.lower().replace('_', '-')

def audit_dependencies():
    """Audit dependencies between task requirements and compose installations."""
    print("=" * 80)
    print("DEPENDENCY AUDIT REPORT")
    print("=" * 80)
    
    # Load data
    task_deps = load_task_dependencies()
    compose_data = load_compose_file()
    
    # Track issues
    missing_services = []
    missing_python_packages = []
    missing_apt_packages = []
    extra_packages = defaultdict(list)
    
    print(f"\nAnalyzing {len(task_deps)} tasks...")
    
    for task_name, deps in task_deps.items():
        service_name = normalize_task_name(task_name)
        
        # Check if service exists in compose file
        if service_name not in compose_data['services']:
            missing_services.append(task_name)
            continue
        
        service_config = compose_data['services'][service_name]
        installed_pip, installed_apt = extract_service_dependencies(service_config)
        
        # Required packages
        required_python = set(deps.get('python_packages', []))
        required_apt = set(deps.get('apt_packages', []))
        
        # Installed packages
        installed_python_set = set(installed_pip)
        installed_apt_set = set(installed_apt)
        
        # Check for missing packages
        missing_py = required_python - installed_python_set
        missing_ap = required_apt - installed_apt_set
        
        if missing_py:
            missing_python_packages.append({
                'task': task_name,
                'missing': list(missing_py),
                'required': list(required_python),
                'installed': list(installed_python_set)
            })
        
        if missing_ap:
            missing_apt_packages.append({
                'task': task_name,
                'missing': list(missing_ap),
                'required': list(required_apt),
                'installed': list(installed_apt_set)
            })
        
        # Check for extra packages (not necessarily bad, but worth noting)
        extra_py = installed_python_set - required_python
        extra_ap = installed_apt_set - required_apt
        
        if extra_py or extra_ap:
            extra_packages[task_name] = {
                'python': list(extra_py),
                'apt': list(extra_ap)
            }
    
    # Report results
    print("\n" + "="*50)
    print("AUDIT RESULTS")
    print("="*50)
    
    if missing_services:
        print(f"\n❌ MISSING SERVICES ({len(missing_services)}):")
        for service in missing_services:
            print(f"   • {service}")
    else:
        print(f"\n✅ All {len(task_deps)} tasks have corresponding services")
    
    if missing_python_packages:
        print(f"\n❌ MISSING PYTHON PACKAGES ({len(missing_python_packages)}):")
        for item in missing_python_packages:
            print(f"   • {item['task']}:")
            print(f"     Missing: {item['missing']}")
            print(f"     Required: {item['required']}")
            print(f"     Installed: {item['installed']}")
    else:
        print(f"\n✅ All required Python packages are installed")
    
    if missing_apt_packages:
        print(f"\n❌ MISSING APT PACKAGES ({len(missing_apt_packages)}):")
        for item in missing_apt_packages:
            print(f"   • {item['task']}:")
            print(f"     Missing: {item['missing']}")
            print(f"     Required: {item['required']}")
            print(f"     Installed: {item['installed']}")
    else:
        print(f"\n✅ All required APT packages are installed")
    
    # Show summary statistics
    total_python_deps = sum(len(deps.get('python_packages', [])) for deps in task_deps.values())
    total_apt_deps = sum(len(deps.get('apt_packages', [])) for deps in task_deps.values())
    
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   Total tasks: {len(task_deps)}")
    print(f"   Total Python package requirements: {total_python_deps}")
    print(f"   Total APT package requirements: {total_apt_deps}")
    print(f"   Services missing: {len(missing_services)}")
    print(f"   Python packages missing: {sum(len(item['missing']) for item in missing_python_packages)}")
    print(f"   APT packages missing: {sum(len(item['missing']) for item in missing_apt_packages)}")
    
    # Generate fixes if needed
    if missing_python_packages or missing_apt_packages or missing_services:
        print(f"\n🔧 SUGGESTED FIXES:")
        
        for item in missing_python_packages:
            service_name = normalize_task_name(item['task'])
            print(f"\n   Fix for {item['task']}:")
            print(f"   Add to service '{service_name}' command:")
            print(f"   pip install {' '.join(item['missing'])}")
        
        for item in missing_apt_packages:
            service_name = normalize_task_name(item['task'])
            print(f"\n   Fix for {item['task']}:")
            print(f"   Add to service '{service_name}' command:")
            print(f"   apt-get install -y {' '.join(item['missing'])}")
    
    print("\n" + "="*80)
    
    return len(missing_services) + len(missing_python_packages) + len(missing_apt_packages) == 0

if __name__ == "__main__":
    try:
        success = audit_dependencies()
        if success:
            print("🎉 All dependencies are properly configured!")
        else:
            print("⚠️  Issues found that need to be addressed.")
    except Exception as e:
        print(f"❌ Error during audit: {e}")