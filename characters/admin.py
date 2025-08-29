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
<<<<<<< HEAD
    readonly_fields = ['character_id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('character_id', 'book', 'profile')
=======
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'book', 'profile')
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
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
<<<<<<< HEAD
    list_display = ['get_character_name', 'get_chunk_number', 'mention_count', 'created_at']
    list_filter = ['chunk__book', 'mention_count', 'created_at'] # Use 'chunk__' not 'chunk_id__'
=======
    list_display = ['get_character_name', 'get_chunk_number', 'created_at']
    list_filter = ['chunk__book', 'created_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    search_fields = ['character__profile__name', 'chunk__chunk_number'] # Corrected field names
    ordering = ['chunk', 'character'] # Use actual field names
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
<<<<<<< HEAD
            'fields': ('chunk', 'character', 'mention_count', 'position_info') # Corrected field names
=======
            'fields': ('chunk', 'character') # Corrected field names
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
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

<<<<<<< HEAD
    list_display = ['get_character_1_name', 'relationship_type', 'get_character_2_name', 'book', 'created_at']
    list_filter = ['relationship_type', 'book', 'created_at']
=======
    list_display = ['get_character_1_name', 'relationship_type', 'get_character_2_name', 'chunk', 'created_at']
    list_filter = ['relationship_type', 'chunk', 'created_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    # Corrected search_fields to use the proper model field names
    search_fields = [
        'from_character__profile__name',
        'to_character__profile__name',
<<<<<<< HEAD
        'description'
    ]
    ordering = ['book', 'from_character', 'to_character']
=======
    ]
    ordering = ['chunk', 'from_character', 'to_character']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
<<<<<<< HEAD
            'fields': ('from_character', 'to_character', 'relationship_type', 'description', 'book')
=======
            'fields': ('from_character', 'to_character', 'relationship_type', 'desciption', 'chunk')
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
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