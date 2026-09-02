import type {
  DrugConcept,
  DrugGraph,
} from "../types/drug";

const API_BASE_URL = "http://localhost:8000";

export async function ingestDrug(
  name: string
): Promise<DrugConcept> {
  const response = await fetch(
    `${API_BASE_URL}/drugs/ingest?name=${encodeURIComponent(name)}`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to ingest drug");
  }

  return response.json();
}

export async function getDrugGraph(
  rxcui: string
): Promise<DrugGraph> {
  const response = await fetch(
    `${API_BASE_URL}/drugs/${rxcui}/graph`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch drug graph");
  }

  return response.json();
}

export async function expandDrug(
  rxcui: string
): Promise<DrugConcept> {
  const response = await fetch(
    `${API_BASE_URL}/drugs/${rxcui}/expand`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const body = await response.text();

    throw new Error(
      `Expand failed: ${response.status} ${body}`
    );
  }

  return response.json();
}