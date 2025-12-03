'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Star,
  Download,
  TrendingUp,
  Code,
  FileText,
  Database,
  Globe,
  Bot,
  Zap,
  Brain,
  MessageSquare,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: any;
  downloads: number;
  rating: number;
  price: 'free' | 'pro' | 'enterprise';
  tags: string[];
  author: string;
  featured?: boolean;
}

const templates: AgentTemplate[] = [
  {
    id: '1',
    name: 'Research Master',
    description: 'Advanced research agent with web scraping, data synthesis, and citation management',
    category: 'Research',
    icon: Globe,
    downloads: 12540,
    rating: 4.9,
    price: 'free',
    tags: ['research', 'web-scraping', 'data'],
    author: 'Suna Team',
    featured: true,
  },
  {
    id: '2',
    name: 'Code Reviewer Pro',
    description: 'Automated code review with best practices, security checks, and optimization suggestions',
    category: 'Development',
    icon: Code,
    downloads: 8920,
    rating: 4.8,
    price: 'pro',
    tags: ['code', 'review', 'security'],
    author: 'DevTools Inc',
    featured: true,
  },
  {
    id: '3',
    name: 'Content Writer AI',
    description: 'Generate blog posts, articles, and marketing copy with SEO optimization',
    category: 'Content',
    icon: FileText,
    downloads: 15320,
    rating: 4.7,
    price: 'free',
    tags: ['writing', 'content', 'seo'],
    author: 'ContentPro',
  },
  {
    id: '4',
    name: 'Data Analyst',
    description: 'Analyze datasets, create visualizations, and generate insights automatically',
    category: 'Analytics',
    icon: Database,
    downloads: 6780,
    rating: 4.6,
    price: 'pro',
    tags: ['data', 'analytics', 'visualization'],
    author: 'DataViz Studio',
  },
  {
    id: '5',
    name: 'Social Media Manager',
    description: 'Schedule posts, engage with followers, and analyze social media performance',
    category: 'Marketing',
    icon: MessageSquare,
    downloads: 9450,
    rating: 4.5,
    price: 'free',
    tags: ['social-media', 'marketing', 'automation'],
    author: 'SocialAI',
  },
  {
    id: '6',
    name: 'Smart Assistant',
    description: 'General-purpose assistant for task management, scheduling, and email handling',
    category: 'Productivity',
    icon: Bot,
    downloads: 18920,
    rating: 4.9,
    price: 'free',
    tags: ['assistant', 'productivity', 'automation'],
    author: 'Suna Team',
    featured: true,
  },
  {
    id: '7',
    name: 'Performance Optimizer',
    description: 'Monitor and optimize system performance, detect bottlenecks, suggest improvements',
    category: 'DevOps',
    icon: Zap,
    downloads: 5230,
    rating: 4.7,
    price: 'enterprise',
    tags: ['performance', 'optimization', 'monitoring'],
    author: 'OptimizePro',
  },
  {
    id: '8',
    name: 'ML Model Trainer',
    description: 'Automate machine learning model training, hyperparameter tuning, and deployment',
    category: 'AI/ML',
    icon: Brain,
    downloads: 4560,
    rating: 4.8,
    price: 'enterprise',
    tags: ['ml', 'ai', 'training'],
    author: 'ML Labs',
  },
];

const categories = ['All', 'Research', 'Development', 'Content', 'Analytics', 'Marketing', 'Productivity', 'DevOps', 'AI/ML'];

const priceColors = {
  free: 'bg-green-500/10 text-green-500',
  pro: 'bg-blue-500/10 text-blue-500',
  enterprise: 'bg-purple-500/10 text-purple-500',
};

function TemplateCard({ template }: { template: AgentTemplate }) {
  const Icon = template.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
    >
      <Card className="h-full flex flex-col hover:shadow-lg transition-shadow">
        <CardHeader>
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Icon className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-lg">{template.name}</CardTitle>
                <CardDescription className="text-xs">{template.author}</CardDescription>
              </div>
            </div>
            {template.featured && (
              <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-600">
                <Star className="w-3 h-3 mr-1 fill-yellow-600" />
                Featured
              </Badge>
            )}
          </div>
        </CardHeader>
        
        <CardContent className="flex-1">
          <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
            {template.description}
          </p>
          
          <div className="flex flex-wrap gap-1 mb-4">
            {template.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
          
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Download className="w-3 h-3" />
              <span>{template.downloads.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
              <span>{template.rating}</span>
            </div>
          </div>
        </CardContent>
        
        <CardFooter className="flex items-center justify-between pt-4 border-t">
          <Badge className={priceColors[template.price]} variant="secondary">
            {template.price === 'free' ? 'Free' : template.price.charAt(0).toUpperCase() + template.price.slice(1)}
          </Badge>
          <Button size="sm">
            <Download className="w-4 h-4 mr-2" />
            Install
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}

export function AgentMarketplace() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sortBy, setSortBy] = useState('featured');

  const filteredTemplates = templates
    .filter((template) => {
      const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      const matchesCategory = selectedCategory === 'All' || template.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortBy === 'featured') {
        if (a.featured && !b.featured) return -1;
        if (!a.featured && b.featured) return 1;
        return b.downloads - a.downloads;
      }
      if (sortBy === 'downloads') return b.downloads - a.downloads;
      if (sortBy === 'rating') return b.rating - a.rating;
      return 0;
    });

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search agents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="featured">Featured</SelectItem>
                <SelectItem value="downloads">Most Downloads</SelectItem>
                <SelectItem value="rating">Highest Rated</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          <span>{filteredTemplates.length} agents available</span>
        </div>
        <div className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          <span>
            {templates.reduce((sum, t) => sum + t.downloads, 0).toLocaleString()} total downloads
          </span>
        </div>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <TemplateCard key={template.id} template={template} />
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <Bot className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-lg font-medium mb-2">No agents found</p>
          <p className="text-sm text-muted-foreground">
            Try adjusting your search or filters
          </p>
        </div>
      )}
    </div>
  );
}
