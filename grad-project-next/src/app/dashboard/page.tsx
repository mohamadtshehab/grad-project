'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth';
import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  BookOpen, 
  Users, 
  Network, 
  Upload, 
  Library,
  Eye,
  Play,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus
} from 'lucide-react';
import { Book, ProcessingStatus } from '@/types';
import { booksApi } from '@/lib/api';
import { formatFileSize, formatDate, getProgressPercentage } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const { user, isAuthenticated } = useAuthStore();
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth';
      return;
    }

    fetchBooks();
  }, [isAuthenticated]);

  const fetchBooks = async () => {
    try {
      setIsLoading(true);
      const response = await booksApi.getUserBooks();
      if (response.success) {
        setBooks(response.data);
      }
    } catch (error: any) {
      toast.error('Failed to load books');
      console.error('Error fetching books:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: ProcessingStatus) => {
    switch (status.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-blue-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: ProcessingStatus) => {
    switch (status.status) {
      case 'completed':
        return 'text-green-600';
      case 'processing':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-gray-600">
            Manage your uploaded books and explore AI-powered insights
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/upload">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Upload className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Upload New Book</h3>
                <p className="text-sm text-gray-600">Add a new EPUB to your library</p>
              </CardContent>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/library">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Library className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Public Library</h3>
                <p className="text-sm text-gray-600">Explore shared books</p>
              </CardContent>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/characters">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Users className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Character Profiles</h3>
                <p className="text-sm text-gray-600">View all characters</p>
              </CardContent>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/relationships">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Network className="h-6 w-6 text-orange-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Relationship Graphs</h3>
                <p className="text-sm text-gray-600">Visualize connections</p>
              </CardContent>
            </Link>
          </Card>
        </div>

        {/* Books Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Your Books</h2>
            <Link href="/upload">
              <Button className="flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>Upload Book</span>
              </Button>
            </Link>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-4 bg-gray-200 rounded mb-4"></div>
                    <div className="h-3 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : books.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No books yet</h3>
                <p className="text-gray-600 mb-6">
                  Upload your first EPUB book to get started with AI-powered analysis
                </p>
                <Link href="/upload">
                  <Button className="flex items-center space-x-2">
                    <Upload className="h-4 w-4" />
                    <span>Upload Your First Book</span>
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {books.map((book) => (
                <Card key={book.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-2">{book.title}</CardTitle>
                        <CardDescription className="text-sm">
                          by {book.author}
                        </CardDescription>
                      </div>
                      {getStatusIcon(book.processingStatus)}
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Status:</span>
                        <span className={`font-medium ${getStatusColor(book.processingStatus)}`}>
                          {book.processingStatus.status}
                        </span>
                      </div>
                      
                      {book.processingStatus.status === 'processing' && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Progress:</span>
                            <span className="font-medium">
                              {getProgressPercentage(book.processedPages, book.totalPages)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                              style={{ 
                                width: `${getProgressPercentage(book.processedPages, book.totalPages)}%` 
                              }}
                            ></div>
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">File size:</span>
                        <span className="font-medium">{formatFileSize(book.fileSize)}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Uploaded:</span>
                        <span className="font-medium">{formatDate(book.uploadDate)}</span>
                      </div>
                      
                      {book.processingStatus.status === 'completed' && (
                        <div className="pt-3 border-t">
                          <div className="flex space-x-2">
                            <Link href={`/reader/${book.id}`} className="flex-1">
                              <Button size="sm" className="w-full">
                                <Play className="h-4 w-4 mr-1" />
                                Read
                              </Button>
                            </Link>
                            <Link href={`/characters/${book.id}`} className="flex-1">
                              <Button variant="outline" size="sm" className="w-full">
                                <Users className="h-4 w-4 mr-1" />
                                Characters
                              </Button>
                            </Link>
                            <Link href={`/relationships/${book.id}`} className="flex-1">
                              <Button variant="outline" size="sm" className="w-full">
                                <Network className="h-4 w-4 mr-1" />
                                Graph
                              </Button>
                            </Link>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Stats Section */}
        {books.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <BookOpen className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Books</p>
                    <p className="text-2xl font-bold text-gray-900">{books.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Processed</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {books.filter(b => b.processingStatus.status === 'completed').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
                    <Clock className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Processing</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {books.filter(b => b.processingStatus.status === 'processing').length}
                    </p>
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