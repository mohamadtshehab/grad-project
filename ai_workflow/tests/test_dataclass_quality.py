#!/usr/bin/env python3
"""
Test script for dataclass-based Arabic Text Quality Assessment
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.schemas.data_classes import TextQualityAssessment
from src.preprocessors.text_quality_assessor import assess_arabic_text_quality


def test_dataclass_quality():
    """Test the dataclass-based Arabic text quality assessment"""
    
    # Test cases with different quality levels
    test_cases = [
        {
            "text": "الطريق كان مزدحم اليوم",
            "description": "Good quality - normal Arabic text"
        },
        {
            "text": "ال3طريق ك@ن مزدحم",
            "description": "Poor quality - OCR errors with numbers and symbols"
        },
        {
            "text": "",
            "description": "Empty text"
        }
    ]
    
    print("Testing Dataclass-based Arabic Text Quality Assessment")
    print("=" * 60)
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        description = test_case["description"]
        
        print(f"Test Case {i}: {description}")
        print(f"Text: '{text}'")
        
        # Assess quality
        result = assess_arabic_text_quality(text)
        
        # Display results
        print(f"Quality Score: {result['final_quality_score']:.4f}")
        print(f"Quality Level: {result['quality_level']}")
        print(f"Issues: {result['issues']}")
        print(f"Suggestions: {result['suggestions']}")
        print(f"Reasoning: {result['reasoning']}")
        
        # Test dataclass
        if 'assessment' in result:
            assessment = result['assessment']
            print(f"Dataclass - Quality Score: {assessment.quality_score}")
            print(f"Dataclass - Quality Level: {assessment.quality_level}")
            print(f"Dataclass - Issues: {assessment.issues}")
            print(f"Dataclass - Suggestions: {assessment.suggestions}")
            print(f"Dataclass - Reasoning: {assessment.reasoning}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        print("-" * 60)
        print()


if __name__ == "__main__":
    test_dataclass_quality() 