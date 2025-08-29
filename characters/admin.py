# characters/admin.py

from django.contrib import admin
from .models import Character, ChunkCharacter, CharacterRelationship


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    """Admin configuration for Character model"""

    # Use custom methods to display data from the 'profile' JSONField
    list_display = ['get_name', 'get_role', 'book', 'created_at']
    list_filter = ['book', 'created_at']
    search_fields = ['profile__name', 'profile__role']
    ordering = ['book', 'profile__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'book', 'profile')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Method to get the character's name from the JSONField
    def get_name(self, obj):
        return obj.profile.get('name', 'N/A')
    get_name.short_description = 'Name'
    get_name.admin_order_field = 'profile__name' # Allows sorting

    # Method to get the character's role from the JSONField
    def get_role(self, obj):
        return obj.profile.get('role', 'N/A')
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role' # Allows sorting


@admin.register(ChunkCharacter)
class ChunkCharacterAdmin(admin.ModelAdmin):
    """Admin configuration for ChunkCharacter model"""

    # Use custom methods to display data from related models
    list_display = ['get_character_name', 'get_chunk_number', 'created_at']
    list_filter = ['chunk__book', 'created_at']
    search_fields = ['character__profile__name', 'chunk__chunk_number'] # Corrected field names
    ordering = ['chunk', 'character'] # Use actual field names
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('chunk', 'character') # Corrected field names
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Method to follow the foreign key to the Character model
    def get_character_name(self, obj):
        return obj.character.profile.get('name', 'N/A')
    get_character_name.short_description = 'Character'
    get_character_name.admin_order_field = 'character__profile__name'

    # Method to follow the foreign key to the Chunk model
    def get_chunk_number(self, obj):
        return obj.chunk.chunk_number
    get_chunk_number.short_description = 'Chunk Number'
    get_chunk_number.admin_order_field = 'chunk__chunk_number'


@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(admin.ModelAdmin):
    """Admin configuration for CharacterRelationship model"""

    list_display = ['get_character_1_name', 'relationship_type', 'get_character_2_name', 'chunk', 'created_at']
    list_filter = ['relationship_type', 'chunk', 'created_at']
    # Corrected search_fields to use the proper model field names
    search_fields = [
        'from_character__profile__name',
        'to_character__profile__name',
    ]
    ordering = ['chunk', 'from_character', 'to_character']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('from_character', 'to_character', 'relationship_type', 'desciption', 'chunk')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Method to get the first character's name
    def get_character_1_name(self, obj):
        return obj.from_character.profile.get('name', 'N/A')
    get_character_1_name.short_description = 'Character 1'
    get_character_1_name.admin_order_field = 'from_character__profile__name'

    # Method to get the second character's name
    def get_character_2_name(self, obj):
        return obj.to_character.profile.get('name', 'N/A')
    get_character_2_name.short_description = 'Character 2'
    get_character_2_name.admin_order_field = 'to_character__profile__name'