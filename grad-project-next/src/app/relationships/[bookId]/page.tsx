'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  Network, 
  Users, 
  Filter, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  ArrowLeft,
  BookOpen,
  Eye,
  EyeOff
} from 'lucide-react';
import { Relationship, Book, Character } from '@/types';
import { relationshipsApi, booksApi, charactersApi } from '@/lib/api';
import toast from 'react-hot-toast';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// Dynamically import react-force-graph to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph').then(mod => mod.ForceGraph2D), {
  ssr: false,
  loading: () => <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">Loading graph...</div>
});

interface GraphNode {
  id: string;
  name: string;
  group: number;
  val: number;
}

interface GraphLink {
  source: string;
  target: string;
  value: number;
  label: string;
  type: string;
}

export default function RelationshipGraphPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { isAuthenticated } = useAuthStore();
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRelationshipType, setSelectedRelationshipType] = useState<string>('all');
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({ nodes: [], links: [] });
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [showLabels, setShowLabels] = useState(true);
  const graphRef = useRef<any>();

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth';
      return;
    }

    fetchData();
  }, [bookId, isAuthenticated]);

  useEffect(() => {
    if (relationships.length > 0 && characters.length > 0) {
      buildGraphData();
    }
  }, [relationships, characters, selectedRelationshipType]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch book details
      const bookResponse = await booksApi.getBook(bookId);
      if (bookResponse.success) {
        setBook(bookResponse.data);
      }
      
      // Fetch relationships and characters
      const [relationshipsResponse, charactersResponse] = await Promise.all([
        relationshipsApi.getBookRelationships(bookId),
        charactersApi.getBookCharacters(bookId)
      ]);
      
      if (relationshipsResponse.success) {
        setRelationships(relationshipsResponse.data);
      }
      
      if (charactersResponse.success) {
        setCharacters(charactersResponse.data);
      }
    } catch (error: any) {
      toast.error('Failed to load relationship data');
      console.error('Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const buildGraphData = () => {
    const characterMap = new Map(characters.map(c => [c.id, c]));
    const nodes: GraphNode[] = [];
    const links: GraphLink[] = [];
    const nodeSet = new Set<string>();

    // Filter relationships by type
    const filteredRelationships = selectedRelationshipType === 'all' 
      ? relationships 
      : relationships.filter(r => r.relationshipType === selectedRelationshipType);

    // Create nodes
    filteredRelationships.forEach(relationship => {
      const sourceChar = characterMap.get(relationship.sourceCharacterId);
      const targetChar = characterMap.get(relationship.targetCharacterId);
      
      if (sourceChar && !nodeSet.has(sourceChar.id)) {
        nodes.push({
          id: sourceChar.id,
          name: sourceChar.name,
          group: 1,
          val: sourceChar.relationships.length
        });
        nodeSet.add(sourceChar.id);
      }
      
      if (targetChar && !nodeSet.has(targetChar.id)) {
        nodes.push({
          id: targetChar.id,
          name: targetChar.name,
          group: 1,
          val: targetChar.relationships.length
        });
        nodeSet.add(targetChar.id);
      }
    });

    // Create links
    filteredRelationships.forEach(relationship => {
      links.push({
        source: relationship.sourceCharacterId,
        target: relationship.targetCharacterId,
        value: relationship.strength,
        label: relationship.relationshipType,
        type: relationship.relationshipType
      });
    });

    setGraphData({ nodes, links });
  };

  const getRelationshipTypes = () => {
    const types = new Set(relationships.map(r => r.relationshipType));
    return Array.from(types).sort();
  };

  const handleNodeClick = (node: any) => {
    const nodeId = node.id;
    const connectedNodes = new Set();
    const connectedLinks = new Set();

    // Find all connected nodes and links
    graphData.links.forEach((link: any) => {
      if (link.source.id === nodeId || link.target.id === nodeId) {
        connectedLinks.add(link);
        connectedNodes.add(link.source.id);
        connectedNodes.add(link.target.id);
      }
    });

    setHighlightNodes(connectedNodes);
    setHighlightLinks(connectedLinks);
  };

  const handleBackgroundClick = () => {
    setHighlightNodes(new Set());
    setHighlightLinks(new Set());
  };

  const handleZoomIn = () => {
    graphRef.current?.zoom(1.5, 1000);
  };

  const handleZoomOut = () => {
    graphRef.current?.zoom(0.5, 1000);
  };

  const handleReset = () => {
    graphRef.current?.zoomToFit(1000);
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
                Relationship Graph
              </h1>
              {book && (
                <p className="text-gray-600">
                  Character relationships in "{book.title}" by {book.author}
                </p>
              )}
            </div>
            
            <div className="flex space-x-3">
              <Link href={`/characters/${bookId}`}>
                <Button variant="outline" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>View Characters</span>
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

        {/* Controls */}
        <div className="mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Filter className="h-4 w-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">Filter by type:</span>
                  </div>
                  <select
                    value={selectedRelationshipType}
                    onChange={(e) => setSelectedRelationshipType(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="all">All Relationships</option>
                    {getRelationshipTypes().map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowLabels(!showLabels)}
                    className="flex items-center space-x-1"
                  >
                    {showLabels ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    <span>Labels</span>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleZoomIn}
                    className="flex items-center space-x-1"
                  >
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleZoomOut}
                    className="flex items-center space-x-1"
                  >
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReset}
                    className="flex items-center space-x-1"
                  >
                    <RotateCcw className="h-4 w-4" />
                    <span>Reset</span>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Graph Container */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading relationship data...</p>
                </div>
              </div>
            ) : graphData.nodes.length === 0 ? (
              <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Network className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No relationships found</h3>
                  <p className="text-gray-600">
                    The AI is still processing this book. Relationships will appear here once analysis is complete.
                  </p>
                </div>
              </div>
            ) : (
              <div className="w-full h-96">
                <ForceGraph2D
                  ref={graphRef}
                  graphData={graphData}
                  nodeLabel={(node: any) => node.name}
                  linkLabel={(link: any) => `${link.label} (${Math.round(link.value * 100)}%)`}
                  nodeColor={(node: any) => 
                    highlightNodes.has(node.id) ? '#3b82f6' : '#6b7280'
                  }
                  linkColor={(link: any) => 
                    highlightLinks.has(link) ? '#3b82f6' : '#d1d5db'
                  }
                  linkWidth={(link: any) => 
                    highlightLinks.has(link) ? 3 : link.value * 2
                  }
                  nodeRelSize={6}
                  linkDirectionalParticles={2}
                  linkDirectionalParticleSpeed={0.005}
                  onNodeClick={handleNodeClick}
                  onBackgroundClick={handleBackgroundClick}
                  cooldownTicks={100}
                  nodeCanvasObject={(node: any, ctx, globalScale) => {
                        const label = node.name;
                        const fontSize = 12/globalScale;
                        ctx.font = `${fontSize}px Sans-Serif`;
                        const textWidth = ctx.measureText(label).width;
                        const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

                        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                        ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = highlightNodes.has(node.id) ? '#3b82f6' : '#374151';
                        ctx.fillText(label, node.x, node.y);

                        node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
                      }}
                  nodePointerAreaPaint={(node: any, color, ctx) => {
                        ctx.fillStyle = color;
                        const bckgDimensions = node.__bckgDimensions;
                        bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);
                      }}
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Graph Stats */}
        {graphData.nodes.length > 0 && (
          <div className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Graph Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{graphData.nodes.length}</p>
                    <p className="text-sm text-gray-600">Characters</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{graphData.links.length}</p>
                    <p className="text-sm text-gray-600">Relationships</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {getRelationshipTypes().length}
                    </p>
                    <p className="text-sm text-gray-600">Relationship Types</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {Math.round(graphData.links.reduce((sum, link) => sum + link.value, 0) / graphData.links.length * 100)}%
                    </p>
                    <p className="text-sm text-gray-600">Avg. Relationship Strength</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Legend */}
        {graphData.nodes.length > 0 && (
          <div className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">How to Use</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Interactions</h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• Click on a character to highlight their connections</li>
                      <li>• Drag to move the graph around</li>
                      <li>• Scroll to zoom in/out</li>
                      <li>• Use the controls above to filter and adjust view</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Visual Elements</h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• <span className="font-medium">Nodes:</span> Characters (size indicates relationship count)</li>
                      <li>• <span className="font-medium">Edges:</span> Relationships (thickness indicates strength)</li>
                      <li>• <span className="font-medium">Colors:</span> Highlighted connections are blue</li>
                      <li>• <span className="font-medium">Labels:</span> Hover to see relationship details</li>
                    </ul>
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