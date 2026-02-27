"use client";

import ProtectedRoute from "@/components/ProtectedRoute";
import { useHomeState } from "@/hooks/useHomeState";

import NoIdentity from "@/states/NoIdentity";
import NoDecision from "@/states/NoDecision";
import NoCommitment from "@/states/NoCommitment";
import LimitReached from "@/states/LimitReached";
import ActiveCommitments from "@/states/ActiveCommitments";

export default function Home() {
  const { data, isLoading } = useHomeState();

  if (isLoading) return <div>Loading...</div>;

  const state = data.state;

  return (
    <ProtectedRoute>
      {state === "no_identity" && <NoIdentity />}
      {state === "no_decision" && <NoDecision />}
      {state === "no_commitment" && <NoCommitment />}
      {state === "limit_reached" && <LimitReached />}
      {state === "active_commitments" && (
        <ActiveCommitments data={data} />
      )}
    </ProtectedRoute>
  );
}
