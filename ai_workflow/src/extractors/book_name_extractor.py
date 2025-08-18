import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports to work correctly
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from language_models.llms import book_name_extraction_llm
from language_models.prompts import book_name_extraction_prompt
from language_models.chains import book_name_extraction_chain
from schemas.output_structures import Book


def extract_book_name_from_file(file_path: str):
    """
    Extract book name from file content using LLM
    
    Args:
        book: Book object containing the file
        filename: Original filename for context
        
    Returns:
        Book: Structured output with book name, confidence, and reasoning
    """
    try:
        # Extract text content from the file (handles EPUB and plain text)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        filename = os.path.basename(file_path)
        
        # Extract first 3000 and last 1000 characters
        first_3000_chars = content[:3000]
        last_1000_chars = content[-1000:]
        
        # Format the prompt with file content
        chain_input = {
            "first_300_chars": first_3000_chars,
            "last_100_chars": last_1000_chars,
            'filename': filename
        }
    
        response = book_name_extraction_chain.invoke(chain_input)
        return response
        
    except Exception as e:
        # Return a fallback result if LLM fails
        fallback_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        return Book(
            book_name=fallback_name,
            confidence="منخفض",
            reasoning=f"فشل في استخراج الاسم من المحتوى: {str(e)}. تم استخدام اسم الملف كبديل."
        )
