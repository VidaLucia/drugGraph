import type { DrugGraph } from "../types/drug";
type GraphFilterPanelProps = {
  graph: DrugGraph | null;
  drugSubtypes: Set<string>;
  classSubtypes: Set<string>;
  onToggleDrugSubtype: (subtype: string) => void;
  onToggleClassSubtype: (subtype: string) => void;
};

const DRUG_FILTERS = [
  { subtype: "IN", label: "Ingredients" },
  { subtype: "PIN", label: "Precise Ingredients" },
  { subtype: "BN", label: "Brands" },
  { subtype: "SCD", label: "Clinical Drugs" },
  { subtype: "SBD", label: "Branded Drugs" },
  { subtype: "SCDC", label: "Drug Components" },
  { subtype: "SCDF", label: "Dose Forms" },
  { subtype: "SCDG", label: "Drug Groups" },
];

const CLASS_FILTERS = [
  { subtype: "ATC1-4", label: "ATC Classes" },
  { subtype: "MOA", label: "Mechanism of Action" },
  { subtype: "EPC", label: "Pharmacologic Class" },
  { subtype: "PE", label: "Physiologic Effect" },
];

export default function GraphFilterPanel({
  graph,
  drugSubtypes,
  classSubtypes,
  onToggleDrugSubtype,
  onToggleClassSubtype,
}: GraphFilterPanelProps) {
    const allNodes = graph? [graph.root, ...graph.nodes]: [];
  function getCount(
    nodeType: "DRUG" | "CLASS",
    subtype: string
  ) {
    return allNodes.filter(
      (node) =>
        node.node_type === nodeType &&
        node.subtype === subtype
    ).length;
  }
  return (
    <div className="absolute left-4 top-4 z-10 w-64 rounded-xl border border-slate-800 bg-slate-900/95 p-4 shadow-xl">
      <h2 className="text-sm font-semibold text-white">
        Graph Filters
      </h2>

      <div className="mt-4">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          Drug Concepts
        </p>

        <div className="mt-2 space-y-2">
          {DRUG_FILTERS.map((filter) => (
            <label
              key={filter.subtype}
              className="flex cursor-pointer items-center gap-2 text-sm text-slate-300"
            >
              <input
                type="checkbox"
                checked={drugSubtypes.has(filter.subtype)}
                onChange={() =>
                  onToggleDrugSubtype(filter.subtype)
                }
              />

              <span className="flex flex-1 items-center justify-between gap-2">
                <span>{filter.label}</span>

                <span className="text-xs tabular-nums text-slate-500">
                  {getCount("DRUG", filter.subtype)}
                </span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="mt-5">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          Drug Classes
        </p>

        <div className="mt-2 space-y-2">
          {CLASS_FILTERS.map((filter) => (
            <label
              key={filter.subtype}
              className="flex cursor-pointer items-center gap-2 text-sm text-slate-300"
            >
              <input
                type="checkbox"
                checked={classSubtypes.has(filter.subtype)}
                onChange={() =>
                  onToggleClassSubtype(filter.subtype)
                }
              />

              <span className="flex flex-1 items-center justify-between gap-2">
                <span>{filter.label}</span>

                <span className="text-xs tabular-nums text-slate-500">
                  {getCount("CLASS", filter.subtype)}
                </span>
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}