export type DrugConcept = {
  rxcui: string;
  name: string;
  term_type: string;
  synonym: string | null;
  source: string;
};

export type DrugGraphNode = {
  id: string;
  name: string;
  node_type: "DRUG" | "CLASS";
  subtype: string;
  synonym: string | null;
  source: string;
};

export type DrugGraphEdge = {
  source_id: string;
  target_id: string;
  relationship_type: string | null;
  relationship_source: string | null;
};

export type DrugGraph = {
  root: DrugGraphNode;
  nodes: DrugGraphNode[];
  edges: DrugGraphEdge[];
};