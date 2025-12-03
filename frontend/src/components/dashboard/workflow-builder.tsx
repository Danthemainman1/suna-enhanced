'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  Plus,
  Save,
  Download,
  Upload,
  Trash2,
  Settings,
  GitBranch,
  ArrowRight,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface WorkflowNode {
  id: string;
  type: 'trigger' | 'agent' | 'condition' | 'action';
  label: string;
  agentType?: string;
  config?: any;
  x: number;
  y: number;
}

interface Connection {
  from: string;
  to: string;
}

const agentTypes = [
  'ResearchAgent',
  'CodeAgent',
  'DataAgent',
  'WriterAgent',
  'PlannerAgent',
  'CriticAgent',
  'ExecutorAgent',
  'MemoryAgent',
];

const nodeColors = {
  trigger: 'bg-green-500/10 border-green-500',
  agent: 'bg-blue-500/10 border-blue-500',
  condition: 'bg-yellow-500/10 border-yellow-500',
  action: 'bg-purple-500/10 border-purple-500',
};

function WorkflowNode({ node, onDelete }: { node: WorkflowNode; onDelete: () => void }) {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      style={{
        position: 'absolute',
        left: node.x,
        top: node.y,
      }}
      className="cursor-move"
    >
      <Card className={`w-48 ${nodeColors[node.type]} border-2`}>
        <CardHeader className="p-4 pb-2">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <Badge variant="secondary" className="mb-2 text-xs">
                {node.type}
              </Badge>
              <CardTitle className="text-sm">{node.label}</CardTitle>
              {node.agentType && (
                <p className="text-xs text-muted-foreground mt-1">{node.agentType}</p>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={onDelete}
            >
              <Trash2 className="w-3 h-3" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <Button variant="ghost" size="sm" className="w-full text-xs">
            <Settings className="w-3 h-3 mr-1" />
            Configure
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function WorkflowBuilder() {
  const [nodes, setNodes] = useState<WorkflowNode[]>([
    {
      id: '1',
      type: 'trigger',
      label: 'Webhook Trigger',
      x: 50,
      y: 50,
    },
    {
      id: '2',
      type: 'agent',
      label: 'Research Task',
      agentType: 'ResearchAgent',
      x: 50,
      y: 200,
    },
    {
      id: '3',
      type: 'agent',
      label: 'Generate Report',
      agentType: 'WriterAgent',
      x: 50,
      y: 350,
    },
  ]);

  const [connections] = useState<Connection[]>([
    { from: '1', to: '2' },
    { from: '2', to: '3' },
  ]);

  const addNode = (type: WorkflowNode['type']) => {
    // Grid-based positioning to avoid overlaps
    const gridSize = 200;
    const column = nodes.length % 3;
    const row = Math.floor(nodes.length / 3);
    
    const newNode: WorkflowNode = {
      id: `${Date.now()}`,
      type,
      label: `New ${type}`,
      x: 50 + (column * gridSize),
      y: 50 + (row * gridSize),
    };
    setNodes([...nodes, newNode]);
  };

  const deleteNode = (id: string) => {
    setNodes(nodes.filter((n) => n.id !== id));
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button size="sm" onClick={() => addNode('trigger')}>
                <Plus className="w-4 h-4 mr-2" />
                Trigger
              </Button>
              <Button size="sm" onClick={() => addNode('agent')}>
                <Plus className="w-4 h-4 mr-2" />
                Agent
              </Button>
              <Button size="sm" onClick={() => addNode('condition')}>
                <Plus className="w-4 h-4 mr-2" />
                Condition
              </Button>
              <Button size="sm" onClick={() => addNode('action')}>
                <Plus className="w-4 h-4 mr-2" />
                Action
              </Button>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Upload className="w-4 h-4 mr-2" />
                Import
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Save className="w-4 h-4 mr-2" />
                Save
              </Button>
              <Button size="sm">
                <Play className="w-4 h-4 mr-2" />
                Run
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Canvas */}
      <Card className="h-[600px] relative overflow-hidden">
        <CardContent className="p-0 h-full">
          {/* Grid background */}
          <div
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage: `
                linear-gradient(rgba(0, 0, 0, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 0, 0, 0.1) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px',
            }}
          />

          {/* Connections */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {connections.map((conn, index) => {
              const fromNode = nodes.find((n) => n.id === conn.from);
              const toNode = nodes.find((n) => n.id === conn.to);
              if (!fromNode || !toNode) return null;

              const fromX = fromNode.x + 96; // Half of card width
              const fromY = fromNode.y + 80; // Bottom of card
              const toX = toNode.x + 96;
              const toY = toNode.y + 20; // Top of card

              return (
                <g key={index}>
                  <defs>
                    <marker
                      id={`arrowhead-${index}`}
                      markerWidth="10"
                      markerHeight="10"
                      refX="9"
                      refY="3"
                      orient="auto"
                    >
                      <polygon
                        points="0 0, 10 3, 0 6"
                        fill="currentColor"
                        className="text-muted-foreground"
                      />
                    </marker>
                  </defs>
                  <path
                    d={`M ${fromX} ${fromY} L ${toX} ${toY}`}
                    stroke="currentColor"
                    strokeWidth="2"
                    fill="none"
                    markerEnd={`url(#arrowhead-${index})`}
                    className="text-muted-foreground"
                  />
                </g>
              );
            })}
          </svg>

          {/* Nodes */}
          <div className="relative w-full h-full">
            {nodes.map((node) => (
              <WorkflowNode
                key={node.id}
                node={node}
                onDelete={() => deleteNode(node.id)}
              />
            ))}
          </div>

          {/* Empty State */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <GitBranch className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">Start Building Your Workflow</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Add triggers, agents, and actions to create your automation
                </p>
                <Button onClick={() => addNode('trigger')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Node
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Workflow Information</CardTitle>
        </CardHeader>
        <CardContent className="text-sm">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-muted-foreground mb-1">Total Nodes</p>
              <p className="text-2xl font-bold">{nodes.length}</p>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Connections</p>
              <p className="text-2xl font-bold">{connections.length}</p>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Status</p>
              <Badge variant="secondary" className="mt-1">
                Draft
              </Badge>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Last Modified</p>
              <p className="text-sm">Just now</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
