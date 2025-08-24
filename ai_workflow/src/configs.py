"""
Configuration constants and settings for the AI workflow.
Centralizes all configuration values and thresholds.
"""

# Similarity matching thresholds
SIMILARITY_THRESHOLD = 0.9
EMBEDDING_CACHE_SIZE = 1000

# Text processing settings
CHUNK_CONTEXT_RATIO = 3  # Use 1/3 of text for context
SUMMARY_CONTEXT_RATIO = 3  # Use 2/3 of summary for context

# Database operation settings
BULK_QUERY_CHUNK_SIZE = 100
MAX_RELATIONSHIP_BATCH_SIZE = 50

# AI service settings
COHERE_MODEL = "small"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Character name normalization
HONORIFICS_PATTERN = (
    r"^(?:ال)?(?:(?:شيخ)|(?:السيد)|(?:سيد)|(?:معلم)|(?:الحاج)|(?:الحاجة)|"
    r"(?:الدكتور)|(?:دكتور)|(?:د\.)|(?:الأستاذ)|(?:الاستاذ)|(?:استاذ))\s+"
)

# Profile validation settings
REQUIRED_PROFILE_FIELDS = ['name']
MIN_VALIDATION_SCORE = 0.5

# Workflow settings
MAX_CHUNKS_PER_BATCH = 10
PROGRESS_CALLBACK_INTERVAL = 1  # Send progress every N chunks

# Django settings
DEFAULT_DJANGO_SETTINGS = 'graduation_backend.settings'

# Graph configuration
GRAPH_CONFIG = {"configurable": {"thread_id": 1}, 'recursion_limit': 100000}

# Fuzzy matching configuration
FUZZY_MATCHING_CONFIG = {
    'similarity_thresholds': {
        'high_confidence': 0.85,      # Automatic merge threshold
        'medium_confidence': 0.75,    # Review flag threshold
        'low_confidence': 0.65,       # Minimum consideration threshold
    },
    'weights': {
        'name_similarity': 0.7,       # Weight for name matching
    },
    'default_threshold': 0.85         # Default threshold for profile_retriever_creator
}

# Chunking configuration
CHUNKING_CONFIG = {
    'chunk_size': 8000,
    'chunk_overlap': 200
}

# Metadata removal configuration
METADATA_REMOVAL_CONFIG = {
    'search_window_size': 2000,
    'max_metadata_line_length': 80,
    'metadata_keywords': [
        'نشر', 'ترجمة', 'شركة', 'صحافة', 'طباعة', 'توزيع', 'موافقة', 
        'ناشر', 'غلاف', 'تأليف', 'مركز', 'دار', 'حقوق', 'محفوظة', 
        'كاتب', 'أديب', 'مؤلف', 'رقم', 'تاريخ', 'رواية', 'كتاب', 
        'نسخة', 'غلاف', 'قانون', 'شركة', 'مترجم', 'طبعة', 'تحرير', 
        'محرر', 'إهداء', 'فاكس'
    ],
    'start_keywords':['فصل', 'أول', 'جزء']
}
