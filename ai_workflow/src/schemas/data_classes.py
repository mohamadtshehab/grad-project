from dataclasses import dataclass ,field
from typing import List, Optional

@dataclass
class Profile:
    id: str
    name: str
    hint: Optional[str] = None
    age: Optional[str] = None
    role: Optional[str] = None
    physical_characteristics: List[str] = field(default_factory=list)
    personality: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    
@dataclass
class LastAppearingCharacter:
    name: str
    hint: str

@dataclass
class TextQualityAssessment:
    quality_score: float
    quality_level: str
    issues: list[str]
    suggestions: list[str]
    reasoning: str
    
@dataclass
class TextClassification:
    is_literary: bool
    classification: str
    confidence: float
    reasoning: str
    literary_features: list[str]
    non_literary_features: list[str]

@dataclass
class EmptyProfileValidation :
    has_empty_profiles: bool 
    empty_profiles: list[str]
    suggestions: list[str] 
    profiles: list[Profile]
    validation_score: float 
