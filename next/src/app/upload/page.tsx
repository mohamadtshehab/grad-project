'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { useAuthStore } from '@/store/auth';
import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Share2,
  Lock,
  Clock,
  X
} from 'lucide-react';
import { booksApi } from '@/lib/api';
import { formatFileSize } from '@/lib/utils';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function UploadPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isPublic, setIsPublic] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'error'>('idle');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      if (file.type !== 'application/epub+zip' && !file.name.endsWith('.epub')) {
        toast.error('Please upload a valid EPUB file');
        return;
      }
      setUploadedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/epub+zip': ['.epub']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const handleUpload = async () => {
    if (!uploadedFile) {
      toast.error('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    setUploadStatus('uploading');
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await booksApi.uploadBook(uploadedFile, isPublic);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('processing');
      
      if (response.success) {
        toast.success('Book uploaded successfully! Processing will begin shortly.');
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
      }
    } catch (error: any) {
      setUploadStatus('error');
      toast.error(error.response?.data?.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setUploadProgress(0);
    setUploadStatus('idle');
  };

  if (!isAuthenticated) {
    router.push('/auth');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard" className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </Link>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Upload EPUB Book
          </h1>
          <p className="text-gray-600">
            Upload your EPUB file and let our AI analyze it for characters and relationships
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-5 w-5" />
                  <span>Upload EPUB File</span>
                </CardTitle>
                <CardDescription>
                  Drag and drop your EPUB file here, or click to browse
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                {!uploadedFile ? (
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      isDragActive
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    {isDragActive ? (
                      <p className="text-primary-600 font-medium">Drop the file here</p>
                    ) : (
                      <div>
                        <p className="text-gray-600 mb-2">
                          Drag and drop your EPUB file here
                        </p>
                        <p className="text-sm text-gray-500">
                          or click to browse files
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <FileText className="h-8 w-8 text-primary-600" />
                        <div>
                          <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                          <p className="text-sm text-gray-500">{formatFileSize(uploadedFile.size)}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={removeFile}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>

                    {/* Upload Progress */}
                    {uploadStatus !== 'idle' && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">
                            {uploadStatus === 'uploading' && 'Uploading...'}
                            {uploadStatus === 'processing' && 'Processing...'}
                            {uploadStatus === 'completed' && 'Completed!'}
                            {uploadStatus === 'error' && 'Upload failed'}
                          </span>
                          <span className="text-sm text-gray-500">{uploadProgress}%</span>
                        </div>
                        
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              uploadStatus === 'error' ? 'bg-red-500' : 'bg-primary-600'
                            }`}
                            style={{ width: `${uploadProgress}%` }}
                          ></div>
                        </div>
                        
                        {uploadStatus === 'processing' && (
                          <div className="flex items-center space-x-2 text-sm text-blue-600">
                            <Clock className="h-4 w-4" />
                            <span>AI is analyzing your book...</span>
                          </div>
                        )}
                        
                        {uploadStatus === 'completed' && (
                          <div className="flex items-center space-x-2 text-sm text-green-600">
                            <CheckCircle className="h-4 w-4" />
                            <span>Upload successful!</span>
                          </div>
                        )}
                        
                        {uploadStatus === 'error' && (
                          <div className="flex items-center space-x-2 text-sm text-red-600">
                            <AlertCircle className="h-4 w-4" />
                            <span>Upload failed. Please try again.</span>
                          </div>
                        )}
                      </div>
                    )}

                    <Button
                      onClick={handleUpload}
                      disabled={!uploadedFile || isUploading}
                      className="w-full"
                    >
                      {isUploading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Uploading...</span>
                        </div>
                      ) : (
                        <span>Upload Book</span>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Settings Section */}
          <div className="space-y-6">
            {/* Sharing Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Share2 className="h-5 w-5" />
                  <span>Sharing Options</span>
                </CardTitle>
                <CardDescription>
                  Choose whether to share this book with the community
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="sharing"
                      checked={!isPublic}
                      onChange={() => setIsPublic(false)}
                      className="text-primary-600 focus:ring-primary-500"
                    />
                    <div className="flex items-center space-x-2">
                      <Lock className="h-4 w-4 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900">Private</p>
                        <p className="text-sm text-gray-500">Only you can access this book</p>
                      </div>
                    </div>
                  </label>
                  
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="sharing"
                      checked={isPublic}
                      onChange={() => setIsPublic(true)}
                      className="text-primary-600 focus:ring-primary-500"
                    />
                    <div className="flex items-center space-x-2">
                      <Share2 className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="font-medium text-gray-900">Public</p>
                        <p className="text-sm text-gray-500">Share with the community</p>
                      </div>
                    </div>
                  </label>
                </div>
              </CardContent>
            </Card>

            {/* Upload Guidelines */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Guidelines</CardTitle>
                <CardDescription>
                  Follow these guidelines for the best results
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Supported format: EPUB files only</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Maximum file size: 100MB</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Processing time: 5-15 minutes depending on book size</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>AI will extract characters, relationships, and build graphs</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* What Happens Next */}
            <Card>
              <CardHeader>
                <CardTitle>What Happens Next?</CardTitle>
                <CardDescription>
                  After uploading, our AI will:
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-xs font-bold">
                      1
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Analyze Text</p>
                      <p className="text-sm text-gray-600">Process the book content in chunks</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-xs font-bold">
                      2
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Extract Characters</p>
                      <p className="text-sm text-gray-600">Identify and profile all characters</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-xs font-bold">
                      3
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Build Relationships</p>
                      <p className="text-sm text-gray-600">Map character connections and interactions</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-xs font-bold">
                      4
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Create Visualizations</p>
                      <p className="text-sm text-gray-600">Generate interactive graphs and profiles</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 