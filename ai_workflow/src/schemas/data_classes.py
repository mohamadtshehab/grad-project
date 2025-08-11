from dataclasses import dataclass


@dataclass
class Profile:
    name: str
    hint: str
    age: str
    role: str
    physical_characteristics: list[str]
    personality: str
    events: list[str]
    relationships: list[str]
    aliases: list[str]
    id: str
    
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
