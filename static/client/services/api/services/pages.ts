import { api } from "@/services/api";
import type {
  INewPage,
  INewPageResponse,
  IPagesResponse,
  IRequestChanges,
  IRequestRemoval,
} from "@/services/api/types/pages";
import type { IUser } from "@/services/api/types/users";

export const getPages = async (domain: string, noCache?: boolean): Promise<IPagesResponse> => {
  return api.pages.getPages(domain, noCache);
};

export const setOwner = async (user: IUser | {}, webpageId: number): Promise<void> => {
  return api.pages.setOwner(user, webpageId);
};

export const setReviewers = async (users: IUser[], webpageId: number): Promise<void> => {
  return api.pages.setReviewers(users, webpageId);
};

export const createPage = async (page: INewPage): Promise<INewPageResponse> => {
  return api.pages.createPage(page);
};

export const requestChanges = async (body: IRequestChanges): Promise<void> => {
  return api.pages.requestChanges(body);
};

export const requestRemoval = async (body: IRequestRemoval): Promise<void> => {
  return api.pages.requestRemoval(body);
};

export * as PagesServices from "./pages";
