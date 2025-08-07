export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  settings: UserSettings;
}

export interface UserSettings {
  autoShareBooks: boolean;
  emailNotifications: boolean;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  coverImage?: string;
  fileSize: number;
  uploadDate: string;
  processingStatus: ProcessingStatus;
  totalPages: number;
  processedPages: number;
  isPublic: boolean;
  uploadedBy: string;
  characters: Character[];
  relationships: Relationship[];
}

export interface ProcessingStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
}

export interface Character {
  id: string;
  name: string;
  age?: number;
  physicalTraits: string[];
  personality: string[];
  relationships: CharacterRelationship[];
  events: CharacterEvent[];
  bookId: string;
}

export interface CharacterRelationship {
  targetCharacterId: string;
  targetCharacterName: string;
  relationshipType: string;
  strength: number; // 0-1
  description: string;
}

export interface CharacterEvent {
  id: string;
  title: string;
  description: string;
  chapter: number;
  page: number;
}

export interface Relationship {
  id: string;
  sourceCharacterId: string;
  targetCharacterId: string;
  relationshipType: string;
  strength: number;
  description: string;
  bookId: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  name: string;
}

export interface UploadBookRequest {
  file: File;
  isPublic: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
} 