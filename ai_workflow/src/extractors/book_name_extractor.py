import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports to work correctly
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from language_models.llms import book_name_extraction_llm
from language_models.prompts import book_name_extraction_prompt
from schemas.output_structures import Book


def extract_book_name_from_file(book, filename: str):
    """
    Extract book name from file content using LLM
    
    Args:
        book: Book object containing the file
        filename: Original filename for context
        
    Returns:
        Book: Structured output with book name, confidence, and reasoning
    """
    try:
        # Read file content - EPUB files are binary, so we need to handle encoding properly
        try:
            # Try to read as text with UTF-8 encoding
            with book.file.open(mode='r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except (UnicodeDecodeError, TypeError):
            # If that fails, try reading as bytes and decoding
            with book.file.open(mode='rb') as f:
                content_bytes = f.read()
                # Try different encodings
                for encoding in ['utf-8', 'cp1256', 'iso-8859-6', 'windows-1256']:
                    try:
                        content = content_bytes.decode(encoding, errors='ignore')
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # If all encodings fail, use the filename
                    raise Exception("Unable to decode file content with any supported encoding")
        
        # Extract first 3000 and last 1000 characters
        first_3000_chars = content[:3000]
        last_1000_chars = content[-1000:]
        
        # Format the prompt with file content
        formatted_prompt = book_name_extraction_prompt.format(
            filename=filename,
            first_3000_chars=first_3000_chars,
            last_1000_chars=last_1000_chars
        )
        
        # Call the LLM
        response = book_name_extraction_llm.invoke(formatted_prompt)
        
        return response
        
    except Exception as e:
        # Return a fallback result if LLM fails
        fallback_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        return Book(
            book_name=fallback_name,
            confidence="منخفض",
            reasoning=f"فشل في استخراج الاسم من المحتوى: {str(e)}. تم استخدام اسم الملف كبديل."
        )


if __name__ == "__main__":
    # Test the extractor
    if len(sys.argv) != 2:
        print("Usage: python book_name_extractor.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    filename = os.path.basename(file_path)
    
    # Create a mock book object for testing
    class MockBook:
        def __init__(self, file_path):
            self.file_path = file_path
        
        @property
        def file(self):
            class MockFile:
                def __init__(self, path):
                    self.path = path
                
                def open(self, mode='r', encoding=None, errors=None):
                    if mode == 'rb':
                        return open(self.path, 'rb')
                    else:
                        return open(self.path, mode, encoding=encoding, errors=errors)
            return MockFile(self.file_path)
    
    try:
        mock_book = MockBook(file_path)
        result = extract_book_name_from_file(mock_book, filename)
        print(f"Book Name: {result.book_name}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
