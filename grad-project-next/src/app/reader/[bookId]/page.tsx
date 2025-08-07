'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  BookOpen, 
  ChevronLeft, 
  ChevronRight, 
  Brain,
  Users,
  Network,
  ArrowLeft,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react';
import { Book } from '@/types';
import { booksApi } from '@/lib/api';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function ReaderPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { isAuthenticated } = useAuthStore();
  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [fontSize, setFontSize] = useState(16);
  const [showAIInsights, setShowAIInsights] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth';
      return;
    }

    fetchBook();
  }, [bookId, isAuthenticated]);

  const fetchBook = async () => {
    try {
      setIsLoading(true);
      const response = await booksApi.getBook(bookId);
      if (response.success) {
        setBook(response.data);
        setTotalPages(response.data.totalPages);
      }
    } catch (error: any) {
      toast.error('Failed to load book');
      console.error('Error fetching book:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handleFontSizeChange = (newSize: number) => {
    setFontSize(Math.max(12, Math.min(24, newSize)));
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Loading book...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Card>
            <CardContent className="p-12 text-center">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Book not found</h3>
              <p className="text-gray-600 mb-6">
                The book you're looking for doesn't exist or you don't have permission to access it.
              </p>
              <Link href="/dashboard">
                <Button>Back to Dashboard</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {!isFullscreen && <Navigation />}
      
      <div className={`${isFullscreen ? 'h-full' : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'}`}>
        {/* Header */}
        {!isFullscreen && (
          <div className="mb-6">
            <Link href="/dashboard" className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4">
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Link>
            
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-1">{book.title}</h1>
                <p className="text-gray-600">by {book.author}</p>
              </div>
              
              <div className="flex items-center space-x-3">
                <Link href={`/characters/${bookId}`}>
                  <Button variant="outline" size="sm" className="flex items-center space-x-1">
                    <Users className="h-4 w-4" />
                    <span>Characters</span>
                  </Button>
                </Link>
                <Link href={`/relationships/${bookId}`}>
                  <Button variant="outline" size="sm" className="flex items-center space-x-1">
                    <Network className="h-4 w-4" />
                    <span>Graph</span>
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Reader Controls */}
        <div className="mb-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">Font Size:</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleFontSizeChange(fontSize - 1)}
                      disabled={fontSize <= 12}
                    >
                      A-
                    </Button>
                    <span className="text-sm font-medium">{fontSize}px</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleFontSizeChange(fontSize + 1)}
                      disabled={fontSize >= 24}
                    >
                      A+
                    </Button>
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAIInsights(!showAIInsights)}
                    className="flex items-center space-x-1"
                  >
                    {showAIInsights ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    <span>AI Insights</span>
                  </Button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={toggleFullscreen}
                  >
                    {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Reader Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Reader */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] lg:h-[800px]">
              <CardContent className="p-6 h-full overflow-y-auto">
                <div 
                  className="prose max-w-none h-full"
                  style={{ fontSize: `${fontSize}px` }}
                >
                  {/* Placeholder content - in a real implementation, this would render the actual EPUB content */}
                  <div className="text-center py-20">
                    <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">EPUB Reader</h2>
                    <p className="text-gray-600 mb-4">
                      Page {currentPage} of {totalPages}
                    </p>
                    <p className="text-gray-500">
                      This is a placeholder for the actual EPUB content. In a real implementation, 
                      this would display the parsed EPUB text with proper formatting, images, and navigation.
                    </p>
                    <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <Brain className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-900">AI Analysis Active</span>
                      </div>
                      <p className="text-sm text-blue-700">
                        Our AI is analyzing this content for character mentions, relationships, and key events.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Insights Sidebar */}
          {showAIInsights && (
            <div className="lg:col-span-1">
              <div className="space-y-4">
                {/* Processing Status */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="h-5 w-5" />
                      <span>AI Analysis</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Processing Status:</span>
                        <span className={`text-sm font-medium ${
                          book.processingStatus.status === 'completed' ? 'text-green-600' : 
                          book.processingStatus.status === 'processing' ? 'text-blue-600' : 'text-gray-600'
                        }`}>
                          {book.processingStatus.status}
                        </span>
                      </div>
                      
                      {book.processingStatus.status === 'processing' && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Progress:</span>
                            <span className="font-medium">
                              {Math.round((book.processedPages / book.totalPages) * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${(book.processedPages / book.totalPages) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Characters Found:</span>
                        <span className="font-medium">{book.characters.length}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Relationships:</span>
                        <span className="font-medium">{book.relationships.length}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Current Page Characters */}
                {book.characters.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Users className="h-5 w-5" />
                        <span>Characters on This Page</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {book.characters.slice(0, 5).map((character) => (
                          <div key={character.id} className="p-2 bg-gray-50 rounded">
                            <p className="font-medium text-sm">{character.name}</p>
                            {character.age && (
                              <p className="text-xs text-gray-500">{character.age} years old</p>
                            )}
                          </div>
                        ))}
                        {book.characters.length > 5 && (
                          <p className="text-xs text-gray-500 text-center">
                            +{book.characters.length - 5} more characters
                          </p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Reading Progress */}
                <Card>
                  <CardHeader>
                    <CardTitle>Reading Progress</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Current Page:</span>
                        <span className="font-medium">{currentPage}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Total Pages:</span>
                        <span className="font-medium">{totalPages}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(currentPage / totalPages) * 100}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-500 text-center">
                        {Math.round((currentPage / totalPages) * 100)}% complete
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Controls */}
        <div className="mt-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <Button
                  onClick={handlePreviousPage}
                  disabled={currentPage <= 1}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <ChevronLeft className="h-4 w-4" />
                  <span>Previous</span>
                </Button>
                
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    Page {currentPage} of {totalPages}
                  </span>
                  <input
                    type="number"
                    min="1"
                    max={totalPages}
                    value={currentPage}
                    onChange={(e) => {
                      const page = parseInt(e.target.value);
                      if (page >= 1 && page <= totalPages) {
                        setCurrentPage(page);
                      }
                    }}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-center text-sm"
                  />
                </div>
                
                <Button
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <span>Next</span>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 