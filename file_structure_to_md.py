#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import fnmatch
import re
from pathlib import Path
from datetime import datetime

# ====================================
# USER CONFIGURATION SECTION
# Configure root folder and subfolders to process
ROOT_FOLDER = "/Users/alexc/Documents/AlexCoding/cfin"
FOLDERS_TO_PROCESS = [
    # Add your folders here, for example:
    # "/path/to/project1",
    # "/path/to/project2",
    # "./relative/path/to/project3",
    os.path.join(ROOT_FOLDER, "nextjs-fdas"),
    os.path.join(ROOT_FOLDER, "backend")
]
# ====================================
# Configure which folders to process here
FOLDERS_TO_PROCESS = [
    # Add your folders here, for example:
    # "/path/to/project1",
    # "/path/to/project2",
    # "./relative/path/to/project3",
    "/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas",
    "/Users/alexc/Documents/AlexCoding/cfin/backend"
]

# Output file path (empty string means output to stdout)
OUTPUT_FILE = f"/Users/alexc/Documents/AlexCoding/cfin/frontend_new_vs_old_{datetime.now().strftime('%Y-%m-%d')}.md"  # e.g., "output.md"

# Maximum file size in bytes (default: 10MB)
MAX_FILE_SIZE = 10485760

# Skip binary files
SKIP_BINARY_FILES = True

# Custom ignore patterns (in addition to defaults)
CUSTOM_IGNORE_PATTERNS = [
    ".pytest_cache/",
    "htmlcov/",
    "logs/",
    "samples/",
    "test_data/",
    "tests/",
    "uploads/",
    "venv/",
    "test*",
    "*tests*"
]

# Include all files (override ignore patterns)
INCLUDE_ALL_FILES = False
# ====================================
# END USER CONFIGURATION SECTION
# ====================================

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a markdown file structure with file contents wrapped in XML tags')
    parser.add_argument('directories', nargs='*', help='Directories to process (overrides in-script configuration)')
    parser.add_argument('-o', '--output', help='Write output to FILE instead of stdout')
    parser.add_argument('-m', '--max-size', type=int, help='Skip files larger than SIZE bytes')
    parser.add_argument('-b', '--no-binary', action='store_true', help='Skip binary files')
    parser.add_argument('-i', '--ignore', action='append', help='Add custom ignore pattern (can be used multiple times)', default=[])
    parser.add_argument('-a', '--all', action='store_true', help='Include files/dirs that would normally be ignored')
    parser.add_argument('-c', '--use-config', action='store_true', help='Use only in-script configuration (ignore command line args)')
    parser.add_argument('-r', '--relative', action='store_true', help='Use relative paths in XML tags instead of full paths')
    return parser.parse_args()

def get_default_ignore_patterns():
    return [
        "node_modules/",
        ".next/",
        ".nuxt/",
        "dist/",
        ".cache/",
        ".git/",
        ".github/",
        ".vscode/",
        ".idea/",
        ".DS_Store",
        "*.env*",
        ".env",
        ".env.local",
        ".env.development",
        ".env.test",
        ".env.production",
        "build/",
        "coverage/",
        "*.log",
        "yarn.lock",
        "package-lock.json",
        "pnpm-lock.yaml"
    ]

def should_ignore(path, ignore_patterns, include_all):
    """Check if path should be ignored based on patterns"""
    if include_all:
        return False
    
    path_str = str(path)
    for pattern in ignore_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            dir_pattern = pattern[:-1]
            if path_str == dir_pattern or path_str.startswith(f"{dir_pattern}/"):
                return True
                
        # Handle wildcard patterns
        elif '*' in pattern:
            if fnmatch.fnmatch(path_str, pattern):
                return True
                
        # Handle exact matches
        elif path_str == pattern:
            return True
            
    return False

def is_binary_file(filepath):
    """Check if file is binary using file command"""
    try:
        result = subprocess.run(['file', '--mime-type', '-b', filepath], 
                               capture_output=True, text=True, check=True)
        mime_type = result.stdout.strip()
        return not (mime_type.startswith('text/') or 
                   mime_type in ['application/json', 'application/xml', 'application/javascript'])
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fallback method: try to read as text
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read(1024)
                return False
        except UnicodeDecodeError:
            return True
    return False

def should_exclude(filepath, ignore_patterns, include_all, max_size, skip_binary):
    """Check if file should be excluded due to pattern, size or type"""
    # Check if path should be ignored first
    if should_ignore(filepath, ignore_patterns, include_all):
        return True
    
    # Check file size
    try:
        if os.path.getsize(filepath) > max_size:
            return True
    except (OSError, FileNotFoundError):
        return True
    
    # Check if binary file
    if skip_binary and is_binary_file(filepath):
        return True
    
    return False

def find_items(base_dir, ignore_patterns, include_all):
    """Find files and directories respecting ignore patterns"""
    items = []
    base_path = Path(base_dir)
    
    for root, dirs, files in os.walk(base_path, topdown=True):
        rel_root = Path(root).relative_to(base_path)
        rel_root_str = str(rel_root) if rel_root != Path('.') else ''
        
        # Filter directories to avoid descending into ignored ones
        dirs[:] = [d for d in dirs if not should_ignore(
            os.path.join(rel_root_str, d) if rel_root_str else d,
            ignore_patterns, include_all
        )]
        
        # Add directories to items
        for d in dirs:
            rel_path = os.path.join(rel_root_str, d) if rel_root_str else d
            items.append((rel_path, True))  # True means it's a directory
        
        # Add files to items
        for f in files:
            rel_path = os.path.join(rel_root_str, f) if rel_root_str else f
            items.append((rel_path, False))  # False means it's a file
    
    # Sort items
    return sorted(items)

def markdown_escape(text):
    """Escape special markdown characters"""
    # Replace characters that have special meaning in markdown
    escapes = [
        ('\\', '\\\\'),  # Backslash needs to be first
        ('`', '\\`'),
        ('*', '\\*'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('[', '\\['),
        (']', '\\]'),
        ('(', '\\('),
        (')', '\\)'),
        ('#', '\\#'),
        ('+', '\\+'),
        ('-', '\\-'),
        ('.', '\\.'),
        ('!', '\\!'),
        ('|', '\\|')
    ]
    
    for char, escape in escapes:
        text = text.replace(char, escape)
    
    return text

def xml_escape(text):
    """Escape special XML characters"""
    escapes = [
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&apos;')
    ]
    
    for char, escape in escapes:
        text = text.replace(char, escape)
    
    return text

def generate_markdown_with_xml(output_file, directories, ignore_patterns, include_all, max_size, skip_binary, use_relative_paths):
    """Generate markdown output with file contents wrapped in XML tags"""
    # Combine default and custom ignore patterns
    all_ignore_patterns = get_default_ignore_patterns() + ignore_patterns
    
    # Prepare output
    lines = []
    lines.append("# Project File Structure\n")
    lines.append("*Generated with file-structure-to-md script*\n")
    lines.append(f"## Root Path: /Users/alexc/Documents/AlexCoding/cfin\n\n")
    
    # Process each directory
    for dir_path in directories:
        if not os.path.isdir(dir_path):
            lines.append(f"## Error: Directory not found: {markdown_escape(dir_path)}\n")
            continue
        
        # Get absolute path for the directory
        abs_dir_path = os.path.abspath(dir_path)
        dir_name = os.path.basename(abs_dir_path)
        
        lines.append(f"## Directory: {markdown_escape(dir_name)}\n")
        lines.append(f"**Path**: {markdown_escape(abs_dir_path)}\n")
        
        # File tree section
        lines.append("### File Tree\n")
        lines.append("```\n")  # Start code block for directory tree
        
        items = find_items(dir_path, all_ignore_patterns, include_all)
        for item_path, is_dir in items:
            indent = "  " * (item_path.count(os.sep))
            if is_dir:
                lines.append(f"{indent}📁 {os.path.basename(item_path)}/\n")
            else:
                filepath = os.path.join(dir_path, item_path)
                if should_exclude(filepath, all_ignore_patterns, include_all, max_size, skip_binary):
                    lines.append(f"{indent}⚠️ {os.path.basename(item_path)} [excluded]\n")
                else:
                    lines.append(f"{indent}📄 {os.path.basename(item_path)}\n")
        
        lines.append("```\n")  # End code block
        
        # File contents section
        lines.append("### File Contents\n")
        
        for item_path, is_dir in items:
            if is_dir:
                continue  # Skip directories, only process files
            
            filepath = os.path.join(dir_path, item_path)
            if should_exclude(filepath, all_ignore_patterns, include_all, max_size, skip_binary):
                continue
            
            # Get file size
            try:
                size = os.path.getsize(filepath)
                size_str = f"{size} bytes"
                if size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
            except (OSError, FileNotFoundError):
                size_str = "unknown size"
            
            # File header with path and metadata
            lines.append(f"#### {markdown_escape(item_path)}\n")
            lines.append(f"*Size: {size_str}*\n")
            
            # Determine path to use in XML tags
            if use_relative_paths:
                xml_path = item_path
            else:
                xml_path = os.path.join(abs_dir_path, item_path)
            
            # XML-wrapped content
            lines.append("```\n")  # Start code block without language for XML tags
            
            # Read and add file content with XML tags
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Add opening XML tag with file path
                    lines.append(f"<file path=\"{xml_escape(xml_path)}\">\n")
                    # Add file content
                    lines.append(content)
                    # Ensure file ends with newline before closing tag
                    if content and not content.endswith('\n'):
                        lines.append("\n")
                    # Add closing XML tag
                    lines.append("</file>\n")
            except Exception as e:
                lines.append(f"<file path=\"{xml_escape(xml_path)}\">\n")
                lines.append(f"Error reading file: {str(e)}\n")
                lines.append("</file>\n")
            
            # End code block
            lines.append("```\n\n")
    
    # Output the markdown content
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Output written to {output_file}")
    else:
        sys.stdout.writelines(lines)

def main():
    args = parse_arguments()
    
    # Determine if we should use command-line args or in-script configuration
    if args.use_config or (not args.directories and not any([
            args.output is not None,
            args.max_size is not None,
            args.no_binary,
            args.ignore, 
            args.all
        ])):
        # Use in-script configuration
        directories = FOLDERS_TO_PROCESS
        output_file = OUTPUT_FILE
        max_size = MAX_FILE_SIZE
        skip_binary = SKIP_BINARY_FILES
        ignore_patterns = CUSTOM_IGNORE_PATTERNS
        include_all = INCLUDE_ALL_FILES
        use_relative_paths = args.relative  # Still use this from args
    else:
        # Command-line arguments take precedence over in-script configuration
        directories = args.directories if args.directories else FOLDERS_TO_PROCESS
        output_file = args.output if args.output is not None else OUTPUT_FILE
        max_size = args.max_size if args.max_size is not None else MAX_FILE_SIZE
        skip_binary = args.no_binary if args.no_binary else SKIP_BINARY_FILES
        ignore_patterns = args.ignore if args.ignore else CUSTOM_IGNORE_PATTERNS
        include_all = args.all if args.all else INCLUDE_ALL_FILES
        use_relative_paths = args.relative
    
    # Ensure we have directories to process
    if not directories:
        print("Error: No directories specified. Either provide directories as arguments or configure FOLDERS_TO_PROCESS in the script.")
        sys.exit(1)
    
    generate_markdown_with_xml(output_file, directories, ignore_patterns, include_all, max_size, skip_binary, use_relative_paths)

if __name__ == "__main__":
    main()