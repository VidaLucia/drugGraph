export type DrugConcept = {
  rxcui: string;
  name: string;
  term_type: string;
  synonym: string | null;
  source: string;
};

export type DrugGraphNode = {
  rxcui: string;
  name: string;
  term_type: string;
  synonym: string | null;
};

export type DrugGraphEdge = {
  source_rxcui: string;
  target_rxcui: string;
  relationship_type: string;
};

export type DrugGraph = {
  root: DrugGraphNode;
  nodes: DrugGraphNode[];
  edges: DrugGraphEdge[];
};