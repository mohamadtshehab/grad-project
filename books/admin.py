from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model"""
    
    list_display = ['title', 'author', 'user', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at', 'author']
    search_fields = ['title', 'author', 'description']
    ordering = ['-created_at']
    readonly_fields = ['book_id', 'created_at', 'updated_at', 'file_size', 'file_extension']
    
    fieldsets = (
        (None, {
            'fields': ('book_id', 'title', 'author', 'description', 'user')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'file_extension')
        }),
        ('Status', {
            'fields': ('is_deleted',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in a readable format"""
        size = obj.file_size
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    file_size_display.short_description = "File Size"
