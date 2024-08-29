import { type IPagesResponse } from "@/services/api/types/pages";

export interface IStore {
  selectedProject: IPagesResponse["data"] | null;
  user: string | null;
  setSelectedProject: (s: IPagesResponse["data"]) => void;
  setUser: (u: string) => void;
}
