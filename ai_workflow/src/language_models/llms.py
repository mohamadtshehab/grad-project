from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
    
)
from ai_workflow.src.schemas.output_structures import NameQuerier, ProfileRefresher, Summary, BookNameExtractor, TextQualityAssessment, TextClassification, ProfileValidation
from ai_workflow.src.language_models.tools import character_role_tool
from dotenv import load_dotenv

load_dotenv()

model = 'gemini-2.5-flash'

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_TOXICITY: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY: HarmBlockThreshold.OFF,
}

profile_update_llm = ChatGoogleGenerativeAI(model=model, 
                                            temperature=0.0, 
                                            safety_settings=safety_settings,
                                            ).bind_tools([character_role_tool]).with_structured_output(ProfileRefresher)

name_query_llm = ChatGoogleGenerativeAI(model=model, 
                                        temperature=0.0,
                                        safety_settings=safety_settings,
                                        ).with_structured_output(NameQuerier)

summary_llm = ChatGoogleGenerativeAI(model=model,
                                     temperature=1.0, 
                                     safety_settings=safety_settings,
                                     ).with_structured_output(Summary)

book_name_extraction_llm = ChatGoogleGenerativeAI(model=model,
                                                  temperature=0.0,
                                                  safety_settings=safety_settings,
                                                  ).with_structured_output(BookNameExtractor)

text_quality_assessment_llm = ChatGoogleGenerativeAI(model=model,
                                                     temperature=0.0,
                                                     safety_settings=safety_settings,
                                                     ).with_structured_output(TextQualityAssessment)

text_classification_llm = ChatGoogleGenerativeAI(model=model,
                                                temperature=0.0,
                                                safety_settings=safety_settings,
                                                ).with_structured_output(TextClassification)