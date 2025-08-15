from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
    HTMLHeaderTextSplitter,
    SentenceTransformersTokenTextSplitter
)
from typing import List, Optional, Dict, Any
import os
import random


class TextChunker:
    """
    A utility class for chunking text using various LangChain text splitters.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text chunker with default parameters.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize the default recursive splitter
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def chunk_text_recursive(self, text: str) -> List[str]:
        """
        Split text using RecursiveCharacterTextSplitter (recommended for most use cases).
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        return self.recursive_splitter.split_text(text)
    
    def chunk_text_character(self, text: str, separator: str = "\n") -> List[str]:
        """
        Split text using CharacterTextSplitter.
        
        Args:
            text: The text to split
            separator: Character to split on
            
        Returns:
            List of text chunks
        """
        splitter = CharacterTextSplitter(
            separator=separator,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        return splitter.split_text(text)
    
    def chunk_text_token(self, text: str, model_name: str = "gpt-3.5-turbo") -> List[str]:
        """
        Split text using TokenTextSplitter (useful for token-aware splitting).
        
        Args:
            text: The text to split
            model_name: The model name for token counting
            
        Returns:
            List of text chunks
        """
        splitter = TokenTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            model_name=model_name
        )
        return splitter.split_text(text)
    

    
    def chunk_text_sentence_transformers(self, text: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[str]:
        """
        Split text using SentenceTransformersTokenTextSplitter.
        
        Args:
            text: The text to split
            model_name: The sentence transformer model name
            
        Returns:
            List of text chunks
        """
        splitter = SentenceTransformersTokenTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            model_name=model_name
        )
        return splitter.split_text(text)
    
    def chunk_text_arabic_optimized(self, text: str) -> List[str]:
        """
        Split Arabic text with optimizations for Arabic language characteristics.
        
        Args:
            text: The Arabic text to split
            
        Returns:
            List of text chunks
        """
        # Custom separators optimized for Arabic text
        arabic_separators = [
            "\n\n",  # Paragraph breaks
            "\n",    # Line breaks
            ". ",    # Sentence endings
            "؟ ",    # Question mark
            "! ",    # Exclamation mark
            "، ",    # Arabic comma
            "؛ ",    # Arabic semicolon
            " ",     # Space
            ""       # Character level
        ]
        
        arabic_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=arabic_separators
        )
        
        return arabic_splitter.split_text(text)
    
    
def get_validation_chunks(
    file_path: str,
    chunk_size: int = 20,
    num_chunks_to_select: int = 10
) -> str:
    """
    Processes a text file into randomly selected chunks for validation.

    The chunking method depends on the target_node:
    - 'classification': Chunks are based on a number of words (chunk_size).
    - 'quality_assessment': Chunks are based on a number of lines (chunk_size).

    Args:
        file_path: Path to the text file.
        chunk_size: Number of words or lines per chunk, depending on the target_node.
        num_chunks_to_select: Number of random chunks to select.

    Returns:
        A formatted string of selected chunks for LLM processing.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    # Validate file path first to avoid redundant checks
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    all_chunks: List[str] = []
    with open(file_path, 'r', encoding='utf-8') as file:
        # Split the entire text into words
        content = file.read().split()
        # Create word-based chunks using a list comprehension
        all_chunks = [
            " ".join(content[i : i + chunk_size])
            for i in range(0, len(content), chunk_size)
        ]

    # Select random chunks, ensuring we don't request more than exist
    num_to_sample = min(num_chunks_to_select, len(all_chunks))
    selected_chunks = random.sample(all_chunks, k=num_to_sample)

    # Format the selected chunks into a final string efficiently
    return "".join(
        f"Chunk {i+1}:\n{chunk}\n" for i, chunk in enumerate(selected_chunks)
    )