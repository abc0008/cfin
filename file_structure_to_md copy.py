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
# Configure root folder and specific files to process
ROOT_FOLDER = "/Users/alexc/Documents/AlexCoding/cfin"

# List of specific files to process
FILES_TO_PROCESS = [
    os.path.join(ROOT_FOLDER, "pdf_processing/claude_service.py"),
    os.path.join(ROOT_FOLDER, "nextjs-fdas/src/components/charts/ChartRenderer.tsx"),
    os.path.join(ROOT_FOLDER, "nextjs-fdas/src/components/visualization/Canvas.tsx"),
    os.path.join(ROOT_FOLDER, "nextjs-fdas/src/lib/api/analysis.ts"),
    # Add specific BarChart.tsx, LineChart.tsx files 
    os.path.join(ROOT_FOLDER, "nextjs-fdas/src/components/charts/BarChart.tsx"),
    os.path.join(ROOT_FOLDER, "nextjs-fdas/src/components/charts/LineChart.tsx"),
    os.path.join(ROOT_FOLDER, "nextjs-fdas/src/components/charts/PieChart.tsx"),
    os.path.join(ROOT_FOLDER, "services/analysis_service.py"),
    os.path.join(ROOT_FOLDER, "app/routes/analysis.py")
]

# Output file path (empty string means output to stdout)
OUTPUT_FILE = f"/Users/alexc/Documents/AlexCoding/cfin/file_changes_{datetime.now().strftime('%Y-%m-%d')}.md"

# Maximum file size in bytes (default: 10MB)
MAX_FILE_SIZE = 10485760

# Skip binary files
SKIP_BINARY_FILES = True

# Custom ignore patterns (in addition to defaults)
CUSTOM_IGNORE_PATTERNS = []

# Include all files (override ignore patterns)
INCLUDE_ALL_FILES = True
# ====================================
# END USER CONFIGURATION SECTION
# ====================================

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a markdown file structure with file contents wrapped in XML tags')
    parser.add_argument('files', nargs='*', help='Files to process (overrides in-script configuration)')
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

def find_specific_files(files_list):
    """Return a list of files in the format expected by the markdown generator"""
    items = []
    
    for filepath in files_list:
        if os.path.isfile(filepath):
            # Extract the relative path for display purposes
            base_path = Path(ROOT_FOLDER)
            try:
                rel_path = Path(filepath).relative_to(base_path)
                items.append((str(rel_path), False))  # False means it's a file
            except ValueError:
                # If file is not within the ROOT_FOLDER
                items.append((filepath, False))
    
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

def generate_markdown_with_xml(output_file, files, ignore_patterns, include_all, max_size, skip_binary, use_relative_paths):
    """Generate markdown output with file contents wrapped in XML tags"""
    # Combine default and custom ignore patterns
    all_ignore_patterns = get_default_ignore_patterns() + ignore_patterns
    
    # Prepare output
    lines = []
    lines.append("# Key Files from CFIN Project\n")
    lines.append("*Generated with file-structure-to-md script*\n")
    lines.append(f"## Root Path: {ROOT_FOLDER}\n\n")
    
    # Get list of files
    items = find_specific_files(files)
    
    # File contents section
    lines.append("## File Contents\n")
    
    for item_path, is_dir in items:
        if is_dir:
            continue  # Skip directories, only process files
        
        filepath = os.path.join(ROOT_FOLDER, item_path)
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
        lines.append(f"### {markdown_escape(item_path)}\n")
        lines.append(f"*Size: {size_str}*\n")
        
        # Determine path to use in XML tags
        if use_relative_paths:
            xml_path = item_path
        else:
            xml_path = filepath
        
        # Add language-specific code fence
        file_ext = os.path.splitext(filepath)[1].lower()
        lang = ""
        if file_ext == ".py":
            lang = "python"
        elif file_ext == ".tsx" or file_ext == ".ts":
            lang = "typescript"
        elif file_ext == ".js":
            lang = "javascript"
        
        # XML-wrapped content with language code fence
        lines.append(f"```{lang}\n")  # Start code block with language
        
        # Read and add file content with XML tags
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines.append(content)
        except Exception as e:
            lines.append(f"Error reading file: {str(e)}\n")
        
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
    if args.use_config or (not args.files and not any([
            args.output is not None,
            args.max_size is not None,
            args.no_binary,
            args.ignore, 
            args.all
        ])):
        # Use in-script configuration
        files = FILES_TO_PROCESS
        output_file = OUTPUT_FILE
        max_size = MAX_FILE_SIZE
        skip_binary = SKIP_BINARY_FILES
        ignore_patterns = CUSTOM_IGNORE_PATTERNS
        include_all = INCLUDE_ALL_FILES
        use_relative_paths = args.relative  # Still use this from args
    else:
        # Command-line arguments take precedence over in-script configuration
        files = args.files if args.files else FILES_TO_PROCESS
        output_file = args.output if args.output is not None else OUTPUT_FILE
        max_size = args.max_size if args.max_size is not None else MAX_FILE_SIZE
        skip_binary = args.no_binary if args.no_binary else SKIP_BINARY_FILES
        ignore_patterns = args.ignore if args.ignore else CUSTOM_IGNORE_PATTERNS
        include_all = args.all if args.all else INCLUDE_ALL_FILES
        use_relative_paths = args.relative
    
    # Ensure we have files to process
    if not files:
        print("Error: No files specified. Either provide files as arguments or configure FILES_TO_PROCESS in the script.")
        sys.exit(1)
    
    generate_markdown_with_xml(output_file, files, ignore_patterns, include_all, max_size, skip_binary, use_relative_paths)

if __name__ == "__main__":
    main()