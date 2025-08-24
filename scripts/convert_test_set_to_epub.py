#!/usr/bin/env python3
"""
Script to convert all text files in the test_set directory to EPUB format.
Uses the existing txt_to_epub_converter module.
"""

import os
import sys
from pathlib import Path

# Add the ai_workflow src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "ai_workflow" / "src"))

from preprocessors.epub.txt_to_epub_converter import convert_txt_to_epub


def main():
    # Define paths
    test_set_dir = Path("ai_workflow/resources/texts/test_set")
    output_dir = test_set_dir / "epub_conversions"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    print(f"Converting text files from: {test_set_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Find all .txt files in the test_set directory
    txt_files = list(test_set_dir.glob("*.txt"))
    
    if not txt_files:
        print("No .txt files found in the test_set directory.")
        return
    
    print(f"Found {len(txt_files)} text files to convert:")
    for txt_file in txt_files:
        print(f"  - {txt_file.name}")
    
    print("\nStarting conversion...")
    
    # Convert each text file to EPUB
    successful_conversions = 0
    failed_conversions = 0
    
    for txt_file in txt_files:
        try:
            print(f"\nConverting: {txt_file.name}")
            
            # Extract title from filename (remove .txt extension and any _reshaped suffix)
            title = txt_file.stem
            if title.endswith("_reshaped"):
                title = title[:-9]  # Remove "_reshaped" suffix
            
            # Convert to EPUB
            epub_path = convert_txt_to_epub(
                str(txt_file),
                title=title,
                author="Unknown",
                language="ar",  # Arabic language
                output_dir=str(output_dir)
            )
            
            print(f"  ✓ Successfully converted to: {os.path.basename(epub_path)}")
            successful_conversions += 1
            
        except Exception as e:
            print(f"  ✗ Failed to convert {txt_file.name}: {str(e)}")
            failed_conversions += 1
    
    print("\n" + "=" * 50)
    print(f"Conversion complete!")
    print(f"Successful: {successful_conversions}")
    print(f"Failed: {failed_conversions}")
    print(f"Total: {len(txt_files)}")
    
    if successful_conversions > 0:
        print(f"\nEPUB files saved to: {output_dir}")


if __name__ == "__main__":
    main()
