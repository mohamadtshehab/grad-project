"""
Custom parsers for handling EPUB file uploads
"""

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ParseError
import logging

logger = logging.getLogger(__name__)


class EPUBMultiPartParser(MultiPartParser):
    """
    Custom MultiPartParser that handles EPUB files properly
    """
    
    media_type = 'multipart/form-data'
    
    def parse(self, stream, media_type=None, parser_context=None):
        """
        Override parse method to handle EPUB files
        """
        try:
            # Log the incoming request details
            request = parser_context.get('request') if parser_context else None
            if request:
                logger.info(f"Parsing request with content type: {request.content_type}")
                logger.info(f"Request META CONTENT_TYPE: {request.META.get('CONTENT_TYPE', 'Not set')}")
            
            # Call the parent parse method
            result = super().parse(stream, media_type, parser_context)
            
            # Log the parsed result
            logger.info(f"Parsed files: {list(result.files.keys()) if hasattr(result, 'files') else 'No files'}")
            logger.info(f"Parsed data: {list(result.data.keys()) if hasattr(result, 'data') else 'No data'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing multipart data: {str(e)}")
            raise ParseError(f"Multipart form parse error: {str(e)}")


class FlexibleMultiPartParser(MultiPartParser):
    """
    A more flexible multipart parser that accepts various content types
    """
    
    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parse multipart data with flexible content type handling
        """
        try:
            # Get the request from parser context
            request = parser_context.get('request') if parser_context else None
            
            if request and media_type:
                logger.info(f"Original media type: {media_type}")
                
                # If the media type contains 'multipart', treat it as multipart/form-data
                if 'multipart' in media_type.lower():
                    # Force the media type to be multipart/form-data
                    media_type = 'multipart/form-data'
                    logger.info(f"Adjusted media type to: {media_type}")
            
            return super().parse(stream, media_type, parser_context)
            
        except Exception as e:
            logger.error(f"Flexible parser error: {str(e)}")
            # Try to parse with default multipart/form-data
            try:
                return super().parse(stream, 'multipart/form-data', parser_context)
            except Exception as fallback_error:
                logger.error(f"Fallback parser error: {str(fallback_error)}")
                raise ParseError(f"Unable to parse request: {str(e)}")
