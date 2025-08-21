GRAPH_CONFIG = {"configurable": {"thread_id": 1}, 'recursion_limit': 100000}
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

CHUNKING_CONFIG = {
    'chunk_size': 12000,
    'chunk_overlap': 200
}

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