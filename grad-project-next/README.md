# Interactive EPUB Reader

A full-stack web application that allows users to upload EPUB books, read them, and automatically extract character profiles and relationship graphs using AI. Users can also choose to share their processed books to a public library.

## 🚀 Features

### Core Functionality
- **EPUB Upload & Processing**: Upload EPUB files and let AI analyze them automatically
- **AI-Powered Analysis**: Extract characters, relationships, and build interactive graphs
- **Character Profiles**: Detailed character information with traits, relationships, and story events
- **Relationship Graphs**: Interactive network visualization of character connections
- **Enhanced Reading**: Read with AI-powered insights and character tracking
- **Public Library**: Share and explore books from the community

### Technical Features
- **Modern UI**: Built with Next.js, TypeScript, and TailwindCSS
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Processing**: Live progress tracking for book analysis
- **Interactive Visualizations**: Force-directed graphs for relationship mapping
- **Authentication**: Secure user authentication and account management
- **File Upload**: Drag-and-drop EPUB file upload with progress tracking

## 🛠️ Tech Stack

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **React Hook Form**: Form handling and validation
- **Zustand**: State management
- **React Force Graph**: Interactive network visualizations
- **React Dropzone**: File upload functionality
- **React Hot Toast**: Toast notifications

### Backend (Planned)
- **Django**: Python web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Celery**: Background task processing
- **Redis**: Caching and message broker

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # User dashboard
│   ├── upload/            # Book upload page
│   ├── characters/        # Character profiles
│   ├── relationships/     # Relationship graphs
│   ├── library/           # Public library
│   ├── reader/            # EPUB reader
│   └── settings/          # User settings
├── components/            # Reusable components
│   ├── ui/               # UI components (Button, Input, Card, etc.)
│   └── layout/           # Layout components (Navigation)
├── lib/                  # Utilities and configurations
│   ├── api.ts           # API client and endpoints
│   └── utils.ts         # Utility functions
├── store/               # State management
│   └── auth.ts          # Authentication store
└── types/               # TypeScript type definitions
    └── index.ts         # Application types
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd interactive-epub-reader
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create a `.env.local` file in the root directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📖 Usage Guide

### 1. Getting Started
- Visit the landing page to learn about the application
- Click "Get Started" to create an account or sign in
- Complete the authentication process

### 2. Uploading Books
- Navigate to the Upload page from the dashboard
- Drag and drop your EPUB file or click to browse
- Choose whether to share the book publicly
- Monitor the processing progress
- Once complete, access character profiles and relationship graphs

### 3. Exploring Characters
- View detailed character profiles with traits and relationships
- Expand character cards to see full details
- Browse character events and story connections
- Filter and search through character information

### 4. Relationship Graphs
- Interactive network visualization of character relationships
- Click on characters to highlight their connections
- Filter by relationship type
- Zoom, pan, and explore the graph
- View relationship strength and descriptions

### 5. Reading Experience
- Enhanced EPUB reader with AI insights
- Adjust font size and reading preferences
- View character mentions on current page
- Track reading progress
- Access character and graph information while reading

### 6. Public Library
- Browse books shared by the community
- Search and filter public books
- View character counts and processing status
- Access shared character profiles and graphs

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Structure

The application follows a modular structure with clear separation of concerns:

- **Pages**: Each route has its own page component
- **Components**: Reusable UI components with TypeScript interfaces
- **API Layer**: Centralized API client with error handling
- **State Management**: Zustand stores for global state
- **Types**: Comprehensive TypeScript definitions

### Key Components

- **Navigation**: Responsive navigation with user menu
- **Upload**: Drag-and-drop file upload with progress tracking
- **Character Profiles**: Expandable character cards with detailed information
- **Relationship Graph**: Interactive force-directed graph visualization
- **Reader**: EPUB reader with AI insights sidebar

## 🎨 UI/UX Features

### Design System
- **Color Palette**: Primary blue theme with semantic colors
- **Typography**: Inter font family for modern readability
- **Components**: Consistent button, input, and card components
- **Responsive**: Mobile-first design approach

### User Experience
- **Loading States**: Skeleton loaders and progress indicators
- **Error Handling**: Toast notifications for user feedback
- **Accessibility**: ARIA labels and keyboard navigation
- **Animations**: Smooth transitions and micro-interactions

## 🔒 Security

- **Authentication**: JWT-based authentication
- **Authorization**: Route protection for authenticated users
- **Input Validation**: Form validation and sanitization
- **API Security**: CORS configuration and request validation

## 🚧 Backend Integration

The frontend is designed to work with a Django REST API backend. Key endpoints include:

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

### Books
- `GET /api/books/` - Get user's books
- `POST /api/books/upload/` - Upload new book
- `GET /api/books/{id}/` - Get book details
- `GET /api/books/public/` - Get public books

### Characters & Relationships
- `GET /api/books/{id}/characters/` - Get book characters
- `GET /api/books/{id}/relationships/` - Get book relationships

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile
- `POST /api/user/change-password/` - Change password

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Next.js team for the amazing React framework
- TailwindCSS for the utility-first CSS framework
- Lucide for the beautiful icon set
- React Force Graph for the network visualization library

## 📞 Support

For support, email support@interactive-epub-reader.com or create an issue in the repository.

---

**Note**: This is a frontend implementation. The backend Django API needs to be developed separately to provide the required endpoints for full functionality.
