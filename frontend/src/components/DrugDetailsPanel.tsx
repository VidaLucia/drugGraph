import type { Node } from "@xyflow/react";

type DrugDetailsPanelProps = {
  node: Node;
  onClose: () => void;
  onExpand: (id: string) => void;
  expanding: boolean;
  isExpanded: boolean;
};

export default function DrugDetailsPanel({
  node,
  onClose,
  onExpand,
  expanding,
  isExpanded,
}: DrugDetailsPanelProps) {
  const nodeType = String(node.data.nodeType);
  const isDrug = nodeType === "DRUG";

  return (
    <aside className="w-80 shrink-0 border-l border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {isDrug ? "Drug Details" : "Class Details"}
        </h2>

        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white"
        >
          ✕
        </button>
      </div>

      <div className="mt-8 space-y-5">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Name
          </p>

          <p className="mt-1 text-sm text-white">
            {String(node.data.label)}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            {isDrug ? "RxCUI" : "Class ID"}
          </p>

          <p className="mt-1 font-mono text-sm text-slate-300">
            {node.id}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Type
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {String(node.data.termType)}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Source
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {String(node.data.source)}
          </p>
        </div>
      </div>

      {isDrug && (
        <button
          onClick={() => onExpand(node.id)}
          disabled={expanding || isExpanded}
          className="mt-8 w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-sm font-medium transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isExpanded
            ? "Expanded"
            : expanding
              ? "Expanding..."
              : "Expand Node"}
        </button>
      )}
    </aside>
  );
}