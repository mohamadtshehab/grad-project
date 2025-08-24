# Character API Documentation

## Endpoints

### Get Character Relationships

**Endpoint:** `GET /api/characters/{character_id}/relationships/`

**Description:** Retrieves a simplified list of character names and relationship types for characters that have relationships with the specified character.

**Parameters:**
- `character_id` (UUID): The unique identifier of the character

**Response Format:**
```json
{
    "character_name": "Character Name",
    "relationships": [
        {
            "character_name": "Other Character Name",
            "character_id": "uuid-string",
            "relationship_type": "friends"
        }
    ],
    "total_relationships": 1
}
```

**Example Request:**
```bash
GET /api/characters/550e8400-e29b-41d4-a716-446655440000/relationships/
```

**Example Response:**
```json
{
    "character_name": "Alice",
    "relationships": [
        {
            "character_name": "Bob",
            "character_id": "550e8400-e29b-41d4-a716-446655440001",
            "relationship_type": "friends"
        },
        {
            "character_name": "Charlie",
            "character_id": "550e8400-e29b-41d4-a716-446655440002",
            "relationship_type": "family"
        }
    ],
    "total_relationships": 2
}
```

**Error Responses:**

**404 Not Found:**
```json
{
    "error": "Character not found",
    "details": "No character found with ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Failed to retrieve character relationships",
    "details": "Error details here"
}
```

## Notes

- The endpoint returns a simplified list of relationships for the specified character
- Each relationship contains the other character's name, ID, and the relationship type
- Relationships are ordered by creation date (oldest first)
- The `character_name` field shows the name of the character being queried
- The `total_relationships` field provides a count of all relationships for the character
- The response is optimized for simple relationship queries while providing essential character identification
