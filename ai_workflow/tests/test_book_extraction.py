#!/usr/bin/env python3
"""
Test script for book name extraction LLM
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.language_models.llms import book_name_extraction_llm
from src.language_models.prompts import book_name_extraction_prompt

def read_file_content(file_path, first_chars=3000, last_chars=1000):
    """Read file content and extract first and last characters"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        first_3000 = content[:first_chars]
        last_1000 = content[-last_chars:] if len(content) > last_chars else content
        
        return first_3000, last_1000
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return "", ""

def test_book_extraction():
    """Test the book name extraction LLM with actual files"""
    
    test_cases = [
        {
            "file_path": "resources/texts/وجـه من المـاضي_djvu.txt",
        },
        {
            "file_path": "resources/texts/رواية عشق قرقّلا .txt",
        },
        {
            "file_path": "resources/texts/lskfdlks.txt",
        }
    ]
    
    print("Testing Book Name Extraction LLM")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        file_path = test_case["file_path"]
        filename = test_case["file_path"].split('/')[-1]
        
        print(f"\nTest Case {i}:")
        print(f"File Path: {file_path}")
        print(f"Filename: {filename}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print("-" * 50)
            continue
        
        try:
            # Read file content
            first_3000_chars, last_1000_chars = read_file_content(file_path)
            
            if not first_3000_chars:
                print(f"❌ Could not read file content: {file_path}")
                print("-" * 50)
                continue
            
            print(f"First 3000 chars: {first_3000_chars[:100]}...")
            print(f"Last 1000 chars: {last_1000_chars[:100]}...")
            
            # Create the prompt
            prompt = book_name_extraction_prompt.format(
                filename=filename,
                first_3000_chars=first_3000_chars,
                last_1000_chars=last_1000_chars
            )
            
            # Get the result
            result = book_name_extraction_llm.invoke(prompt)
            
            print(f"\n✅ Result:")
            print(f"  Book Name: {result.book_name}")
            print(f"  Confidence: {result.confidence}")
            print(f"  Reasoning: {result.reasoning}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_book_extraction() 