import type { Node } from "@xyflow/react";

type DrugDetailsPanelProps = {
  node: Node;
  onClose: () => void;
  onExpand: (rxcui: string) => void;
  expanding: boolean;
};

export default function DrugDetailsPanel({
  node,
  onClose,
  onExpand,
  expanding,
}: DrugDetailsPanelProps) {
  return (
    <aside className="w-80 shrink-0 border-l border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Drug Details
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
            RxCUI
          </p>

          <p className="mt-1 font-mono text-sm text-slate-300">
            {node.id}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Term Type
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {String(node.data.termType)}
          </p>
        </div>
      </div>

      <button
        onClick={() => onExpand(node.id)}
        disabled={expanding}
        className="mt-8 w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-sm font-medium transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {expanding ? "Expanding..." : "Expand Node"}
      </button>
    </aside>
  );
}