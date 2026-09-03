import { useState } from "react";
import type { Edge, Node } from "@xyflow/react";

import Sidebar from "../components/Sidebar";
import GraphCanvas from "../components/GraphCanvas";
import DrugDetailsPanel from "../components/DrugDetailsPanel";
import RelationshipDetailsPanel from "../components/RelationshipDetailsPanel";
import {
  expandDrug,
  getDrugGraph,
  ingestDrug,
} from "../api/drugs";

import type {
  DrugGraph,
  DrugGraphNode,
  DrugGraphEdge,
} from "../types/drug";

export default function DrugExplorerPage() {
  const [graph, setGraph] =
    useState<DrugGraph | null>(null);
  
  const [expanding, setExpanding] =
    useState(false);

  const [selectedNode, setSelectedNode] =
    useState<Node | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);
  const [selectedEdge, setSelectedEdge] =
    useState<Edge | null>(null);
  function mergeGraphs(
    current: DrugGraph,
    incoming: DrugGraph
  ): DrugGraph {
    const nodeMap =
      new Map<string, DrugGraphNode>();

    [
      current.root,
      ...current.nodes,
      incoming.root,
      ...incoming.nodes,
    ].forEach((node) => {
      nodeMap.set(
        node.id,
        node
      );
    });

    const edgeMap =
      new Map<string, DrugGraphEdge>();

    [
      ...current.edges,
      ...incoming.edges,
    ].forEach((edge) => {
      const key =
        `${edge.source_id}-${edge.target_id}-${edge.relationship_type}-${edge.relationship_source}`;
        edgeMap.set(
        key,
        edge
      );
    });

    return {
      root: current.root,

      nodes: Array.from(
        nodeMap.values()
      ).filter(
        (node) =>
          node.id !==
          current.root.id
      ),

      edges: Array.from(
        edgeMap.values()
      ),
    };
  }

  async function handleSearch(
    name: string
  ) {
    try {
      setLoading(true);
      setError(null);
      setSelectedNode(null);

      const drug =
        await ingestDrug(name);

      const graphData =
        await getDrugGraph(
          drug.rxcui
        );

      setGraph(graphData);
    } catch (error) {
      console.error(error);

      setError(
        "Unable to load drug graph."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleExpand(
  id: string
) {
  try {
    setExpanding(true);
    setError(null);

    await expandDrug(id);

    const expandedGraph =
      await getDrugGraph(id);

    setGraph((currentGraph) => {
      if (!currentGraph) {
        return expandedGraph;
      }

      const merged =
        mergeGraphs(
          currentGraph,
          expandedGraph
        );

      return merged;
    });

  } catch (error) {
    console.error(error);

    if (error instanceof Error) {
      setError(error.message);
    } else {
      setError(
        "Unable to expand node."
      );
    }
  } finally {
    setExpanding(false);
  }
}
  function handleNodeSelect(node: Node) {
    setSelectedNode(node);
    setSelectedEdge(null);
  }
  function handleEdgeSelect(edge: Edge) {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }
  return (
    <div className="flex h-screen w-screen bg-slate-950 text-white">
      <Sidebar
        onSearch={handleSearch}
        loading={loading}
      />

      <main className="relative min-w-0 flex-1">
        {error && (
          <div className="absolute left-1/2 top-6 z-10 -translate-x-1/2 rounded-lg border border-red-900 bg-red-950 px-4 py-2 text-sm text-red-200">
            {error}
          </div>
        )}

        <GraphCanvas
          graph={graph}
          onNodeSelect={handleNodeSelect}
          onEdgeSelect={handleEdgeSelect}
        />
      </main>

      {selectedNode && (
        <DrugDetailsPanel
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
            onExpand={handleExpand}
            expanding={expanding}
        />
        )}

        {selectedEdge && (
        <RelationshipDetailsPanel
            edge={selectedEdge}
            graph={graph}
            onClose={() =>
                setSelectedEdge(null)
            }
        />
        )}
    </div>
  );
}