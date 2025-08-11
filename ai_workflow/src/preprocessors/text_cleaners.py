import re
import os

def normalize_arabic_characters(text):
    """
    Comprehensive Arabic character normalization.
    """
    # Normalize different forms of letters
    replacements = {
        # Alif variations
        '\u0622': '\u0627',  # Alif with madda
        '\u0623': '\u0627',  # Alif with hamza above
        '\u0625': '\u0627',  # Alif with hamza below
        
        # Remove Arabic diacritics (harakat)
        '\u064B': '',  # Fatha
        '\u064C': '',  # Kasra
        '\u064D': '',  # Damma
        '\u064E': '',  # Fathatan
        '\u064F': '',  # Kasratan
        '\u0650': '',  # Damma on top
        '\u0651': '',  # Kasra on top
        '\u0652': '',  # Fathatan on top
        '\u0629': '\u0647',  # Ta Marbuta to Ha (optional)
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def normalize_arabic_numbers(text):
    """
    Normalize Arabic numerals to English numerals or vice versa.
    """
    # Arabic to English numerals
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    # English to Arabic numerals (alternative)
    english_to_arabic = {
        '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
    }

    for arabic, english in arabic_to_english.items():
        text = text.replace(arabic, english)
    
    return text

def normalize_arabic_punctuation(text):
    """
    Normalize Arabic punctuation marks.
    """
    # Arabic punctuation to English equivalents
    punctuation_map = {
        '،': ',',      # Arabic comma
        '؛': ';',      # Arabic semicolon
        '؟': '?',      # Arabic question mark
        '！': '!',      # Arabic exclamation mark
        'ـ': '-',      # Arabic tatweel (elongation)
        '…': '...',    # Arabic ellipsis
        '«': '"',      # Arabic left double quotation mark
        '»': '"',      # Arabic right double quotation mark
        '‹': "'",      # Arabic left single quotation mark
        '›': "'",      # Arabic right single quotation mark
    }
    
    for arabic, english in punctuation_map.items():
        text = text.replace(arabic, english)
    
    return text


def normalize_arabic_spacing(text):
    """
    Normalize spacing around Arabic text elements.
    """
    # Remove extra spaces around punctuation
    text = re.sub(r'\s+([،؛؟!])', r'\1', text)
    text = re.sub(r'([،؛؟!])\s+', r'\1 ', text)
    
    # Normalize spacing around numbers
    text = re.sub(r'(\d+)\s+(\d+)', r'\1\2', text)
    
    # Remove spaces before punctuation marks
    text = re.sub(r'\s+([،؛؟!])', r'\1', text)
    
    return text

def clean_arabic_text_comprehensive(text):
    """
    Comprehensive Arabic text cleaning with all normalizations.
    """
    # Apply all normalizations in order
    text = re.sub(r'\s+', ' ', text).strip()  # Basic cleaning
    text = normalize_arabic_characters(text)  # Character normalization
    text = normalize_arabic_numbers(text)  # Number normalization
    text = normalize_arabic_punctuation(text)  # Punctuation normalization
    text = normalize_arabic_spacing(text)  # Spacing normalization
    
    return text



# test_text = "resources/texts/01- رواية أرض الإله - احمد مراد_djvu.txt"
# with open(test_text, 'r', encoding='utf-8') as file:
#     text = file.read()
#     save_to_path = "resources/texts/cleaned/أرض الإله_cleaned.txt"
#     #create the directory if it doesn't exist
#     os.makedirs(os.path.dirname(save_to_path), exist_ok=True)
#     with open(save_to_path, 'w', encoding='utf-8') as file:
#         file.write(clean_arabic_text_comprehensive(text))
