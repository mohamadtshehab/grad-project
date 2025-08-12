import os
import random
from typing import List


def get_validation_chunks(file_path: str, lines_per_chunk: int = 20, num_chunks_to_select: int = 10) -> str:
    """
    Process a text file into chunks for validation purposes.
    
    Args:
        file_path: Path to the text file
        lines_per_chunk: Number of lines per chunk
        num_chunks_to_select: Number of random chunks to select
        
    Returns:
        Formatted string of selected chunks for LLM processing
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text_lines = file.readlines()
    
    def get_non_overlapping_chunks(lines: List[str], num_lines_per_chunk: int) -> List[str]:
        """
        Splits a list of lines into non-overlapping chunks.
        """
        chunks = []
        for i in range(0, len(lines), num_lines_per_chunk): 
            chunk = "".join(lines[i:i + num_lines_per_chunk])
            chunks.append(chunk)
        return chunks

    all_chunks = get_non_overlapping_chunks(raw_text_lines, lines_per_chunk)
    
    # Select random, non-overlapping chunks
    if len(all_chunks) > num_chunks_to_select:
        random_chunks = random.sample(all_chunks, num_chunks_to_select)
    else:
        random_chunks = all_chunks

    # Format the selected chunks for the LLM
    formatted_chunks = ""
    for i, chunk in enumerate(random_chunks):
        formatted_chunks += f"Chunk {i+1}:\n{chunk}\n"
    
    return formatted_chunks