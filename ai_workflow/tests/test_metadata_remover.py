#!/usr/bin/env python3
"""
Test script for the improved priority logic in metadata removal.
Tests that content markers are prioritized over metadata detection.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocessors.metadata_remover import remove_book_metadata

def test_priority_logic():
    """Test the improved priority logic that checks content markers first."""
    
    # Test 1: Content marker exists - should prioritize content marker
    test_text1 = """نشر وتوزيع دار النشر
حقوق محفوظة 2024
فصل أول: بداية القصة
هذا هو المحتوى الحقيقي للرواية."""
    
    print("Test 1: Content marker exists - should prioritize content marker")
    print("Original:")
    print(test_text1)
    print("-" * 50)
    
    cleaned1 = remove_book_metadata(test_text1)
    print("Cleaned:")
    print(cleaned1)
    print("-" * 50)
    
    if cleaned1.startswith("فصل أول"):
        print("✓ SUCCESS: Correctly prioritized content marker over metadata")
    else:
        print("✗ FAILED: Did not prioritize content marker")
    
    # Test 2: Content marker with metadata keywords in prose - should still prioritize content marker
    test_text2 = """فصل أول: بداية القصة
هذا هو المحتوى الحقيقي للرواية الذي يتحدث عن المؤلف والكاتب والأديب الذي كتب هذه الرواية الرائعة التي نشرتها دار النشر المعروفة في جميع أنحاء العالم."""
    
    print("\nTest 2: Content marker with metadata keywords in prose")
    print("Original:")
    print(test_text2)
    print("-" * 50)
    
    cleaned2 = remove_book_metadata(test_text2)
    print("Cleaned:")
    print(cleaned2)
    print("-" * 50)
    
    if cleaned2.startswith("فصل أول"):
        print("✓ SUCCESS: Correctly prioritized content marker despite metadata keywords in prose")
    else:
        print("✗ FAILED: Did not prioritize content marker when metadata keywords were in prose")
    
    # Test 3: No content marker, only metadata - should remove metadata
    test_text3 = """نشر وتوزيع دار النشر
حقوق محفوظة 2024
هذا هو المحتوى الحقيقي للرواية الذي يتحدث عن المؤلف والكاتب والأديب الذي كتب هذه الرواية الرائعة التي نشرتها دار النشر المعروفة في جميع أنحاء العالم."""
    
    print("\nTest 3: No content marker, only metadata")
    print("Original:")
    print(test_text3)
    print("-" * 50)
    
    cleaned3 = remove_book_metadata(test_text3)
    print("Cleaned:")
    print(cleaned3)
    print("-" * 50)
    
    if cleaned3.startswith("هذا هو المحتوى"):
        print("✓ SUCCESS: Correctly removed metadata when no content markers were found")
    else:
        print("✗ FAILED: Did not correctly handle case with only metadata")
    
    # Test 4: No markers at all - should return original text
    test_text4 = """هذا هو المحتوى الحقيقي للرواية الذي يتحدث عن المؤلف والكاتب والأديب الذي كتب هذه الرواية الرائعة التي نشرتها دار النشر المعروفة في جميع أنحاء العالم."""
    
    print("\nTest 4: No markers at all")
    print("Original:")
    print(test_text4)
    print("-" * 50)
    
    cleaned4 = remove_book_metadata(test_text4)
    print("Cleaned:")
    print(cleaned4)
    print("-" * 50)
    
    if cleaned4 == test_text4:
        print("✓ SUCCESS: Correctly returned original text when no markers were found")
    else:
        print("✗ FAILED: Did not return original text when no markers were found")
    
    # Test with actual file
    test_file_path = "resources/texts/05 أسطورة الموتى الأحياء_djvu.txt"
    
    if os.path.exists(test_file_path):
        print(f"\nTesting with actual file: {test_file_path}")
        with open(test_file_path, 'r', encoding='utf-8') as file:
            original_text = file.read()
        
        print(f"Original length: {len(original_text)}")
        print(f"First 200 characters:")
        print(original_text[:200])
        print("-" * 50)
        
        cleaned_text = remove_book_metadata(original_text)
        print(f"Cleaned length: {len(cleaned_text)}")
        print(f"Removed: {len(original_text) - len(cleaned_text)} characters")
        print(f"First 200 characters of cleaned text:")
        print(cleaned_text[:200])
        
        # Save for inspection
        output_path = "resources/texts/cleaned/" + test_file_path.split('/')[-1].replace('.txt', '_cleaned.txt')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_text)
        print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    test_priority_logic() 