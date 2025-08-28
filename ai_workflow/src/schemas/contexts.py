from typing import TypedDict, Optional, Any, Callable

class Context(TypedDict):
    progress_callback: Optional[Callable]
    
