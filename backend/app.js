const API_URL = "http://localhost:8000";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }

  return response.json();
}

export async function getHome() {
  return request("/home", {
    method: "GET"
  });
}

export async function createIdentityAnchor(description) {
  return request("/identity_anchor", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

export async function createPrioritizationFilter(description) {
  return request("/prioritization_filter", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

export async function createDecisionContext(description) {
  return request("/decision_context", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

export async function createCapacitySnapshot(description) {
  return request("/capacity_snapshot", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

export async function createCommitmentCalibration(description) {
  return request("/commitment_calibration", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

export async function createCommitment(commitment, source) {
  return request("/commitment", {
    method: "POST",
    body: JSON.stringify({
      commitment,
      source
    })
  });
}

export async function reportExecution(commitment_id, outcome, prompt_response) {
  return request("/execution", {
    method: "POST",
    body: JSON.stringify({
      commitment_id,
      outcome,
      prompt_response
    })
  });
}