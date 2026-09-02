const LEGEND_ITEMS = [
  { label: "Ingredient", className: "bg-emerald-950 border-emerald-500/60" },
  { label: "Brand", className: "bg-purple-950 border-purple-500/60" },
  { label: "Clinical Drug", className: "bg-blue-950 border-blue-500/60" },
  { label: "Branded Drug", className: "bg-violet-950 border-violet-500/60" },
  { label: "Dose Form", className: "bg-orange-950 border-orange-500/60" },
];

export default function GraphLegend() {
  return (
    <div className="absolute bottom-4 left-4 z-10 rounded-xl border border-slate-800 bg-slate-900/95 p-3 shadow-lg">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
        Node Types
      </p>

      <div className="space-y-2">
        {LEGEND_ITEMS.map((item) => (
          <div
            key={item.label}
            className="flex items-center gap-2 text-xs text-slate-300"
          >
            <span
              className={`h-3 w-3 rounded-full border ${item.className}`}
            />
            {item.label}
          </div>
        ))}
      </div>
    </div>
  );
}