import type { Edge } from "@xyflow/react";
import type { DrugGraph } from "../types/drug";

type RelationshipDetailsPanelProps = {
  edge: Edge;
  graph: DrugGraph | null;
  onClose: () => void;
};

export default function RelationshipDetailsPanel({
  edge,
  graph,
  onClose,
}: RelationshipDetailsPanelProps) {
  const allNodes = graph
    ? [graph.root, ...graph.nodes]
    : [];

  const sourceNode = allNodes.find(
    (node) => node.id === edge.source
  );

  const targetNode = allNodes.find(
    (node) => node.id === edge.target
  );

  const relationship =
    String(edge.data?.relationshipType ?? "");

  return (
    <aside className="w-80 shrink-0 border-l border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Relationship
        </h2>

        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white"
        >
          ✕
        </button>
      </div>

      <div className="mt-8 space-y-6">

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Source
          </p>

          <p className="mt-1 text-sm font-medium text-white">
            {sourceNode?.name ?? edge.source}
          </p>

          <p className="mt-1 font-mono text-xs text-slate-500">
            {edge.source}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Relationship
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {relationship}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Target
          </p>

          <p className="mt-1 text-sm font-medium text-white">
            {targetNode?.name ?? edge.target}
          </p>

          <p className="mt-1 font-mono text-xs text-slate-500">
            {edge.target}
          </p>
        </div>

      </div>
    </aside>
  );
}