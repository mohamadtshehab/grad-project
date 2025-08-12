from django.contrib import admin
from .models import Character, ChunkCharacter, CharacterRelationship


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    """Admin configuration for Character model"""
    
    list_display = ['name', 'role', 'book_id', 'created_at']
    list_filter = ['book_id', 'created_at']
    search_fields = ['character_data__name', 'character_data__role']
    ordering = ['book_id', 'character_data__name']
    readonly_fields = ['character_id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('character_id', 'book_id', 'character_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChunkCharacter)
class ChunkCharacterAdmin(admin.ModelAdmin):
    """Admin configuration for ChunkCharacter model"""
    
    list_display = ['character_name', 'chunk_number', 'mention_count', 'created_at']
    list_filter = ['chunk_id__book_id', 'mention_count', 'created_at']
    search_fields = ['character_id__character_data__name', 'chunk_id__chunk_number']
    ordering = ['chunk_id', 'character_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('chunk_id', 'character_id', 'mention_count', 'position_info')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(admin.ModelAdmin):
    """Admin configuration for CharacterRelationship model"""
    
    list_display = ['character_1_name', 'relationship_type', 'character_2_name', 'book_id', 'created_at']
    list_filter = ['relationship_type', 'book_id', 'created_at']
    search_fields = [
        'character_id_1__character_data__name', 
        'character_id_2__character_data__name',
        'description'
    ]
    ordering = ['book_id', 'character_id_1', 'character_id_2']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('character_id_1', 'character_id_2', 'relationship_type', 'description', 'book_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
