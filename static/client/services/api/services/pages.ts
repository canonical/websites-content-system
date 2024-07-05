import { api } from "@/services/api";
import type { IPagesResponse } from "@/services/api/types/pages";

export const getPages = async (domain: string): Promise<IPagesResponse> => {
  return api.pages.getPages(domain);
};

export * as PagesServices from "./pages";
