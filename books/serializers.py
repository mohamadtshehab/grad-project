from rest_framework import serializers
from .models import Book
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import os


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for listing user's books"""
    
    file_size_mb = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 
            'processing_status', 'file_size_mb', 'file_extension',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_size_mb(self, obj):
        """Return file size in MB"""
        try:
            size_bytes = obj.file.size
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0
    
    def get_file_extension(self, obj):
        """Return file extension"""
        try:
            return os.path.splitext(obj.file.name)[1].lower()
        except:
            return None


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed book information"""
    
    file_size_mb = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 
            'processing_status', 'processing_error',
            'file_size_mb', 'file_extension', 'file_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'processing_status', 'processing_error',
            'created_at', 'updated_at'
        ]
    
    def get_file_size_mb(self, obj):
        """Return file size in MB"""
        try:
            size_bytes = obj.file.size
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0
    
    def get_file_extension(self, obj):
        """Return file extension"""
        try:
            return os.path.splitext(obj.file.name)[1].lower()
        except:
            return None
    
    def get_file_name(self, obj):
        """Return original file name"""
        try:
            return os.path.basename(obj.file.name)
        except:
            return None


class BookUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading books"""
    
    class Meta:
        model = Book
        fields = ['title', 'file']
        
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check if file exists
        if not value:
            raise serializers.ValidationError("No file provided.")
            
        # Check file extension
        if not hasattr(value, 'name') or not value.name:
            raise serializers.ValidationError("Invalid file name.")
            
        ext = os.path.splitext(value.name)[1].lower()
        if ext != '.epub':
            raise serializers.ValidationError("Only EPUB files are allowed.")
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        try:
            file_size = getattr(value, 'size', 0)
            if file_size > max_size:
                raise serializers.ValidationError(
                    f"File size too large. Maximum allowed size is 50MB. "
                    f"Your file is {round(file_size / (1024 * 1024), 2)}MB."
                )
        except Exception:
            # If we can't get the size, allow it to proceed
            pass
        
        return value
    
    def create(self, validated_data):
        """Create book instance with user"""
        # Add user from context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BookStatusSerializer(serializers.ModelSerializer):
    """Serializer for book processing status"""
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'processing_status', 
            'processing_error', 'updated_at'
        ]
        read_only_fields = ['id', 'title', 'processing_status', 'processing_error', 'updated_at']



