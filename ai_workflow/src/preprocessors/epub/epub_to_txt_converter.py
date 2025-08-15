"""
EPUB to TXT converter for AI workflow preprocessing
"""

import os
import tempfile
from typing import Tuple
from ai_workflow.src.preprocessors.epub.epub_extractor import extract_text_from_file


def convert_epub_to_txt(epub_path: str, output_dir: str = None) -> str:
    """
    Convert an EPUB file to a TXT file.
    
    Args:
        epub_path: Path to the EPUB file
        output_dir: Directory to save the TXT file (defaults to temp directory)
        
    Returns:
        Path to the generated TXT file
        
    Raises:
        FileNotFoundError: If EPUB file doesn't exist
        ValueError: If conversion fails
    """
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
    
    # Extract text from EPUB
    try:
        text_content = extract_text_from_file(epub_path)
    except Exception as e:
        raise ValueError(f"Failed to extract text from EPUB: {str(e)}")
    
    # Determine output path
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    # Generate output filename
    epub_name = os.path.splitext(os.path.basename(epub_path))[0]
    txt_filename = f"{epub_name}_converted.txt"
    txt_path = os.path.join(output_dir, txt_filename)
    
    # Write text to file
    try:
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text_content)
    except Exception as e:
        raise ValueError(f"Failed to write TXT file: {str(e)}")
    
    return txt_path


def get_or_convert_to_txt(file_path: str, temp_dir: str = None) -> Tuple[str, bool]:
    """
    Get a TXT file path, converting from EPUB if necessary.
    
    Args:
        file_path: Path to the input file (EPUB or TXT)
        temp_dir: Directory for temporary files (optional)
        
    Returns:
        Tuple of (txt_file_path, is_temporary)
        - txt_file_path: Path to the TXT file
        - is_temporary: True if a temporary file was created
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If conversion fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.epub':
        # Convert EPUB to TXT
        print(f"Converting EPUB to TXT: {os.path.basename(file_path)}")
        txt_path = convert_epub_to_txt(file_path, temp_dir)
        print(f"Conversion complete: {txt_path}")
        return txt_path, True
    elif ext in ['.txt', '.text']:
        # Already a text file
        return file_path, False
    else:
        # Try to treat as text file
        try:
            # Test if we can read it as text
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)  # Read first 100 chars as test
            return file_path, False
        except UnicodeDecodeError:
            raise ValueError(f"Unsupported file format: {ext}")


def cleanup_temp_file(file_path: str, is_temporary: bool = True) -> None:
    """
    Clean up temporary file if needed.
    
    Args:
        file_path: Path to the file
        is_temporary: Whether the file is temporary and should be deleted
    """
    if is_temporary and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            print(f"Warning: Could not clean up temporary file {file_path}: {e}")


class EPUBProcessor:
    """Context manager for processing EPUB files with automatic cleanup"""
    
    def __init__(self, file_path: str, temp_dir: str = None):
        self.original_path = file_path
        self.temp_dir = temp_dir
        self.txt_path = None
        self.is_temporary = False
    
    def __enter__(self) -> str:
        """Convert file to TXT and return the path"""
        self.txt_path, self.is_temporary = get_or_convert_to_txt(
            self.original_path, 
            self.temp_dir
        )
        return self.txt_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary files"""
        if self.txt_path:
            cleanup_temp_file(self.txt_path, self.is_temporary)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python epub_to_txt_converter.py <epub_file>")
        sys.exit(1)
    
    epub_file = sys.argv[1]
    
    try:
        # Convert EPUB to TXT
        txt_file = convert_epub_to_txt(epub_file)
        print(f"Successfully converted {epub_file} to {txt_file}")
        
        # Show file info
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Generated TXT file: {len(content)} characters")
            print(f"Preview: {content[:200]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
