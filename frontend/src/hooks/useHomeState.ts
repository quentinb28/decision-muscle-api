import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export const useHomeState = () => {
  return useQuery({
    queryKey: ["home"],
    queryFn: async () => {
      const res = await api.get("/home");
      return res.data;
    },
  });
};
