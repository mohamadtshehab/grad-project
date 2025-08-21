# 🎓 System Architecture - AI-Powered Book Analysis Platform

## Table of Contents
- [Overview](#overview)
- [High-Level Architecture](#high-level-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [AI Workflow Engine](#ai-workflow-engine)
- [Database Design](#database-design)
- [API Architecture](#api-architecture)
- [Security & Infrastructure](#security--infrastructure)
- [Asynchronous Processing](#asynchronous-processing)
- [Data Flow](#data-flow)
- [Deployment Architecture](#deployment-architecture)
- [Technical Specifications](#technical-specifications)

---

## Overview

This system is a **sophisticated AI-powered book analysis platform** that processes EPUB files to extract and analyze character information using advanced natural language processing. The platform features a Django REST API backend with real-time processing capabilities, integrated with a LangGraph-based AI workflow engine for intelligent character extraction and analysis.

### Key Features
- 🔐 **JWT-based Authentication** with bilingual support (English/Arabic)
- 📚 **EPUB Book Processing** with automatic text extraction
- 🤖 **AI Character Analysis** using Google Gemini and LangGraph
- ⚡ **Real-time Processing** with WebSocket notifications
- 🔄 **Background Task Processing** via Celery
- 🌐 **RESTful API** with comprehensive endpoints
- 📊 **Character Relationship Mapping** with flexible JSON storage
- 🛡️ **Enterprise-grade Security** with rate limiting and validation

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   React/Vue     │  │   WebSocket     │  │     File Upload             │  │
│  │   Components    │  │   Client        │  │     Interface               │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ HTTPS/WSS
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                            API GATEWAY LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   Django REST   │  │   WebSocket     │  │     Static/Media            │  │
│  │   Framework     │  │   Routing       │  │     File Serving            │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                          BUSINESS LOGIC LAYER                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │    User     │ │    Book     │ │ Character   │ │    AI Workflow          │ │
│  │ Management  │ │ Processing  │ │ Analysis    │ │    Engine               │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                           DATA LAYER                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   SQLite    │ │    Redis    │ │   Celery    │ │     File Storage        │ │
│  │  Database   │ │ Cache/Queue │ │ Task Queue  │ │     (Media Files)       │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### System Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React/Vue.js | User interface and interaction |
| **API Gateway** | Django + DRF | REST API and WebSocket routing |
| **Authentication** | JWT + Django Auth | User management and security |
| **AI Engine** | LangGraph + Gemini | Character extraction and analysis |
| **Task Queue** | Celery + Redis | Background processing |
| **Database** | SQLite | Data persistence |
| **File Storage** | Django FileField | EPUB and text file management |
| **Real-time** | Django Channels | WebSocket notifications |

---

## Frontend Architecture

### Technology Stack
```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND STACK                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   React/    │ │    Axios    │ │     WebSocket           │ │
│  │   Vue.js    │ │   HTTP      │ │     Client              │ │
│  │             │ │   Client    │ │                         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Redux/    │ │  Material   │ │     File Upload         │ │
│  │   Zustand   │ │    UI/      │ │     Components          │ │
│  │             │ │  Ant Design │ │                         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Frontend Application Structure
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   └── PasswordReset.jsx
│   ├── books/
│   │   ├── BookUpload.jsx
│   │   ├── BookList.jsx
│   │   ├── BookDetails.jsx
│   │   └── ProcessingStatus.jsx
│   ├── characters/
│   │   ├── CharacterList.jsx
│   │   ├── CharacterProfile.jsx
│   │   └── RelationshipGraph.jsx
│   └── common/
│       ├── Layout.jsx
│       ├── Notifications.jsx
│       └── ProgressBar.jsx
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── websocket.js
│   └── fileUpload.js
├── store/
│   ├── authSlice.js
│   ├── booksSlice.js
│   └── charactersSlice.js
└── utils/
    ├── constants.js
    ├── helpers.js
    └── validators.js
```

### Key Frontend Features

#### 1. Authentication Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Login     │───▶│  JWT Token  │───▶│ Authorized  │
│   Form      │    │  Storage    │    │  Requests   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Validation  │    │   Refresh   │    │   Logout    │
│   Errors    │    │   Token     │    │ & Cleanup   │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### 2. File Upload Process
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  File Drop  │───▶│ Validation  │───▶│   Upload    │───▶│ Processing  │
│   Zone      │    │ (EPUB only) │    │ Progress    │    │   Status    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Preview   │    │   Error     │    │ WebSocket   │    │ Character   │
│   Display   │    │  Messages   │    │   Updates   │    │  Results    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### 3. Real-time Notifications
```javascript
// WebSocket Integration Example
const useWebSocket = (userId) => {
  const [socket, setSocket] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/notifications/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleNotification(data);
    };
    
    setSocket(ws);
    return () => ws.close();
  }, [userId]);

  const handleNotification = (data) => {
    switch(data.event) {
      case 'processing_started':
        showProgress(data.job_id);
        break;
      case 'validation_completed':
        updateValidationStatus(data.results);
        break;
      case 'characters_extracted':
        refreshCharacterList();
        break;
    }
  };
};
```

---

## Backend Architecture

### Django Application Structure
```
graduation_backend/
├── authentication/      # JWT-based authentication system
│   ├── models.py       # PasswordResetCode model
│   ├── views.py        # Auth endpoints (login, register, etc.)
│   ├── serializers.py  # Request/response serialization
│   ├── tasks.py        # Email sending tasks
│   └── permissions.py  # Custom permissions
├── user/               # Custom user management
│   ├── models.py       # Custom User model with UUID
│   └── admin.py        # Admin interface customization
├── books/              # EPUB book processing
│   ├── models.py       # Book model with file handling
│   ├── views.py        # Book CRUD operations
│   ├── serializers.py  # Book data serialization
│   ├── tasks_workflow.py # Celery AI workflow tasks
│   └── signals.py      # Post-save signal handlers
├── chunks/             # Text chunk management
│   ├── models.py       # Chunk model with positioning
│   ├── views.py        # Chunk API endpoints
│   └── serializers.py  # Chunk serialization
├── characters/         # AI-extracted characters
│   ├── models.py       # Character, ChunkCharacter, Relationships
│   └── admin.py        # Character admin interface
├── ai_workflow/        # LangGraph AI processing engine
│   ├── src/
│   │   ├── graphs/     # LangGraph workflow definitions
│   │   ├── language_models/ # LLM integrations
│   │   ├── preprocessors/   # Text processing utilities
│   │   ├── databases/       # Django ORM adapter
│   │   └── schemas/         # State and output structures
│   └── management/     # Django management commands
└── utils/              # Shared utilities
    ├── models.py       # Job tracking, TimeStampedModel
    ├── consumers.py    # WebSocket consumers
    ├── exception_handler.py # Global exception handling
    └── views.py        # Utility endpoints
```

### Core Models and Relationships

```sql
-- User Management
┌─────────────────┐
│      User       │
│─────────────────│
│ id (UUID) PK    │
│ name            │
│ email (unique)  │
│ password_hash   │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐    ┌─────────────────┐
│      Book       │    │      Job        │
│─────────────────│    │─────────────────│
│ book_id (UUID)  │    │ id (UUID) PK    │
│ title           │    │ user_id FK      │
│ author          │    │ job_type        │
│ file            │    │ status          │
│ txt_file        │    │ progress        │
│ language        │    │ result (JSON)   │
│ quality_score   │    │ error           │
│ processing_status│    │ started_at      │
│ user_id FK      │    │ finished_at     │
└─────────────────┘    └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│     Chunk       │
│─────────────────│
│ chunk_id (UUID) │
│ chunk_text      │
│ chunk_number    │
│ book_id FK      │
│ start_position  │
│ end_position    │
│ word_count      │
└─────────────────┘
         │
         │ N:M
         ▼
┌─────────────────┐    ┌─────────────────┐
│ ChunkCharacter  │    │   Character     │
│─────────────────│    │─────────────────│
│ chunk_id FK     │    │ character_id    │
│ character_id FK │    │ character_data  │
│ mention_count   │    │ (JSON)          │
│ position_info   │    │ book_id FK      │
│ (JSON)          │    │ created_at      │
└─────────────────┘    │ updated_at      │
                       └─────────────────┘
                                │
                                │ N:M (self)
                                ▼
                       ┌─────────────────┐
                       │CharacterRelation│
                       │─────────────────│
                       │ character_1 FK  │
                       │ character_2 FK  │
                       │ relationship_type│
                       │ description     │
                       │ book_id FK      │
                       └─────────────────┘
```

### Django Apps Deep Dive

#### 1. Authentication System (`authentication/`)

**Models:**
```python
class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)  # 6-digit code
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
```

**Key Features:**
- JWT token management with blacklisting
- Email-based password reset with 6-digit codes
- Bilingual response messages (English/Arabic)
- Rate limiting for security
- Celery integration for email sending

**API Endpoints:**
```
POST /api/auth/register/         # User registration
POST /api/auth/login/           # JWT login
POST /api/auth/logout/          # Token blacklisting
GET  /api/auth/profile/         # Get user profile
PUT  /api/auth/profile/         # Update profile
POST /api/auth/password/change/ # Change password
POST /api/auth/password/reset/  # Request reset code
POST /api/auth/password/confirm/# Confirm reset with code
DELETE /api/auth/account/       # Delete account
```

#### 2. Book Management (`books/`)

**Book Model Features:**
```python
class Book(models.Model):
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    # AI Analysis Results
    detected_language = models.CharField(max_length=10, null=True, blank=True)
    language_confidence = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    text_classification = models.JSONField(null=True, blank=True)
    
    # File Management
    file = models.FileField(upload_to=book_upload_path, validators=[validate_book_file])
    txt_file = models.FileField(upload_to=book_upload_path, null=True, blank=True)
    
    # Processing Status
    processing_status = models.CharField(max_length=20, choices=[...], default='pending')
    processing_error = models.TextField(null=True, blank=True)
    
    # Relationships
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
```

**Automatic Text Conversion:**
```python
def epub_to_raw_html_string(epub_path):
    """Extract raw HTML content from EPUB file"""
    book = epub.read_epub(epub_path)
    html_parts = []
    
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content_bytes = item.get_content()
        content_string = content_bytes.decode('utf-8', errors='ignore')
        html_parts.append(content_string)
    
    return "\n\n\n\n".join(html_parts)
```

#### 3. Character Management (`characters/`)

**Flexible Character Data Structure:**
```python
class Character(models.Model):
    character_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character_data = models.JSONField(encoder=UnicodeJSONEncoder)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    # Character data JSON structure:
    # {
    #   "name": "Character Name",
    #   "age": "Age description", 
    #   "role": "main/secondary/minor",
    #   "physical_characteristics": {...},
    #   "personality": {...},
    #   "events": [...],
    #   "relationships": [...],
    #   "aliases": [...]
    # }
```

**Character-Chunk Relationships:**
```python
class ChunkCharacter(models.Model):
    chunk_id = models.ForeignKey(Chunk, on_delete=models.CASCADE)
    character_id = models.ForeignKey(Character, on_delete=models.CASCADE)
    mention_count = models.PositiveIntegerField(default=1)
    position_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        unique_together = ['chunk_id', 'character_id']
```

**Character Relationships:**
```python
class CharacterRelationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('family', 'Family'), ('friend', 'Friend'), ('enemy', 'Enemy'),
        ('romantic', 'Romantic'), ('colleague', 'Colleague'),
        ('mentor', 'Mentor'), ('student', 'Student'),
        ('ally', 'Ally'), ('rival', 'Rival'), ('other', 'Other'),
    ]
    
    character_id_1 = models.ForeignKey(Character, related_name='relationships_as_character_1')
    character_id_2 = models.ForeignKey(Character, related_name='relationships_as_character_2')
    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
```

---

## AI Workflow Engine

### LangGraph Architecture

The AI Workflow Engine uses **LangGraph** to create a sophisticated multi-stage processing pipeline for character extraction and analysis.

```
                        ┌─────────────────────────────────────┐
                        │         ORCHESTRATOR GRAPH          │
                        └─────────────────┬───────────────────┘
                                          │
                        ┌─────────────────▼───────────────────┐
                        │            VALIDATOR                │
                        │ ┌─────────────────────────────────┐ │
                        │ │  language_checker              │ │
                        │ │         ▼                      │ │
                        │ │  text_quality_assessor         │ │
                        │ │         ▼                      │ │
                        │ │  text_classifier               │ │
                        │ └─────────────────────────────────┘ │
                        └─────────────────┬───────────────────┘
                                          │
                        ┌─────────────────▼───────────────────┐
                        │         NAME_EXTRACTOR              │
                        │  Extract book title/metadata        │
                        └─────────────────┬───────────────────┘
                                          │
                        ┌─────────────────▼───────────────────┐
                        │          PREPROCESSOR               │
                        │ ┌─────────────────────────────────┐ │
                        │ │  chunker                       │ │
                        │ │    ▼                           │ │
                        │ │  cleaner                       │ │
                        │ │    ▼                           │ │
                        │ │  metadata_remover              │ │
                        │ └─────────────────────────────────┘ │
                        └─────────────────┬───────────────────┘
                                          │
                        ┌─────────────────▼───────────────────┐
                        │            ANALYST                  │
                        │ ┌─────────────────────────────────┐ │
                        │ │  first_name_querier ◄──────────┐│ │
                        │ │         ▼                      ││ │
                        │ │  summarizer                    ││ │
                        │ │         ▼                      ││ │
                        │ │  second_name_querier           ││ │
                        │ │         ▼                      ││ │
                        │ │  profile_retriever_creator     ││ │
                        │ │         ▼                      ││ │
                        │ │  profile_refresher             ││ │
                        │ │         ▼                      ││ │
                        │ │  chunk_updater ────────────────┘│ │
                        │ └─────────────────────────────────┘ │
                        └─────────────────────────────────────┘
```

### State Management

**Global State Structure:**
```python
class State(TypedDict):
    # Character Analysis
    last_profiles: list[Character] | None
    last_appearing_names: list[str] | None
    
    # Context
    book_id: Optional[str]
    
    # Processing Control
    no_more_chunks: bool
    chunk_num: int
    num_of_chunks: int
    
    # Content Processing
    last_summary: str
    clean_chunks: list[str]
    
    # Validation
    validation_passed: bool
    
    # Progress Tracking
    progress_callback: Optional[Callable]
```

### AI Model Integration

**Language Models Configuration:**
```python
# Google Gemini 2.5 Flash Integration
model = 'gemini-2.5-flash'

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
    # ... comprehensive safety configuration
}

# Specialized LLM Instances
profile_difference_llm = ChatGoogleGenerativeAI(
    model=model, 
    temperature=0.0, 
    safety_settings=safety_settings
).bind_tools([character_role_tool]).with_structured_output(CharacterList)

name_query_llm = ChatGoogleGenerativeAI(
    model=model, 
    temperature=0.0,
    safety_settings=safety_settings
).with_structured_output(NameList)

summary_llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0.0,
    safety_settings=safety_settings
).with_structured_output(Summary)
```

### Workflow Subgraphs

#### 1. Validator Subgraph
```python
# Validation Pipeline
graph.add_node("language_checker", language_checker)
graph.add_node('text_quality_assessor', text_quality_assessor)
graph.add_node('text_classifier', text_classifier)

# Conditional routing based on validation results
graph.add_conditional_edges('language_checker', 
    router_from_language_checker_to_text_quality_assessor_or_end, {
        'text_quality_assessor': 'text_quality_assessor',
        'END': END
    })
```

**Validation Functions:**
- **Language Detection**: Identifies Arabic text with confidence scoring
- **Quality Assessment**: Evaluates text quality on a 0.0-1.0 scale
- **Text Classification**: Determines if content is literary fiction

#### 2. Preprocessor Subgraph
```python
# Text Processing Pipeline
graph.add_node('chunker', chunker)
graph.add_node('cleaner', cleaner)
graph.add_node('metadata_remover', metadata_remover)

# Linear processing flow
graph.add_edge('chunker', 'cleaner')
graph.add_edge('cleaner', 'metadata_remover')
```

**Processing Functions:**
- **Chunker**: Intelligent text segmentation with position tracking
- **Cleaner**: HTML tag removal and text normalization
- **Metadata Remover**: Strip unnecessary metadata and formatting

#### 3. Analyst Subgraph
```python
# Complex character analysis workflow
graph.add_node('first_name_querier', first_name_querier)
graph.add_node('second_name_querier', second_name_querier)
graph.add_node('profile_retriever_creator', profile_retriever_creator)
graph.add_node('profile_refresher', profile_refresher)
graph.add_node('chunk_updater', chunk_updater)
graph.add_node('summarizer', summarizer)

# Conditional routing with feedback loops
graph.add_conditional_edges('chunk_updater', 
    router_from_chunker_to_first_name_querier_or_end, {
        'first_name_querier': 'first_name_querier',
        'END': END
    })

graph.add_conditional_edges('first_name_querier',
    router_from_first_name_querier_to_summarizer_or_chunk_updater, {
        'summarizer': 'summarizer',
        'chunk_updater': 'chunk_updater',
    })
```

**Analysis Functions:**
- **Name Querier**: Extract character names from text chunks
- **Summarizer**: Create contextual summaries for character analysis
- **Profile Creator**: Generate detailed character profiles
- **Profile Refresher**: Update and merge character information
- **Chunk Updater**: Process next text chunk or complete analysis

### Django ORM Integration

**Character Database Adapter:**
```python
class DjangoCharacterAdapter:
    """Adapter for Django ORM integration with AI workflow"""
    
    def __init__(self, book_id: str):
        self.book_id = book_id
        self.book = Book.objects.get(book_id=book_id)
    
    def insert_character(self, character_data: dict) -> str:
        """Insert new character into database"""
        character = Character.objects.create(
            book_id=self.book,
            character_data=character_data
        )
        return str(character.character_id)
    
    def get_character(self, character_id: str) -> dict:
        """Retrieve character by ID"""
        character = Character.objects.get(character_id=character_id)
        return character.to_dict()
    
    def find_characters_by_name(self, name: str, fuzzy: bool = True) -> list:
        """Find characters by name with fuzzy matching"""
        if fuzzy:
            # Implement fuzzy matching logic for Arabic text
            pass
        else:
            characters = Character.objects.filter(
                book_id=self.book,
                character_data__name__icontains=name
            )
        return [char.to_dict() for char in characters]
```

---

## Database Design

### SQLite Schema with Indexing Strategy

```sql
-- =====================================================
-- USER MANAGEMENT TABLES
-- =====================================================

CREATE TABLE user (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login DATETIME,
    date_joined DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_name ON user(name);

-- =====================================================
-- AUTHENTICATION TABLES
-- =====================================================

CREATE TABLE authentication_passwordresetcode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(36) NOT NULL,
    code VARCHAR(6) NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_password_reset_user ON authentication_passwordresetcode(user_id);
CREATE INDEX idx_password_reset_code ON authentication_passwordresetcode(code);
CREATE INDEX idx_password_reset_expires ON authentication_passwordresetcode(expires_at);

-- =====================================================
-- BOOK MANAGEMENT TABLES
-- =====================================================

CREATE TABLE book (
    book_id VARCHAR(36) PRIMARY KEY,      -- UUID
    title VARCHAR(255),
    author VARCHAR(255),
    description TEXT,
    
    -- AI Analysis Results
    detected_language VARCHAR(10),
    language_confidence REAL,
    quality_score REAL,
    text_classification JSON,
    
    -- File Management
    file VARCHAR(100) NOT NULL,
    txt_file VARCHAR(100),
    
    -- Processing Status
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_error TEXT,
    
    -- Metadata
    user_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_book_user ON book(user_id);
CREATE INDEX idx_book_title ON book(title);
CREATE INDEX idx_book_created ON book(created_at);
CREATE INDEX idx_book_status ON book(processing_status);
CREATE INDEX idx_book_language ON book(detected_language);

-- =====================================================
-- TEXT PROCESSING TABLES
-- =====================================================

CREATE TABLE chunk (
    chunk_id VARCHAR(36) PRIMARY KEY,     -- UUID
    chunk_text TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    
    -- Position Information
    start_position INTEGER,
    end_position INTEGER,
    word_count INTEGER,
    
    -- Relationships
    book_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE,
    UNIQUE(book_id, chunk_number)
);

CREATE INDEX idx_chunk_book ON chunk(book_id);
CREATE INDEX idx_chunk_book_number ON chunk(book_id, chunk_number);
CREATE INDEX idx_chunk_number ON chunk(chunk_number);

-- =====================================================
-- CHARACTER ANALYSIS TABLES
-- =====================================================

CREATE TABLE character (
    character_id VARCHAR(36) PRIMARY KEY, -- UUID
    character_data JSON NOT NULL,         -- Flexible character profile
    book_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE
);

CREATE INDEX idx_character_book ON character(book_id);
CREATE INDEX idx_character_created ON character(created_at);

-- Junction Table: Characters mentioned in Chunks
CREATE TABLE chunk_character (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id VARCHAR(36) NOT NULL,
    character_id VARCHAR(36) NOT NULL,
    mention_count INTEGER DEFAULT 1,
    position_info JSON,                   -- Position details within chunk
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (chunk_id) REFERENCES chunk(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES character(character_id) ON DELETE CASCADE,
    UNIQUE(chunk_id, character_id)
);

CREATE INDEX idx_chunk_character_chunk ON chunk_character(chunk_id);
CREATE INDEX idx_chunk_character_character ON chunk_character(character_id);
CREATE INDEX idx_chunk_character_both ON chunk_character(chunk_id, character_id);

-- Character Relationships
CREATE TABLE character_relationship (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id_1 VARCHAR(36) NOT NULL,
    character_id_2 VARCHAR(36) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    description TEXT,
    book_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (character_id_1) REFERENCES character(character_id) ON DELETE CASCADE,
    FOREIGN KEY (character_id_2) REFERENCES character(character_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE,
    UNIQUE(character_id_1, character_id_2, book_id)
);

CREATE INDEX idx_char_rel_char1 ON character_relationship(character_id_1);
CREATE INDEX idx_char_rel_char2 ON character_relationship(character_id_2);
CREATE INDEX idx_char_rel_book ON character_relationship(book_id);
CREATE INDEX idx_char_rel_type ON character_relationship(relationship_type);

-- =====================================================
-- SYSTEM MANAGEMENT TABLES
-- =====================================================

CREATE TABLE job (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    user_id VARCHAR(36),
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result JSON,
    error TEXT,
    started_at DATETIME,
    finished_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_job_user_type ON job(user_id, job_type);
CREATE INDEX idx_job_status_created ON job(status, created_at);
CREATE INDEX idx_job_type ON job(job_type);
```

### Data Relationships and Constraints

```
User (1) ──────────── (N) Book
 │                        │
 │                        └── (1) ──────── (N) Chunk
 │                                           │
 │                                           └── (N) ── (M) Character
 │                                                          │
 └── (1) ──────────── (N) Job                              │
                                                            │
                    Character (N) ──────── (M) Character
                        (via CharacterRelationship)
```

### JSON Schema Examples

**Character Data Structure:**
```json
{
  "name": "أحمد محمد",
  "age": "في الثلاثينات من العمر",
  "role": "main",
  "physical_characteristics": {
    "height": "طويل القامة",
    "build": "نحيف",
    "hair": "شعر أسود",
    "eyes": "عيون بنية"
  },
  "personality": {
    "traits": ["ذكي", "طموح", "صبور"],
    "strengths": ["قيادي", "حكيم"],
    "weaknesses": ["عنيد أحياناً"]
  },
  "events": [
    {
      "event": "تخرج من الجامعة",
      "chapter": 2,
      "importance": "high"
    }
  ],
  "relationships": [
    {
      "character": "فاطمة أحمد",
      "type": "family",
      "description": "أخته الكبرى"
    }
  ],
  "aliases": ["أبو محمد", "الدكتور أحمد"]
}
```

**Text Classification Result:**
```json
{
  "is_literary": true,
  "classification": "fiction",
  "confidence": 0.95,
  "genre_details": {
    "primary_genre": "drama",
    "secondary_genre": "family_saga",
    "themes": ["family", "tradition", "modern_life"]
  }
}
```

---

## API Architecture

### RESTful API Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        API ENDPOINT STRUCTURE                   │
└─────────────────────────────────────────────────────────────────┘

/api/
├── auth/                           # Authentication endpoints
│   ├── register/           POST   # User registration
│   ├── login/             POST   # JWT token obtain
│   ├── logout/            POST   # Token blacklist
│   ├── profile/           GET/PUT # User profile management
│   ├── password/
│   │   ├── change/        POST   # Change password (authenticated)
│   │   ├── reset/         POST   # Request password reset
│   │   └── confirm/       POST   # Confirm password reset
│   └── account/           DELETE # Delete user account
│
├── books/                          # Book management
│   ├── /                  GET    # List user's books
│   ├── /                  POST   # Upload new book
│   ├── {book_id}/         GET    # Get book details
│   ├── {book_id}/         PUT    # Update book metadata
│   ├── {book_id}/         DELETE # Soft delete book
│   ├── {book_id}/download/ GET   # Download original file
│   └── {book_id}/status/  GET    # Get processing status
│
├── chunks/                         # Text chunks (if exposed)
│   ├── /                  GET    # List chunks for a book
│   └── {chunk_id}/        GET    # Get specific chunk
│
├── characters/                     # Character management (if exposed)
│   ├── /                  GET    # List characters for a book
│   ├── {character_id}/    GET    # Get character details
│   └── relationships/     GET    # Get character relationships
│
└── jobs/                          # Job status tracking
    ├── /                  GET    # List user's jobs
    └── {job_id}/          GET    # Get job details
```

### API Request/Response Formats

#### Authentication

**Registration Request:**
```json
POST /api/auth/register/
{
  "name": "أحمد محمد",
  "email": "ahmed@example.com",
  "password": "SecurePassword123",
  "password_confirm": "SecurePassword123"
}
```

**Registration Response:**
```json
{
  "status": "success",
  "en": "User registered successfully",
  "ar": "تم تسجيل المستخدم بنجاح",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "أحمد محمد",
    "email": "ahmed@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Login Response:**
```json
{
  "status": "success",
  "en": "Logged in successfully",
  "ar": "تم تسجيل الدخول بنجاح",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "أحمد محمد",
      "email": "ahmed@example.com"
    }
  }
}
```

#### Book Management

**Book Upload Response:**
```json
{
  "status": "accepted",
  "en": "Book upload accepted; processing started",
  "ar": "تم قبول رفع الكتاب؛ بدأت المعالجة",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "data": {
    "book_id": "987fcdeb-51a2-43d1-9c4e-123456789abc"
  }
}
```

**Book Details Response:**
```json
{
  "status": "success",
  "en": "Book details retrieved successfully",
  "ar": "تم استرجاع تفاصيل الكتاب بنجاح",
  "data": {
    "book_id": "987fcdeb-51a2-43d1-9c4e-123456789abc",
    "title": "رواية عربية",
    "author": "كاتب مشهور",
    "description": "وصف الرواية...",
    "detected_language": "ar",
    "language_confidence": 0.98,
    "quality_score": 0.85,
    "text_classification": {
      "is_literary": true,
      "classification": "fiction",
      "confidence": 0.92
    },
    "processing_status": "completed",
    "file_size": 2048576,
    "file_extension": ".epub",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:45:00Z"
  }
}
```

### API Security and Validation

**JWT Token Structure:**
```json
{
  "header": {
    "typ": "JWT",
    "alg": "HS256"
  },
  "payload": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "ahmed@example.com",
    "exp": 1705401600,
    "iat": 1705315200,
    "jti": "unique-token-id"
  }
}
```

**Rate Limiting Configuration:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',           # Anonymous users
        'user': '1000/hour',          # Authenticated users
        'password_reset': '5/hour',   # Password reset attempts
    }
}
```

**Request Validation:**
```python
class BookUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_book_file])
    
    def validate_file(self, value):
        # File size validation (50MB max)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File too large")
        
        # File type validation
        if not value.name.lower().endswith('.epub'):
            raise serializers.ValidationError("Only EPUB files allowed")
        
        return value
```

---

## Security & Infrastructure

### Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TRANSPORT     │    │  APPLICATION    │    │     DATA        │
│    SECURITY     │    │    SECURITY     │    │   SECURITY      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • HTTPS/TLS     │    │ • JWT Tokens    │    │ • SQL Injection │
│ • WSS           │    │ • CORS Policy   │    │   Protection    │
│ • Certificate   │    │ • CSRF Tokens   │    │ • Input         │
│   Validation    │    │ • Rate Limiting │    │   Validation    │
│ • Secure        │    │ • Permission    │    │ • Data          │
│   Headers       │    │   Classes       │    │   Encryption    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Authentication & Authorization

**JWT Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}
```

**Permission Classes:**
```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners to edit their objects."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        return obj.user_id == request.user

class IsNotAuthenticated(permissions.BasePermission):
    """Permission class for endpoints that require unauthenticated users."""
    
    def has_permission(self, request, view):
        return not request.user.is_authenticated
```

### Input Validation & Sanitization

**File Upload Security:**
```python
def validate_book_file(value):
    """Comprehensive EPUB file validation"""
    ext = os.path.splitext(value.name)[1].lower()
    
    # Extension validation
    if ext != '.epub':
        raise ValidationError(f'Only EPUB files allowed. Got: {ext}')
    
    # File size validation (50MB max)
    if value.size > 50 * 1024 * 1024:
        raise ValidationError('File size exceeds 50MB limit')
    
    # MIME type validation
    try:
        # Basic EPUB structure validation
        import zipfile
        with zipfile.ZipFile(value, 'r') as zip_file:
            if 'META-INF/container.xml' not in zip_file.namelist():
                raise ValidationError('Invalid EPUB file structure')
    except zipfile.BadZipFile:
        raise ValidationError('Corrupted EPUB file')
    
    return value
```

**SQL Injection Protection:**
```python
# Django ORM automatically protects against SQL injection
# Raw queries use parameterized statements
from django.db import connection

def safe_query_example(user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM book WHERE user_id = %s", 
            [user_id]  # Parameterized query
        )
        return cursor.fetchall()
```

### Rate Limiting Implementation

**Custom Throttle Classes:**
```python
class PasswordResetThrottle(throttling.AnonRateThrottle):
    scope = 'password_reset'
    
    def get_cache_key(self, request, view):
        # Rate limit by IP for password reset attempts
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

class BookUploadThrottle(throttling.UserRateThrottle):
    scope = 'book_upload'
    rate = '10/hour'  # Max 10 book uploads per hour per user
```

### Error Handling & Logging

**Global Exception Handler:**
```python
def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'status': 'error',
            'en': 'An error occurred',
            'ar': 'حدث خطأ',
            'error_code': getattr(exc, 'error_code', 'UNKNOWN_ERROR'),
            'details': response.data
        }
        
        # Log security-related errors
        if response.status_code in [401, 403, 429]:
            logger.warning(f'Security event: {exc} - User: {context.get("request").user}')
        
        response.data = custom_response_data
    
    return response
```

**Comprehensive Logging:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': True,
        },
        'ai_workflow': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## Asynchronous Processing

### Celery Task Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CELERY TASK FLOW                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DJANGO VIEW   │───▶│   CELERY TASK   │───▶│  AI WORKFLOW    │
│   (Book Upload) │    │   (Background)  │    │   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JOB RECORD    │    │     REDIS       │    │    DATABASE     │
│   (Database)    │    │   (Message      │    │   (Results)     │
│                 │    │    Broker)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │       WEBSOCKET           │
                    │   (Real-time Updates)     │
                    └───────────────────────────┘
```

### Celery Configuration

**Settings Configuration:**
```python
# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Dubai'

# Task routing
CELERY_TASK_ROUTES = {
    'books.tasks.process_book_workflow': {'queue': 'ai_processing'},
    'authentication.tasks.send_password_reset_email': {'queue': 'email'},
    'authentication.tasks.send_welcome_email': {'queue': 'email'},
}

# Worker configuration
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
```

### Background Task Implementation

**Main Book Processing Task:**
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_book_workflow(self, job_id: str, user_id: str, book_id: str, filename: str):
    """Process uploaded book through complete AI workflow graph."""
    
    try:
        # Initialize job tracking
        job = Job.objects.get(id=job_id)
        book = Book.objects.get(book_id=book_id)
        
        # Update job status
        job.status = Job.Status.RUNNING
        job.started_at = timezone.now()
        job.progress = 10
        job.save(update_fields=["status", "started_at", "progress", "updated_at"])
        
        # Send processing started notification
        _notify_user(user_id, {
            "event": "processing_started",
            "job_id": job_id,
            "status": "running",
            "message": f"بدأ تحليل الملف {filename}"
        })
        
        # Create progress callback for real-time updates
        progress_callback = _create_progress_callback(user_id, job_id)
        
        # Execute AI workflow
        from ai_workflow.src.main import invoke_workflow
        from ai_workflow.src.schemas.states import create_initial_state
        
        initial_state = create_initial_state(
            book_id=str(book_id), 
            file_path=book.file.path, 
            progress_callback=progress_callback
        )
        
        result = invoke_workflow(initial_state)
        
        # Process and save results
        if result:
            # Update book with AI analysis results
            if 'book_name_result' in result:
                book.title = result['book_name_result']['suggested_title']
            
            if 'text_quality_assessment' in result:
                book.quality_score = result['text_quality_assessment'].quality_score
            
            if 'is_arabic' in result:
                book.detected_language = 'ar' if result['is_arabic'] else 'unknown'
                book.language_confidence = 1.0 if result['is_arabic'] else 0.0
            
            if 'text_classification' in result:
                book.text_classification = {
                    "is_literary": result['text_classification'].is_literary,
                    "classification": result['text_classification'].classification,
                    "confidence": result['text_classification'].confidence
                }
            
            book.processing_status = 'completed'
            book.save()
            
            # Complete job
            job.status = Job.Status.COMPLETED
            job.progress = 100
            job.finished_at = timezone.now()
            job.result = {"characters_extracted": True}
            job.save(update_fields=["status", "progress", "finished_at", "result", "updated_at"])
            
            # Send completion notification
            _notify_user(user_id, {
                "event": "processing_completed",
                "job_id": job_id,
                "status": "completed",
                "message": "تم تحليل الكتاب بنجاح"
            })
            
    except Exception as exc:
        # Handle errors with retry logic
        job.status = Job.Status.FAILED
        job.error = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error", "finished_at", "updated_at"])
        
        # Send error notification
        _notify_user(user_id, {
            "event": "processing_failed",
            "job_id": job_id,
            "status": "failed",
            "error": str(exc)
        })
        
        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        raise exc
```

### WebSocket Integration

**Django Channels Configuration:**
```python
# Channel layers configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}

# ASGI application
ASGI_APPLICATION = 'graduation_backend.asgi.application'
```

**WebSocket Consumer:**
```python
class UserNotificationsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        
        if user and user.is_authenticated:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
        else:
            # Test group for development
            self.group_name = "test_group"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def job_update(self, event):
        """Handle job update events from Celery tasks"""
        await self.send_json(event)

    async def receive_json(self, content):
        """Handle incoming messages from client"""
        # Echo for testing
        await self.send_json({
            "type": "echo",
            "message": f"Echo: {content.get('message', 'No message')}",
            "timestamp": timezone.now().isoformat()
        })
```

**Real-time Notification System:**
```python
def _notify_user(user_id: str, payload: dict):
    """Send notification to user via WebSocket."""
    try:
        channel_layer = get_channel_layer()
        group_name = f"user_{user_id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name, 
            {"type": "job.update", **payload}
        )
        
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {str(e)}")
```

---

## Data Flow

### Complete Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        END-TO-END DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. FILE UPLOAD
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Django    │───▶│  Database   │
│ (EPUB File) │    │   (Book     │    │  (Book      │
│             │    │   Model)    │    │   Record)   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ TXT Convert │
                   │ (epub_to_   │
                   │ raw_html)   │
                   └─────────────┘

2. BACKGROUND PROCESSING
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Celery    │───▶│ AI Workflow │───▶│  LangGraph  │
│   Task      │    │  (Django    │    │ (Gemini AI) │
│  (Async)    │    │ Integration)│    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ WebSocket   │    │ State Mgmt  │    │ Character   │
│ Progress    │    │ (TypedDict) │    │ Extraction  │
│ Updates     │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘

3. AI PROCESSING STAGES
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ VALIDATION  │───▶│ NAME EXTRACT│───▶│PREPROCESSING│───▶│  ANALYSIS   │
│             │    │             │    │             │    │             │
│• Language   │    │• Book Title │    │• Chunking   │    │• Character  │
│• Quality    │    │• Metadata   │    │• Cleaning   │    │  Profiles   │
│• Literary   │    │             │    │• Metadata   │    │• Relations  │
│  Class.     │    │             │    │  Removal    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

4. RESULT STORAGE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Character  │───▶│   Chunk     │───▶│Relationship │
│   Records   │    │ Character   │    │   Records   │
│  (JSON)     │    │  Junction   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │  Frontend   │
                   │  Notification│
                   │ (WebSocket) │
                   └─────────────┘
```

### State Transitions

**Book Processing States:**
```
pending ──────▶ processing ──────▶ completed
   │                │                   ▲
   │                ▼                   │
   └──────────▶ failed ─────────────────┘
                   │
                   ▼
               retry_queue
```

**Job Status Flow:**
```python
class JobStatus:
    PENDING = "pending"      # Initial state
    RUNNING = "running"      # Celery task started
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"        # Error occurred

# State transition validation
def update_job_status(job, new_status):
    valid_transitions = {
        'pending': ['running', 'failed'],
        'running': ['completed', 'failed'],
        'completed': [],  # Terminal state
        'failed': ['running']  # Can retry
    }
    
    if new_status not in valid_transitions[job.status]:
        raise ValueError(f"Invalid status transition: {job.status} -> {new_status}")
    
    job.status = new_status
    job.save()
```

### Data Validation Pipeline

**Input Validation Layers:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYERS                            │
└─────────────────────────────────────────────────────────────────┘

1. FRONTEND VALIDATION
├── File type checking (.epub only)
├── File size limits (50MB max)
├── Form field validation
└── Client-side sanitization

2. API VALIDATION  
├── Django serializer validation
├── Custom validator functions
├── Authentication checks
└── Rate limiting enforcement

3. MODEL VALIDATION
├── Database constraints
├── Foreign key validation
├── JSON schema validation
└── Business rule enforcement

4. AI WORKFLOW VALIDATION
├── Text quality assessment
├── Language detection
├── Content classification
└── Processing feasibility check
```

---

## Deployment Architecture

### Production Deployment Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │     NGINX       │
                    │ (Reverse Proxy) │
                    │   Port 80/443   │
                    └─────────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │   Django    │  │   Django    │  │  WebSocket  │
    │ App Server  │  │ App Server  │  │   Server    │
    │   (WSGI)    │  │   (WSGI)    │  │   (ASGI)    │
    │  Port 8000  │  │  Port 8001  │  │  Port 8002  │
    └─────────────┘  └─────────────┘  └─────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
    ┌─────────────────────────▼─────────────────────────┐
    │                 SHARED SERVICES                   │
    ├─────────────┬─────────────┬─────────────┬─────────┤
    │   SQLite    │    Redis    │   Celery    │  File   │
    │  Database   │ Cache/Queue │  Workers    │ Storage │
    │             │             │             │         │
    └─────────────┴─────────────┴─────────────┴─────────┘
```

### Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media directories
RUN mkdir -p /app/media/books

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "graduation_backend.wsgi:application"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./media:/app/media
      - ./static:/app/static
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,127.0.0.1
    depends_on:
      - redis
      - db

  websocket:
    build: .
    command: daphne -b 0.0.0.0 -p 8002 graduation_backend.asgi:application
    ports:
      - "8002:8002"
    volumes:
      - ./media:/app/media
    depends_on:
      - redis
      - db

  celery:
    build: .
    command: celery -A graduation_backend worker -l info
    volumes:
      - ./media:/app/media
    depends_on:
      - redis
      - db

  celery-beat:
    build: .
    command: celery -A graduation_backend beat -l info
    volumes:
      - ./media:/app/media
    depends_on:
      - redis
      - db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=graduation_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/app/static
      - ./media:/app/media
    depends_on:
      - web
      - websocket

volumes:
  postgres_data:
```

### Environment Configuration

**Production Settings:**
```python
# production_settings.py
from .settings import *
import os

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'graduation_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['file'],
    },
}
```

---

## Technical Specifications

### System Requirements

**Minimum Hardware Requirements:**
```
CPU:     4 cores (2.0 GHz+)
RAM:     8 GB
Storage: 100 GB SSD
Network: 100 Mbps
```

**Recommended Hardware Requirements:**
```
CPU:     8 cores (3.0 GHz+)
RAM:     16 GB
Storage: 500 GB NVMe SSD
Network: 1 Gbps
GPU:     Optional (for local LLM inference)
```

### Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend Framework** | Django | 4.2+ | Web framework and ORM |
| **API Framework** | Django REST Framework | 3.14+ | RESTful API development |
| **Authentication** | JWT (Simple JWT) | 5.2+ | Token-based authentication |
| **Database** | SQLite | 3.35+ | Primary database |
| **Cache/Queue** | Redis | 7.0+ | Caching and message broker |
| **Task Queue** | Celery | 5.3+ | Background task processing |
| **WebSocket** | Django Channels | 4.0+ | Real-time communication |
| **AI Framework** | LangGraph | Latest | Workflow orchestration |
| **LLM** | Google Gemini | 2.5-flash | Language model |
| **File Processing** | EbookLib | 0.18+ | EPUB file handling |
| **Web Server** | Gunicorn + Nginx | Latest | Production deployment |
| **Containerization** | Docker | 24.0+ | Application containerization |

### Performance Metrics

**Expected Performance:**
```
API Response Time:     < 200ms (95th percentile)
File Upload:          50MB EPUB in < 30s
AI Processing:        5-15 minutes per book
Concurrent Users:     100+ simultaneous
Database Queries:     < 50ms average
WebSocket Latency:    < 100ms
Memory Usage:         < 2GB per worker
```

**Scalability Targets:**
```
Books per Day:        1,000+
Characters Extracted: 10,000+ per day
Storage Growth:       10GB per month
User Base:           10,000+ registered users
```

### API Rate Limits

```python
RATE_LIMITS = {
    'anonymous_users': '100/hour',
    'authenticated_users': '1000/hour',
    'book_upload': '10/hour',
    'password_reset': '5/hour',
    'character_queries': '500/hour',
}
```

### File Size Limits

```python
FILE_LIMITS = {
    'epub_max_size': 50 * 1024 * 1024,    # 50MB
    'total_storage_per_user': 1024 * 1024 * 1024,  # 1GB
    'max_books_per_user': 100,
    'max_processing_time': 30 * 60,       # 30 minutes
}
```

---

## Conclusion

This system represents a sophisticated, production-ready AI-powered book analysis platform with the following key strengths:

### **Architectural Excellence**
- **Modular Design**: Clear separation of concerns with dedicated Django apps
- **Scalable Infrastructure**: Async processing with Celery and Redis
- **Real-time Capabilities**: WebSocket integration for live updates
- **Security First**: Comprehensive JWT authentication and validation

### **AI Innovation**
- **Advanced Workflow**: LangGraph-based multi-stage processing
- **State-of-the-art Models**: Google Gemini 2.5 Flash integration
- **Intelligent Analysis**: Character extraction with relationship mapping
- **Flexible Data Storage**: JSON-based character profiles with Unicode support

### **Developer Experience**
- **Comprehensive API**: RESTful endpoints with detailed documentation
- **Robust Error Handling**: Global exception handling with logging
- **Testing Framework**: Built-in Django testing with AI workflow validation
- **Documentation**: Extensive markdown documentation

### **Production Readiness**
- **Containerization**: Docker and Docker Compose configurations
- **Monitoring**: Comprehensive logging and error tracking
- **Performance**: Optimized database queries and caching
- **Deployment**: Production-ready with Nginx and Gunicorn

This architecture provides a solid foundation for a scalable, maintainable, and feature-rich book analysis platform that can handle enterprise-level workloads while maintaining excellent user experience through real-time processing updates and bilingual support.

---

*Document Version: 1.0*  
*Last Updated: January 2024*  
*Author: System Architecture Team*
