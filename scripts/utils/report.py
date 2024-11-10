# utils/report.py
import os
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_relevant_file(file_path: Path) -> bool:
    """Check if file is relevant for documentation."""
    relevant_extensions = {'.py', '.yml', '.yaml', '.json', '.env'}
    exclude_patterns = {
        '__init__.py',
        'test_',
        'setup.py',
        'env_report',
        'docker_test.py',
        'code_documentation',
        '__pycache__',
        '.pyc',
        '.git'
    }
    
    if file_path.suffix not in relevant_extensions and file_path.name != '.env':
        return False
        
    if any(pattern in str(file_path) for pattern in exclude_patterns):
        return False
        
    return True

def get_relevant_files(root_dir: Path) -> List[Tuple[Path, str]]:
    """Get list of relevant files with their content."""
    relevant_files = []
    
    try:
        for path in root_dir.rglob('*'):
            if path.is_file() and is_relevant_file(path):
                try:
                    if path.stat().st_size > 1_000_000:
                        logger.warning(f"Skipping large file: {path}")
                        continue
                        
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    relative_path = path.relative_to(root_dir)
                    relevant_files.append((relative_path, content))
                except Exception as e:
                    logger.error(f"Error reading {path}: {e}")
    except Exception as e:
        logger.error(f"Error scanning directory: {e}")
                
    return sorted(relevant_files)

def generate_tree(path: Path, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
    """Generate a tree structure of the project directory including empty folders."""
    tree = ""
    if is_root:
        tree = path.name + "\n"
        
    indent = "    " if is_last else "│   "

    # Get all items and sort them
    items = sorted(path.glob('*'))
    dirs = [d for d in items if d.is_dir() and not d.name.startswith('.')]
    files = [f for f in items if f.is_file() and not f.name.startswith('.')]

    # Process all items
    all_items = dirs + files
    for i, item in enumerate(all_items):
        is_last_item = i == len(all_items) - 1
        connector = "└── " if is_last_item else "├── "
        
        tree += prefix + connector + item.name + "\n"
        
        if item.is_dir():
            next_prefix = prefix + ("    " if is_last_item else "│   ")
            tree += generate_tree(item, next_prefix, is_last_item, False)

    return tree

def generate_markdown(files: List[Tuple[Path, str]], output_file: Path, root_dir: Path) -> None:
    """Generate markdown documentation with file tree and contents."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# Project Code Documentation\n\n")
        f.write(f"Generated: {timestamp}\n\n")
        
        # File Tree
        f.write("## Project Structure\n\n")
        f.write("```\n")
        tree = generate_tree(root_dir)
        f.write(tree)
        f.write("```\n\n")
        
        # File Contents
        f.write("## File Contents\n\n")
        for file_path, content in files:
            f.write(f"### {file_path}\n\n")
            
            extension = file_path.suffix[1:] if file_path.suffix else 'env'
            lang_map = {
                'py': 'python',
                'yml': 'yaml',
                'yaml': 'yaml',
                'json': 'json',
                'env': 'ini'
            }
            lang = lang_map.get(extension, 'text')
            
            f.write(f"```{lang}\n{content}\n```\n\n")

def main():
    try:
        # Get project root (parent of script directory)
        script_dir = Path(__file__).resolve()
        root_dir = script_dir.parents[2]  # Adjust based on script location
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = root_dir / f'code_documentation_{timestamp}.md'
        
        logger.info("Scanning project files...")
        relevant_files = get_relevant_files(root_dir)
        
        logger.info("Generating documentation...")
        generate_markdown(relevant_files, output_file, root_dir)
        
        logger.info(f"Documentation generated: {output_file}")
        
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        raise

if __name__ == "__main__":
    main()