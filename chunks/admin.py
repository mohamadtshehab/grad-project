from django.contrib import admin
from .models import Chunk


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    """Admin configuration for Chunk model"""

<<<<<<< HEAD
    list_display = ['chunk_number', 'book_title', 'word_count', 'created_at']
=======
    list_display = ['chunk_number', 'book_title', 'created_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    # Use the model field 'book', not the db column 'book_id'
    list_filter = ['book', 'created_at']
    # Use 'book__title' to traverse the relationship
    search_fields = ['chunk_text', 'book__title']
    # Use the model field 'book' for ordering
    ordering = ['book', 'chunk_number']
<<<<<<< HEAD
    readonly_fields = ['chunk_id', 'created_at', 'updated_at', 'word_count']
=======
    readonly_fields = ['id', 'created_at', 'updated_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96

    fieldsets = (
        (None, {
            # Use the model field 'book'
<<<<<<< HEAD
            'fields': ('chunk_id', 'book', 'chunk_number')
=======
            'fields': ('id', 'book', 'chunk_number')
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
        }),
        ('Content', {
            'fields': ('chunk_text',)
        }),
<<<<<<< HEAD
        ('Metadata', {
            'fields': ('start_position', 'end_position', 'word_count')
        }),
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def book_title(self, obj):
        """Display the book title"""
        # Access the related object via 'obj.book'
        return obj.book.title
    book_title.short_description = "Book"
    # To make this column sortable in the admin, you can add this line:
    book_title.admin_order_field = 'book__title'

    def get_preview(self, obj):
        """Display a preview of the chunk text"""
        # This assumes your Chunk model has a method called get_preview()
        return obj.get_preview(50)
    get_preview.short_description = "Preview"