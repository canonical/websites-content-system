import type { IUser } from "./users";

export const PageStatus = {
  NEW: "NEW",
  AVAILABLE: "AVAILABLE",
  TO_DELETE: "TO_DELETE",
};

export interface IPage {
  id?: number;
  name: string;
  title?: string;
  description?: string;
  copy_doc_link: string;
  owner: IUser;
  reviewers: IUser[];
  status: (typeof PageStatus)[keyof typeof PageStatus];
  children: IPage[];
}

export interface IPagesResponse {
  data: {
    name: string;
    templates: IPage;
  };
}

export interface INewPage {
  name: string;
  copy_doc_link: string | undefined;
  owner: IUser;
  reviewers: IUser[];
  project: string;
  parent: string;
}

export interface INewPageResponse {
  copy_doc: string;
}
