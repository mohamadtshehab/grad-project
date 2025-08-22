from ai_workflow.src.language_models.prompts import *
from ai_workflow.src.language_models.llms import *

book_name_extraction_chain = book_name_extraction_prompt | book_name_extraction_llm
profile_difference_chain = profile_difference_prompt | profile_difference_llm
name_query_chain = name_query_prompt | name_query_llm
summary_chain = summary_prompt | summary_llm
text_quality_assessment_chain = text_quality_assessment_prompt | text_quality_assessment_llm
text_classification_chain = text_classification_prompt | text_classification_llm
empty_profile_validation_chain = empty_profile_validation_prompt | empty_profile_validation_llm
