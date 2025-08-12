from django.contrib import admin
from .models import Chunk


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    """Admin configuration for Chunk model"""
    
    list_display = ['chunk_number', 'book_title', 'word_count', 'character_count_display', 'created_at']
    list_filter = ['book_id', 'created_at']
    search_fields = ['chunk_text', 'book_id__title']
    ordering = ['book_id', 'chunk_number']
    readonly_fields = ['chunk_id', 'created_at', 'updated_at', 'character_count', 'word_count']
    
    fieldsets = (
        (None, {
            'fields': ('chunk_id', 'book_id', 'chunk_number')
        }),
        ('Content', {
            'fields': ('chunk_text',)
        }),
        ('Metadata', {
            'fields': ('start_position', 'end_position', 'word_count', 'character_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def book_title(self, obj):
        """Display the book title"""
        return obj.book_id.title
    book_title.short_description = "Book"
    
    def character_count_display(self, obj):
        """Display character count"""
        return obj.character_count
    character_count_display.short_description = "Characters"
    
    def get_preview(self, obj):
        """Display a preview of the chunk text"""
        return obj.get_preview(50)
    get_preview.short_description = "Preview"
