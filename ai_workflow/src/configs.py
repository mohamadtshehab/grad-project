GRAPH_CONFIG = {"configurable": {"thread_id": 1}, 'recursion_limit': 1000}
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