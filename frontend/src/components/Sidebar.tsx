import { useState } from "react";

type SidebarProps = {
  onSearch: (name: string) => void;
  loading: boolean;
};

export default function Sidebar({
  onSearch,
  loading,
}: SidebarProps) {
  const [query, setQuery] = useState("");

  function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const trimmed = query.trim();

    if (!trimmed) {
      return;
    }

    onSearch(trimmed);
  }

  return (
    <aside className="w-72 shrink-0 border-r border-slate-800 bg-slate-900 p-5">
      <h1 className="text-2xl font-semibold">
        DrugGraph
      </h1>

      <p className="mt-1 text-sm text-slate-400">
        Pharmaceutical knowledge graph
      </p>

      <form
        onSubmit={handleSubmit}
        className="mt-8"
      >
        <label className="mb-2 block text-sm text-slate-400">
          Search drug
        </label>

        <input
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          type="text"
          placeholder="Metoprolol..."
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none placeholder:text-slate-600 focus:border-slate-500"
        />

        <button
          type="submit"
          disabled={loading}
          className="mt-3 w-full rounded-xl bg-slate-100 px-4 py-3 text-sm font-medium text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Loading..." : "Search"}
        </button>
      </form>
    </aside>
  );
}