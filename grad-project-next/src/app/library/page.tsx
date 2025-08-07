'use client';

import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/auth';
import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  Library, 
  Users, 
  Eye, 
  Search,
  Filter,
  SortAsc,
  SortDesc,
  ArrowLeft
} from 'lucide-react';
import { Book } from '@/types';
import { booksApi } from '@/lib/api';
import { formatFileSize, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function PublicLibraryPage() {
  const { isAuthenticated } = useAuthStore();
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'title' | 'author' | 'uploadDate' | 'characters'>('uploadDate');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

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
      const response = await booksApi.getPublicBooks();
      if (response.success) {
        setBooks(response.data);
      }
    } catch (error: any) {
      toast.error('Failed to load public books');
      console.error('Error fetching books:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredAndSortedBooks = books
    .filter(book => 
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.author.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'author':
          aValue = a.author.toLowerCase();
          bValue = b.author.toLowerCase();
          break;
        case 'uploadDate':
          aValue = new Date(a.uploadDate);
          bValue = new Date(b.uploadDate);
          break;
        case 'characters':
          aValue = a.characters.length;
          bValue = b.characters.length;
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const handleSort = (field: 'title' | 'author' | 'uploadDate' | 'characters') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const getSortIcon = (field: string) => {
    if (sortBy !== field) return null;
    return sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />;
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
                Public Library
              </h1>
              <p className="text-gray-600">
                Explore books shared by the community
              </p>
            </div>
            
            <Link href="/upload">
              <Button className="flex items-center space-x-2">
                <Library className="h-4 w-4" />
                <span>Share Your Book</span>
              </Button>
            </Link>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search books by title or author..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Filter className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Sort by:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => handleSort(e.target.value as any)}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="uploadDate">Upload Date</option>
                    <option value="title">Title</option>
                    <option value="author">Author</option>
                    <option value="characters">Character Count</option>
                  </select>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="flex items-center space-x-1"
                  >
                    {getSortIcon(sortBy) || <SortDesc className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Books Grid */}
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
        ) : filteredAndSortedBooks.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Library className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {searchTerm ? 'No books found' : 'No books shared yet'}
              </h3>
              <p className="text-gray-600 mb-6">
                {searchTerm 
                  ? 'Try adjusting your search terms'
                  : 'Be the first to share a book with the community!'
                }
              </p>
              {!searchTerm && (
                <Link href="/upload">
                  <Button className="flex items-center space-x-2">
                    <Library className="h-4 w-4" />
                    <span>Share Your First Book</span>
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedBooks.map((book) => (
              <Card key={book.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2 line-clamp-2">{book.title}</CardTitle>
                      <CardDescription className="text-sm">
                        by {book.author}
                      </CardDescription>
                    </div>
                    {book.processingStatus.status === 'completed' && (
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <Users className="h-4 w-4 text-green-600" />
                      </div>
                    )}
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Characters:</span>
                      <span className="font-medium">{book.characters.length}</span>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">File size:</span>
                      <span className="font-medium">{formatFileSize(book.fileSize)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Shared by:</span>
                      <span className="font-medium">{book.uploadedBy}</span>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Uploaded:</span>
                      <span className="font-medium">{formatDate(book.uploadDate)}</span>
                    </div>
                    
                    <div className="pt-3 border-t">
                      <div className="flex space-x-2">
                        <Link href={`/characters/${book.id}`} className="flex-1">
                          <Button variant="outline" size="sm" className="w-full">
                            <Users className="h-4 w-4 mr-1" />
                            Characters
                          </Button>
                        </Link>
                        <Link href={`/relationships/${book.id}`} className="flex-1">
                          <Button variant="outline" size="sm" className="w-full">
                            <Library className="h-4 w-4 mr-1" />
                            Graph
                          </Button>
                        </Link>
                        <Link href={`/reader/${book.id}`} className="flex-1">
                          <Button size="sm" className="w-full">
                            <Eye className="h-4 w-4 mr-1" />
                            Read
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Stats */}
        {books.length > 0 && (
          <div className="mt-8">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Library Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{books.length}</p>
                    <p className="text-sm text-gray-600">Total Books</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {books.reduce((sum, book) => sum + book.characters.length, 0)}
                    </p>
                    <p className="text-sm text-gray-600">Total Characters</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {new Set(books.map(book => book.uploadedBy)).size}
                    </p>
                    <p className="text-sm text-gray-600">Contributors</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {books.filter(book => book.processingStatus.status === 'completed').length}
                    </p>
                    <p className="text-sm text-gray-600">Processed Books</p>
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