import pandas as pd
import os
from langchain.tools import BaseTool
from typing import Optional

class CharacterRoleTool(BaseTool):
    name: str = "character_role_classifier"
    description: str = """
    Classifies character roles based on character descriptions and personality traits.
    Provides access to a comprehensive list of character role definitions and examples.
    Use this tool when you need to determine the most appropriate character role for a given character description.
    """
    
    def _run(self, character_description: str = "", personality: str = "", 
             events: str = "", relationships: str = "") -> str:
        """
        Get character role definitions and classify a character's role.
        
        Args:
            character_description: General description of the character
            personality: Personality traits of the character
            events: Events involving the character (comma-separated)
            relationships: Relationships with other characters (comma-separated)
            
        Returns:
            Formatted string with available roles and classification result
        """
        # Load character terms
        csv_path = "resources/character_data/character_terms_arabic.csv"
        if not os.path.exists(csv_path):
            return "Error: Character terms file not found"
        
        df = pd.read_csv(csv_path)
        
        # Format the CSV data for the LLM
        role_definitions = []
        for idx, row in df.iterrows():
            if 'الكلمة' in df.columns:  # Arabic
                word = row['الكلمة']
                meaning = row['المعنى']
                examples = row['الأمثلة'] if pd.notna(row['الأمثلة']) else ""
            else:  # English
                word = row['Word']
                meaning = row['Meaning']
                examples = row['Examples'] if pd.notna(row['Examples']) else ""
            
            role_def = f"Role: {word}\nDescription: {meaning}"
            if examples:
                role_def += f"\nExamples: {examples}"
            role_definitions.append(role_def)
        
        # Format the output
        output = "AVAILABLE CHARACTER ROLES:\n"
        output += "=" * 50 + "\n\n"
        
        for i, role_def in enumerate(role_definitions, 1):
            output += f"{i}. {role_def}\n\n"
        
        # If character information is provided, also include classification
        if character_description or personality:
            output += "\nCHARACTER TO CLASSIFY:\n"
            output += "=" * 30 + "\n"
            output += f"Description: {character_description}\n"
            output += f"Personality: {personality}\n"
            if events:
                output += f"Events: {events}\n"
            if relationships:
                output += f"Relationships: {relationships}\n"
            output += "\nPlease analyze the character information above and select the most appropriate role from the available options."
        
        return output
    
    def _arun(self, character_description: str = "", personality: str = "", 
              events: str = "", relationships: str = "") -> str:
        """Async version of the tool."""
        return self._run(character_description, personality, events, relationships)

# Create the tool instance
character_role_tool = CharacterRoleTool() 