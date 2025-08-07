import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any


class CharacterDatabase:
    """
    SQLite database for storing character profiles in a NoSQL-like setup.
    Uses JSON storage for flexible document structure.
    """
    
    def __init__(self, db_path: str = "characters.sqlite"):
        """
        Initialize the character database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with the required table structure."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,    -- A unique ID we generate (e.g., a UUID)
                    name TEXT NOT NULL,               -- The character's common name (e.g., "Ali")
                    profile_json TEXT                 -- JSON document containing the character profile (including hint)
                );
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);")
            
            conn.commit()
    
    def insert_character(self, name: str, profile: Dict[str, Any], ) -> str:
        """
        Insert a new character profile into the database.
        
        Args:
            name: Character's name
            profile: Character profile as a dictionary
            
        Returns:
            The generated id
        """
        id = str(uuid.uuid4())
        
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO characters (id, name, profile_json)
                VALUES (?, ?, ?)
            """, (id, name, json.dumps(profile, ensure_ascii=False)))
            conn.commit()
        
        return id
    
    def update_character(self, id: str, profile: Dict[str, Any]) -> bool:
        """
        Update an existing character profile.
        
        Args:
            id: The character's unique ID
            profile: Updated character profile
            
        Returns:
            True if update was successful, False if character not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE characters 
                SET profile_json = ?
                WHERE id = ?
            """, (json.dumps(profile, ensure_ascii=False), id))
            
            conn.commit()
            return cursor.rowcount > 0
    


    def get_character(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a character profile by ID.
        
        Args:
            id: The character's unique ID
            
        Returns:
            Character profile as dictionary, or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, profile_json
                FROM characters
                WHERE id = ?
            """, (id,))
            
            row = cursor.fetchone()
            if row:
                name, profile_json = row
                profile = json.loads(profile_json)
                return {
                    'id': id,
                    'name': name,
                    'profile': profile
                }
            return None
    
    def find_characters_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Find characters by name (handles multiple characters with same name).
        
        Args:
            name: Character name to search for
            
        Returns:
            List of character profiles
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, profile_json
                FROM characters
                WHERE name LIKE ?
            """, (f'%{name}%',))
            
            characters = []
            for row in cursor.fetchall():
                id, name, profile_json = row
                profile = json.loads(profile_json)
                characters.append({
                    'id': id,
                    'name': name,
                    'profile': profile
                })
            
            return characters
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """
        Retrieve all character profiles.
        
        Returns:
            List of all character profiles
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, profile_json
                FROM characters
                ORDER BY name
            """)
            
            characters = []
            for row in cursor.fetchall():
                id, name, profile_json = row
                profile = json.loads(profile_json)
                characters.append({
                    'id': id,
                    'name': name,
                    'profile': profile
                })
            
            return characters
    
    def delete_character(self, id: str) -> bool:
        """
        Delete a character profile.
        
        Args:
            id: The character's unique ID
            
        Returns:
            True if deletion was successful, False if character not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_characters(self, query: str) -> List[Dict[str, Any]]:
        """
        Search characters by name or hint in profile.
        
        Args:
            query: Search query
            
        Returns:
            List of matching character profiles
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, profile_json
                FROM characters
                WHERE name LIKE ? OR JSON_EXTRACT(profile_json, '$.hint') LIKE ?
                ORDER BY name
            """, (f'%{query}%', f'%{query}%'))
            
            characters = []
            for row in cursor.fetchall():
                id, name, profile_json = row
                profile = json.loads(profile_json)
                characters.append({
                    'id': id,
                    'name': name,
                    'profile': profile
                })
            
            return characters
    
    def get_character_count(self) -> int:
        """
        Get the total number of characters in the database.
        
        Returns:
            Number of characters
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM characters")
            return cursor.fetchone()[0]
    
    def clear_database(self):
        """Clear all character data from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters")
            conn.commit()


# Global database instance
character_db = CharacterDatabase()


def get_character_db() -> CharacterDatabase:
    """Get the global character database instance."""
    return character_db 