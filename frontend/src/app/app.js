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

/* -------------------------
HOME
------------------------- */

export function getHome() {
  return request("/home", { method: "GET" });
}

/* -------------------------
IDENTITY
------------------------- */

export function createIdentityAnchor(description) {
  return request("/identity_anchor", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

/* -------------------------
DECISION CONTEXT
------------------------- */

export function createDecisionContext(description) {
  return request("/decision_context", {
    method: "POST",
    body: JSON.stringify({ description })
  });
}

/* -------------------------
PRIORITIZATION FILTER
(no payload required)
------------------------- */

export function createPrioritizationFilter() {
  return request("/prioritization_filter", {
    method: "POST"
  });
}

/* -------------------------
CAPACITY SNAPSHOT
(payload depends on schema)
------------------------- */

export function createCapacitySnapshot(payload) {
  return request("/capacity_snapshot", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

/* -------------------------
COMMITMENT CALIBRATION
------------------------- */

export function createCommitmentCalibration(payload) {
  return request("/commitment_calibration", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

/* -------------------------
CREATE COMMITMENT
------------------------- */

export function createCommitment(commitment, source) {
  return request("/commitment", {
    method: "POST",
    body: JSON.stringify({
      commitment,
      source
    })
  });
}

/* -------------------------
EXECUTION
------------------------- */

export function reportExecution(commitment_id, outcome, prompt_response) {
  return request("/execution", {
    method: "POST",
    body: JSON.stringify({
      commitment_id,
      outcome,
      prompt_response
    })
  });
}

/* -------------------------
METRICS
------------------------- */

export function getFollowThroughRate() {
  return request("/metrics/follow-through-rate", {
    method: "GET"
  });
}

// export function getSelfLeadershipRate() {
//   return request("/metrics/self-leadership-rate", {
//     method: "GET"
//   });
// }
