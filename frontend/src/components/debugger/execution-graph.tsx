"use client";

import { useEffect, useState } from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ExecutionGraphProps {
  taskId: string;
}

interface GraphNode {
  id: string;
  type: string;
  data: {
    label: string;
    status: string;
    timestamp: string;
    details?: any;
  };
  position: { x: number; y: number };
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

const nodeColors: Record<string, string> = {
  start: "#10b981",
  thinking: "#8b5cf6",
  decision: "#f59e0b",
  tool_call: "#3b82f6",
  output: "#06b6d4",
  error: "#ef4444",
  end: "#6366f1",
};

export function ExecutionGraph({ taskId }: ExecutionGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const response = await fetch(`/api/tasks/${taskId}/graph`);
        if (response.ok) {
          const data = await response.json();
          
          // Convert graph data to ReactFlow format
          const flowNodes: Node[] = data.nodes.map((node: GraphNode) => ({
            id: node.id,
            type: "default",
            data: {
              label: node.data.label,
            },
            position: node.position,
            style: {
              background: nodeColors[node.type] || "#94a3b8",
              color: "white",
              border: node.data.status === "current" ? "3px solid #fbbf24" : "none",
              padding: 10,
              borderRadius: 8,
              fontSize: 12,
              fontWeight: 500,
            },
          }));

          const flowEdges: Edge[] = data.edges.map((edge: GraphEdge) => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.label,
            type: "smoothstep",
            animated: true,
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          }));

          setNodes(flowNodes);
          setEdges(flowEdges);
        }
      } catch (error) {
        console.error("Failed to fetch execution graph:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGraph();
  }, [taskId, setNodes, setEdges]);

  const onNodeClick = (_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node as any);
  };

  if (isLoading) {
    return (
      <div className="h-[600px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading execution graph...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[600px]">
      <div className="lg:col-span-2 border rounded-lg overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          fitView
        >
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const style = node.style as any;
              return style?.background || "#94a3b8";
            }}
            maskColor="rgba(0, 0, 0, 0.2)"
          />
          <Background gap={12} size={1} />
        </ReactFlow>
      </div>
      <div className="lg:col-span-1">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Node Details</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedNode ? (
              <ScrollArea className="h-[500px]">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Type
                    </label>
                    <Badge className="mt-1">
                      {selectedNode.type || "Unknown"}
                    </Badge>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Label
                    </label>
                    <p className="mt-1 font-medium">
                      {selectedNode.data.label}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Status
                    </label>
                    <p className="mt-1">{selectedNode.data.status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Timestamp
                    </label>
                    <p className="mt-1">
                      {new Date(
                        selectedNode.data.timestamp
                      ).toLocaleString()}
                    </p>
                  </div>
                  {selectedNode.data.details && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">
                        Details
                      </label>
                      <pre className="mt-1 text-xs bg-muted p-2 rounded overflow-auto">
                        {JSON.stringify(selectedNode.data.details, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                Click on a node to view details
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
