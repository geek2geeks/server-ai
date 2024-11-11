# scripts/utils/report.py
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
        '.git',
        'report.py'  # Exclude self from documentation
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

def get_all_paths(root_dir: Path) -> List[str]:
    """Get all relative paths including empty directories."""
    paths = []
    
    try:
        # Get all items including empty directories
        for path in root_dir.rglob('*'):
            # Skip report.py and its parent directories
            if 'report.py' in str(path):
                continue
                
            if path.is_file() or (path.is_dir() and not any(path.iterdir())):
                relative = path.relative_to(root_dir)
                paths.append(str(relative))
    except Exception as e:
        logger.error(f"Error getting paths: {e}")
        
    return sorted(paths)

def generate_markdown(files: List[Tuple[Path, str]], output_file: Path, root_dir: Path) -> None:
    """Generate markdown documentation with paths and contents."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# Project Code Documentation\n\n")
        f.write(f"Generated: {timestamp}\n\n")
        
        # Project Structure
        f.write("## Project Structure\n\n")
        f.write("Relative paths from project root:\n\n")
        f.write("```text\n")
        for path in get_all_paths(root_dir):
            f.write(f"{path}\n")
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