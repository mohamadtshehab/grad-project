def remove_book_metadata(text: str) -> str:
    """
    Remove book metadata from the beginning of Arabic text.
    
    This function identifies and removes initial metadata sections (title page, 
    author, publisher, table of contents) and returns only the main literary content.
    
    The algorithm prioritizes content markers over metadata detection:
    - First, searches for content markers (فصل, أول, جزء) in the entire search window
    - Only if no content markers are found, then looks for metadata keywords
    - Metadata keywords are only considered valid if they appear on short lines (≤80 chars)
    - This prevents false positives when metadata words appear in long prose paragraphs
    
    Args:
        text (str): The full text of the book
        
    Returns:
        str: The text with metadata removed, or the original text if no metadata is detected
    """
    
    # Step 1: Configuration
    SEARCH_WINDOW_SIZE = 2000
    MAX_METADATA_LINE_LENGTH = 80
    METADATA_KEYWORDS = [
        'نشر', 'ترجمة', 'شركة', 'صحافة', 'طباعة', 'توزيع', 'موافقة', 
        'ناشر', 'غلاف', 'تأليف', 'مركز', 'دار', 'حقوق', 'محفوظة', 
        'كاتب', 'أديب', 'مؤلف', 'رقم', 'تاريخ', 'رواية', 'كتاب', 
        'نسخة', 'غلاف', 'قانون', 'شركة', 'مترجم', 'طبعة', 'تحرير', 
        'محرر', 'إهداء', 'فاكس'
    ]
    START_KEYWORDS = ['فصل', 'أول', 'جزء']
    
    # Step 2: Isolate the Search Area and Split into Lines
    search_window = text[:SEARCH_WINDOW_SIZE]
    lines = search_window.split('\n')
    
    # Step 3: Find the First True Content Marker (PRIORITY)
    first_start_pos = -1
    
    for keyword in START_KEYWORDS:
        pos = search_window.find(keyword)
        if pos != -1:
            if first_start_pos == -1:
                first_start_pos = pos
            else:
                first_start_pos = min(first_start_pos, pos)
    
    # Step 4: If no content marker found, then look for metadata
    last_metadata_pos = -1
    
    if first_start_pos == -1:
        # Only check for metadata if no content markers were found
        for line in lines:
            # Check if this line contains a metadata keyword
            for keyword in METADATA_KEYWORDS:
                if keyword in line:
                    # Check if the line is short enough to be considered metadata
                    if len(line.strip()) <= MAX_METADATA_LINE_LENGTH:
                        # Find the position of this keyword in the original search_window
                        line_start_pos = search_window.find(line)
                        keyword_pos_in_line = line.find(keyword)
                        absolute_keyword_pos = line_start_pos + keyword_pos_in_line
                        
                        # Update last_metadata_pos if this is the latest valid metadata tag
                        if absolute_keyword_pos > last_metadata_pos:
                            last_metadata_pos = absolute_keyword_pos
    
    # Step 5: Determine the Final Slice Index
    final_slice_index = None
    
    # Primary Case: Content marker found
    if first_start_pos != -1:
        # Start from the exact character where the content marker begins
        final_slice_index = first_start_pos
    
    # Fallback Case: Metadata found but no clear content marker
    elif last_metadata_pos != -1:
        # Start from the next character after the last metadata keyword
        # Find the end of the metadata keyword
        remaining_text = search_window[last_metadata_pos:]
        words = remaining_text.split()
        if words:
            # Find the end of the first word (which should be the metadata keyword)
            first_word_end = remaining_text.find(words[0]) + len(words[0])
            final_slice_index = last_metadata_pos + first_word_end
        else:
            # If no words found, start from the next character
            final_slice_index = last_metadata_pos + 1
    
    # Worst Case: No markers found
    else:
        # Return original text without modification
        return text
    
    # Step 6: Return the Result
    if final_slice_index is not None:
        return text[final_slice_index:]
    
    return text 