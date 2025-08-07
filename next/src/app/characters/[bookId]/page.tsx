'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  Users, 
  User, 
  Calendar, 
  MapPin, 
  Heart, 
  Brain,
  ChevronDown,
  ChevronRight,
  ArrowLeft,
  Network,
  BookOpen
} from 'lucide-react';
import { Character, Book } from '@/types';
import { charactersApi, booksApi } from '@/lib/api';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function CharacterProfilesPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { isAuthenticated } = useAuthStore();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedCharacter, setExpandedCharacter] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth';
      return;
    }

    fetchData();
  }, [bookId, isAuthenticated]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch book details
      const bookResponse = await booksApi.getBook(bookId);
      if (bookResponse.success) {
        setBook(bookResponse.data);
      }
      
      // Fetch characters
      const charactersResponse = await charactersApi.getBookCharacters(bookId);
      if (charactersResponse.success) {
        setCharacters(charactersResponse.data);
      }
    } catch (error: any) {
      toast.error('Failed to load character data');
      console.error('Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCharacterExpansion = (characterId: string) => {
    setExpandedCharacter(expandedCharacter === characterId ? null : characterId);
  };

  const getRelationshipStrengthColor = (strength: number) => {
    if (strength >= 0.8) return 'text-red-600';
    if (strength >= 0.6) return 'text-orange-600';
    if (strength >= 0.4) return 'text-yellow-600';
    return 'text-gray-600';
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard" className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </Link>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Character Profiles
              </h1>
              {book && (
                <p className="text-gray-600">
                  Characters from "{book.title}" by {book.author}
                </p>
              )}
            </div>
            
            <div className="flex space-x-3">
              <Link href={`/relationships/${bookId}`}>
                <Button variant="outline" className="flex items-center space-x-2">
                  <Network className="h-4 w-4" />
                  <span>View Graph</span>
                </Button>
              </Link>
              <Link href={`/reader/${bookId}`}>
                <Button className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4" />
                  <span>Read Book</span>
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 rounded mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : characters.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No characters found</h3>
              <p className="text-gray-600">
                The AI is still processing this book. Characters will appear here once analysis is complete.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {characters.map((character) => (
              <Card key={character.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{character.name}</CardTitle>
                      {character.age && (
                        <CardDescription className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>{character.age} years old</span>
                        </CardDescription>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleCharacterExpansion(character.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedCharacter === character.id ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </CardHeader>
                
                <CardContent>
                  {/* Physical Traits */}
                  {character.physicalTraits.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center space-x-1">
                        <User className="h-4 w-4" />
                        <span>Physical Traits</span>
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {character.physicalTraits.map((trait, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                          >
                            {trait}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Personality */}
                  {character.personality.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center space-x-1">
                        <Brain className="h-4 w-4" />
                        <span>Personality</span>
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {character.personality.map((trait, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
                          >
                            {trait}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Relationships Summary */}
                  {character.relationships.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center space-x-1">
                        <Heart className="h-4 w-4" />
                        <span>Key Relationships</span>
                      </h4>
                      <div className="space-y-1">
                        {character.relationships.slice(0, 3).map((relationship, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-gray-700">{relationship.targetCharacterName}</span>
                            <span className={`font-medium ${getRelationshipStrengthColor(relationship.strength)}`}>
                              {relationship.relationshipType}
                            </span>
                          </div>
                        ))}
                        {character.relationships.length > 3 && (
                          <p className="text-xs text-gray-500">
                            +{character.relationships.length - 3} more relationships
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Expanded Details */}
                  {expandedCharacter === character.id && (
                    <div className="border-t pt-4 space-y-4">
                      {/* All Relationships */}
                      {character.relationships.length > 0 && (
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">All Relationships</h5>
                          <div className="space-y-2">
                            {character.relationships.map((relationship, index) => (
                              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium text-gray-900">
                                    {relationship.targetCharacterName}
                                  </span>
                                  <span className={`text-sm font-medium ${getRelationshipStrengthColor(relationship.strength)}`}>
                                    {Math.round(relationship.strength * 100)}% strength
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600">{relationship.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Events */}
                      {character.events.length > 0 && (
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">Key Events</h5>
                          <div className="space-y-2">
                            {character.events.map((event, index) => (
                              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium text-gray-900">{event.title}</span>
                                  <span className="text-xs text-gray-500">
                                    Ch. {event.chapter}, Pg. {event.page}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600">{event.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {characters.length > 0 && (
          <div className="mt-8">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Character Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{characters.length}</p>
                    <p className="text-sm text-gray-600">Total Characters</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {characters.filter(c => c.age).length}
                    </p>
                    <p className="text-sm text-gray-600">With Age Info</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {characters.reduce((sum, c) => sum + c.relationships.length, 0)}
                    </p>
                    <p className="text-sm text-gray-600">Total Relationships</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {characters.reduce((sum, c) => sum + c.events.length, 0)}
                    </p>
                    <p className="text-sm text-gray-600">Key Events</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
} 