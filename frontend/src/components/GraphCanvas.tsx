import { useEffect } from "react";
import DrugNode from "./DrugNode";
import {
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from "d3-force";

import {
  Background,
  Controls,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import GraphLegend from "./GraphLegend";
import type { DrugGraph } from "../types/drug";

type GraphCanvasProps = {
  graph: DrugGraph | null;
  onNodeSelect: (node: Node) => void;
  onEdgeSelect: (edge: Edge) => void;
};
const nodeTypes = {
  drug: DrugNode,
};
const NODE_WIDTH = 220;
const NODE_HEIGHT = 80;

type ForceNode = SimulationNodeDatum & {
  id: string;
};

type ForceLink = SimulationLinkDatum<ForceNode>;

function createInitialLayout(
  nodes: Node[],
  edges: Edge[]
): Node[] {
  const width = 1200;
  const height = 800;

  const simulationNodes: ForceNode[] =
    nodes.map((node, index) => ({
      id: node.id,

      x:
        width / 2 +
        Math.cos(index) * 150,

      y:
        height / 2 +
        Math.sin(index) * 150,
    }));

  const simulationLinks: ForceLink[] =
    edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
    }));

  const simulation =
    forceSimulation<ForceNode>(
      simulationNodes
    )
      .force(
        "link",
        forceLink<
          ForceNode,
          ForceLink
        >(simulationLinks)
          .id((node) => node.id)
          .distance(250)
          .strength(0.7)
      )
      .force(
        "charge",
        forceManyBody().strength(-1000)
      )
      .force(
        "collision",
        forceCollide(150)
      )
      .stop();

  for (let i = 0; i < 300; i++) {
    simulation.tick();
  }

  return nodes.map((node) => {
    const forceNode =
      simulationNodes.find(
        (item) =>
          item.id === node.id
      );

    return {
      ...node,

      position: {
        x:
          (forceNode?.x ?? 0) -
          NODE_WIDTH / 2,

        y:
          (forceNode?.y ?? 0) -
          NODE_HEIGHT / 2,
      },
    };
  });
}

function layoutNewNodes(
  newNodes: Node[],
  existingNodes: Node[],
  edges: Edge[]
): Node[] {
  const existingMap = new Map(
    existingNodes.map((node) => [
      node.id,
      node,
    ])
  );

  const newNodeIds = new Set(
    newNodes.map((node) => node.id)
  );

  const allNodes = [
    ...existingNodes,
    ...newNodes,
  ];

  const forceNodes: ForceNode[] =
    allNodes.map((node) => {
      const existingNode =
        existingMap.get(node.id);

      // Existing node:
      // freeze it exactly where the user placed it.
      if (existingNode) {
        const centerX =
          existingNode.position.x +
          NODE_WIDTH / 2;

        const centerY =
          existingNode.position.y +
          NODE_HEIGHT / 2;

        return {
          id: node.id,

          x: centerX,
          y: centerY,

          fx: centerX,
          fy: centerY,
        };
      }

      // New node:
      // try to find an existing connected node
      // to use as its starting point.
      const connectingEdge =
        edges.find(
          (edge) =>
            (edge.target === node.id &&
              existingMap.has(
                edge.source
              )) ||
            (edge.source === node.id &&
              existingMap.has(
                edge.target
              ))
        );

      let anchorX = 600;
      let anchorY = 400;

      if (connectingEdge) {
        const connectedId =
          connectingEdge.target ===
          node.id
            ? connectingEdge.source
            : connectingEdge.target;

        const connectedNode =
          existingMap.get(
            connectedId
          );

        if (connectedNode) {
          anchorX =
            connectedNode.position.x +
            NODE_WIDTH / 2;

          anchorY =
            connectedNode.position.y +
            NODE_HEIGHT / 2;
        }
      }

      return {
        id: node.id,

        x:
          anchorX +
          (Math.random() - 0.5) *
            200,

        y:
          anchorY +
          (Math.random() - 0.5) *
            200,
      };
    });

  const forceLinks: ForceLink[] =
    edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
    }));

  const simulation =
    forceSimulation<ForceNode>(
      forceNodes
    )
      .force(
        "link",
        forceLink<
          ForceNode,
          ForceLink
        >(forceLinks)
          .id((node) => node.id)
          .distance(250)
          .strength(0.7)
      )
      .force(
        "charge",
        forceManyBody().strength(-900)
      )
      .force(
        "collision",
        forceCollide(150)
      )
      .stop();

  for (let i = 0; i < 250; i++) {
    simulation.tick();
  }

  return allNodes.map((node) => {
    // Don't touch manually positioned nodes.
    if (!newNodeIds.has(node.id)) {
      return node;
    }

    const forceNode =
      forceNodes.find(
        (item) =>
          item.id === node.id
      );

    return {
      ...node,

      position: {
        x:
          (forceNode?.x ?? 0) -
          NODE_WIDTH / 2,

        y:
          (forceNode?.y ?? 0) -
          NODE_HEIGHT / 2,
      },
    };
  });
}

export default function GraphCanvas({
  graph,
  onNodeSelect,
  onEdgeSelect,
}: GraphCanvasProps) {
  const [
    nodes,
    setNodes,
    onNodesChange,
  ] = useNodesState<Node>([]);

  const [
    edges,
    setEdges,
    onEdgesChange,
  ] = useEdgesState<Edge>([]);

  useEffect(() => {
    if (!graph) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const graphNodes: Node[] = [
      graph.root,
      ...graph.nodes,
    ].map((drug) => ({
      id: drug.rxcui,

      position: {
        x: 0,
        y: 0,
      },

      type: "drug",

    data: {
        label: drug.name,
        termType: drug.term_type,
        synonym: drug.synonym,
        isRoot:
            drug.rxcui === graph.root.rxcui,
    },

      style: {
        width: NODE_WIDTH,
        minHeight: NODE_HEIGHT,
      },

      className:
        "rounded-xl border border-slate-700 bg-slate-900 text-white shadow-lg",
    }));

    const graphEdges: Edge[] = graph.edges.map((edge) => ({
        id: `${edge.source_rxcui}-${edge.target_rxcui}-${edge.relationship_type}`,
        source: edge.source_rxcui,
        target: edge.target_rxcui,

        data: {
            relationshipType: edge.relationship_type,
        },

        type: "smoothstep",

        style: {
            strokeWidth: 2,
        },
        }));

    setEdges(graphEdges);

    setNodes((currentNodes) => {
      // First ever graph load.
      if (
        currentNodes.length === 0
      ) {
        return createInitialLayout(
          graphNodes,
          graphEdges
        );
      }

      const currentNodeMap =
        new Map(
          currentNodes.map(
            (node) => [
              node.id,
              node,
            ]
          )
        );

      // Keep current position,
      // but update node data/style from backend.
      const preservedNodes =
        graphNodes
          .filter((node) =>
            currentNodeMap.has(
              node.id
            )
          )
          .map((node) => {
            const current =
              currentNodeMap.get(
                node.id
              )!;

            return {
              ...node,

              position:
                current.position,
            };
          });

      // Find nodes we've never seen before.
      const newNodes =
        graphNodes.filter(
          (node) =>
            !currentNodeMap.has(
              node.id
            )
        );

      // No new nodes means don't
      // recalculate anything.
      if (
        newNodes.length === 0
      ) {
        return preservedNodes;
      }

      return layoutNewNodes(
        newNodes,
        preservedNodes,
        graphEdges
      );
    });
  }, [
    graph,
    setNodes,
    setEdges,
  ]);

  if (!graph) {
    return (
      <div className="flex h-full items-center justify-center text-slate-500">
        Search for a drug to begin exploring
      </div>
    );
  }

  return (<div className="relative h-full w-full">
  <ReactFlow
    nodes={nodes}
    edges={edges}
    nodeTypes={nodeTypes}
    onNodesChange={onNodesChange}
    onEdgesChange={onEdgesChange}
    onNodeClick={(_, node) => onNodeSelect(node)}
    onEdgeClick={(_, edge) => onEdgeSelect(edge)}
    nodesDraggable
    nodesConnectable={false}
    elementsSelectable
    fitView
  >
    <Background />
    <Controls />
  </ReactFlow>

  <GraphLegend />
</div>
  );
}