#!/usr/bin/env python3
"""
Script to fix hardcoded paths in Python files for Docker environment
"""
import os
import re
import glob

def fix_paths_in_file(filepath):
    """Fix hardcoded paths in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace hardcoded local paths with Docker paths
        old_pattern = r'/app'
        new_pattern = '/app'
        
        updated_content = content.replace(old_pattern, new_pattern)
        
        if updated_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"⏭️  No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    # Find all Python files in the project
    python_files = glob.glob("**/*.py", recursive=True)
    
    print(f"Found {len(python_files)} Python files")
    print("Fixing hardcoded paths...\n")
    
    fixed_count = 0
    for py_file in python_files:
        if fix_paths_in_file(py_file):
            fixed_count += 1
    
    print(f"\n🎉 Fixed {fixed_count} files!")

if __name__ == "__main__":
    main()