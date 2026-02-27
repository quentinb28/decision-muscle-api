"use client";

import { api } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

export default function NoIdentityAnchor() {
  const [text, setText] = useState("");
  const qc = useQueryClient();

  const mutation = useMutation({
    mutationFn: () =>
      api.post("/identity_anchor", { text }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["home"] });
    },
  });

  return (
    <div>
      <h2>Create Identity Anchor</h2>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={() => mutation.mutate()}>
        Submit
      </button>
    </div>
  );
}
