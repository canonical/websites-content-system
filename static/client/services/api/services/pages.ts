import { api } from "@/services/api";
import type { IPagesResponse } from "@/services/api/types/pages";
import type { IUser } from "@/services/api/types/users";

export const getPages = async (domain: string): Promise<IPagesResponse> => {
  return api.pages.getPages(domain);
};

export const setOwner = async (user: IUser, webpageId: number): Promise<void> => {
  return api.pages.setOwner(user, webpageId);
};

export const setReviewers = async (users: IUser[], webpageId: number): Promise<void> => {
  return api.pages.setReviewers(users, webpageId);
};

export * as PagesServices from "./pages";
