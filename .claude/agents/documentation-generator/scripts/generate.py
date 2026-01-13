#!/usr/bin/env python3
"""
Documentation Generator - Generate docs from code
"""

import argparse
import re
from pathlib import Path


def extract_docstrings(file_path: Path):
    """Extract docstrings from Python file"""
    content = file_path.read_text()

    # Find class docstrings
    class_docs = re.findall(r'class (\w+).*?"""(.*?)"""', content, re.DOTALL)
    # Find function docstrings
    func_docs = re.findall(r'def (\w+)\(.*?\).*?"""(.*?)"""', content, re.DOTALL)

    return {
        'classes': dict(class_docs),
        'functions': dict(func_docs)
    }


def generate_readme(file_path: Path):
    """Generate README from code"""
    docs = extract_docstrings(file_path)

    readme = f"""# {file_path.stem} Documentation

Generated from source code.

## Classes

{chr(10).join(f"### {name}\n\n{doc}" for name, doc in docs['classes'].items())}

## Functions

{chr(10).join(f"### {name}()\n\n{doc}" for name, doc in docs['functions'].items())}
"""

    output_path = file_path.parent / f"{file_path.stem}_README.md"
    output_path.write_text(readme)
    print(f"✅ Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Documentation Generator')
    parser.add_argument('--target', help='File to document')
    parser.add_argument('--all', action='store_true', help='Document all watchers')

    args = parser.parse_args()

    print("📚 Documentation Generator\n")

    if args.target:
        generate_readme(Path(args.target))
    elif args.all:
        watchers = Path('watchers').glob('*_watcher.py')
        for watcher in watchers:
            generate_readme(watcher)


if __name__ == '__main__':
    main()
