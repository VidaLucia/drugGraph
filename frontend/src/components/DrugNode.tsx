import {
  Handle,
  Position,
  type NodeProps,
} from "@xyflow/react";

export type DrugNodeData = {
  label: string;
  termType: string;
  nodeType: "DRUG" | "CLASS";
  source: string;
  synonym?: string | null;
  isRoot?: boolean;
};

const TERM_TYPE_LABELS: Record<string, string> = {
  IN: "Ingredient",
  PIN: "Precise Ingredient",
  BN: "Brand",
  SCD: "Clinical Drug",
  SBD: "Branded Drug",
  SCDG: "Clinical Drug Group",
  SBDG: "Branded Drug Group",
  SCDF: "Clinical Drug Form",
  SBDF: "Branded Drug Form",
  DFG: "Dose Form Group",
  DF: "Dose Form",

  "ATC1-4": "ATC Class",
  MOA: "Mechanism of Action",
  EPC: "Pharmacologic Class",
  PE: "Physiologic Effect",
};

const TERM_TYPE_STYLES: Record<string, string> = {
  IN: "border-emerald-500/60 bg-emerald-950",
  PIN: "border-teal-500/60 bg-teal-950",

  BN: "border-purple-500/60 bg-purple-950",

  SCD: "border-blue-500/60 bg-blue-950",
  SCDG: "border-sky-500/60 bg-sky-950",
  SCDF: "border-cyan-500/60 bg-cyan-950",

  SBD: "border-violet-500/60 bg-violet-950",
  SBDG: "border-fuchsia-500/60 bg-fuchsia-950",
  SBDF: "border-pink-500/60 bg-pink-950",

  DFG: "border-amber-500/60 bg-amber-950",
  DF: "border-orange-500/60 bg-orange-950",

  "ATC1-4": "border-yellow-500/60 bg-yellow-950",
  MOA: "border-red-500/60 bg-red-950",
  EPC: "border-indigo-500/60 bg-indigo-950",
  PE: "border-lime-500/60 bg-lime-950",
};

export default function DrugNode({
  data,
  selected,
}: NodeProps) {
  const drugData =
    data as DrugNodeData;
  const isClass =
    drugData.nodeType === "CLASS";
  const typeStyle =
    TERM_TYPE_STYLES[
      drugData.termType
    ] ??
    "border-slate-600 bg-slate-900";

  const typeLabel =
    TERM_TYPE_LABELS[
      drugData.termType
    ] ??
    drugData.termType;

  return (
    <div
      className={`
        min-w-[220px]
        max-w-[260px]
        rounded-2xl
        border
        px-4
        py-3
        shadow-lg
        transition
        ${typeStyle}
        ${
          selected
            ? "ring-2 ring-white/70"
            : ""
        }
        ${
          drugData.isRoot
            ? "ring-2 ring-slate-300"
            : ""
        }
      `}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="opacity-0"
      />

      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            {typeLabel}
        </span>

        <div className="flex items-center gap-2">
            {isClass && (
            <span className="rounded-md border border-slate-600 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-slate-300">
                Class
            </span>
            )}

            <span className="font-mono text-[10px] text-slate-500">
            {drugData.termType}
            </span>
        </div>
    </div>

      <div className="mt-2 break-words text-sm font-semibold text-white">
        {drugData.label}
      </div>

      {drugData.synonym && (
        <div className="mt-1 truncate text-xs text-slate-400">
          {drugData.synonym}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="opacity-0"
      />
    </div>
  );
}