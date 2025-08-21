"""
EPUB text extraction utilities for AI workflow
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional
import html
import re


class EPUBTextExtractor:
    """Extract plain text from EPUB files"""
    
    def __init__(self):
        self.namespaces = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
    
    def extract_text(self, epub_path: str) -> str:
        """
        Extract plain text from an EPUB file.
        
        Args:
            epub_path: Path to the EPUB file
            
        Returns:
            Extracted plain text content
            
        Raises:
            FileNotFoundError: If EPUB file doesn't exist
            ValueError: If file is not a valid EPUB
        """
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as epub_zip:
                # Find the content.opf file
                container_path = 'META-INF/container.xml'
                if container_path not in epub_zip.namelist():
                    raise ValueError("Invalid EPUB: Missing container.xml")
                
                # Parse container.xml to find OPF file
                container_content = epub_zip.read(container_path)
                container_root = ET.fromstring(container_content)
                
                opf_path = None
                # Try different ways to find the OPF file
                for rootfile in container_root.findall('.//rootfile'):
                    media_type = rootfile.get('media-type', '')
                    if 'oebps-package' in media_type or 'opf' in media_type:
                        opf_path = rootfile.get('full-path')
                        break
                
                # Fallback: look for any .opf file
                if not opf_path:
                    for file_name in epub_zip.namelist():
                        if file_name.endswith('.opf'):
                            opf_path = file_name
                            break
                
                if not opf_path:
                    # Last resort: try to extract text from all HTML/XHTML files
                    return self._extract_text_fallback(epub_zip)
                
                # Parse OPF file to get reading order
                opf_content = epub_zip.read(opf_path)
                opf_root = ET.fromstring(opf_content)
                
                # Get the base directory for the OPF file
                opf_dir = os.path.dirname(opf_path)
                
                # Extract text from all content files in reading order
                text_parts = []
                
                # Get spine (reading order)
                spine = opf_root.find('.//opf:spine', self.namespaces)
                if spine is not None:
                    manifest_items = {}
                    manifest = opf_root.find('.//opf:manifest', self.namespaces)
                    if manifest is not None:
                        for item in manifest.findall('.//opf:item', self.namespaces):
                            item_id = item.get('id')
                            href = item.get('href')
                            if item_id and href:
                                manifest_items[item_id] = href
                    
                    # Process files in spine order
                    for itemref in spine.findall('.//opf:itemref', self.namespaces):
                        idref = itemref.get('idref')
                        if idref in manifest_items:
                            file_path = manifest_items[idref]
                            if opf_dir:
                                file_path = f"{opf_dir}/{file_path}"
                            
                            try:
                                if file_path in epub_zip.namelist():
                                    content_bytes = epub_zip.read(file_path)
                                    content = self._decode_content_safely(content_bytes)
                                    text = self._extract_text_from_html(content)
                                    if text.strip():
                                        text_parts.append(text)
                            except Exception as e:
                                print(f"Warning: Could not extract text from {file_path}: {e}")
                                continue
                
                return '\n\n'.join(text_parts)
                
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid EPUB file: {epub_path}")
        except Exception as e:
            raise ValueError(f"Error extracting EPUB content: {str(e)}")
    
    def _decode_content_safely(self, content_bytes: bytes) -> str:
        """
        Safely decode content bytes with multiple encoding attempts.
        
        Args:
            content_bytes: Raw bytes from file
            
        Returns:
            Decoded string content
        """
        # List of encodings to try in order
        encodings_to_try = [
            'utf-8',
            'utf-16',
            'utf-16le',
            'utf-16be', 
            'latin-1',
            'cp1252',
            'iso-8859-1',
            'ascii'
        ]
        
        for encoding in encodings_to_try:
            try:
                return content_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, use UTF-8 with error replacement
        return content_bytes.decode('utf-8', errors='replace')
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML/XHTML content.
        
        Args:
            html_content: HTML/XHTML content string
            
        Returns:
            Plain text content
        """
        try:
            # Parse as XML/HTML
            # Remove XML declaration and DOCTYPE if present
            html_content = re.sub(r'<\?xml[^>]*\?>', '', html_content)
            html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content)
            
            # Try to parse as XML first
            try:
                root = ET.fromstring(html_content)
                text = self._extract_text_from_element(root)
            except ET.ParseError:
                # Fallback: simple regex-based text extraction
                text = self._extract_text_with_regex(html_content)
            
            # Clean up the text
            text = html.unescape(text)
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            print(f"Warning: Error parsing HTML content: {e}")
            # Fallback to regex extraction
            return self._extract_text_with_regex(html_content)
    
    def _extract_text_from_element(self, element) -> str:
        """Recursively extract text from XML element"""
        text_parts = []
        
        # Add element text
        if element.text:
            text_parts.append(element.text)
        
        # Process child elements
        for child in element:
            child_text = self._extract_text_from_element(child)
            if child_text:
                text_parts.append(child_text)
            
            # Add tail text
            if child.tail:
                text_parts.append(child.tail)
        
        return ' '.join(text_parts)
    
    def _extract_text_with_regex(self, html_content: str) -> str:
        """Fallback text extraction using regex"""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _extract_text_fallback(self, epub_zip) -> str:
        """
        Fallback method to extract text from all HTML/XHTML files in EPUB.
        Used when OPF parsing fails.
        """
        text_parts = []
        
        # Look for common content file patterns
        for file_name in epub_zip.namelist():
            if any(file_name.lower().endswith(ext) for ext in ['.html', '.xhtml', '.htm']):
                # Skip navigation and table of contents files
                if any(skip in file_name.lower() for skip in ['nav', 'toc', 'ncx']):
                    continue
                
                try:
                    content_bytes = epub_zip.read(file_name)
                    content = self._decode_content_safely(content_bytes)
                    text = self._extract_text_from_html(content)
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    print(f"Warning: Could not extract from {file_name}: {e}")
                    continue
        
        return '\n\n'.join(text_parts)


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a file (EPUB or plain text).
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.epub':
        # Extract text from EPUB
        extractor = EPUBTextExtractor()
        return extractor.extract_text(file_path)
    else:
        # Try to read as plain text
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                raise ValueError(f"Cannot read file {file_path}: {str(e)}")
