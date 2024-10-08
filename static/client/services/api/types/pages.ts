import type { IUser } from "./users";

export interface IPage {
  id?: number;
  name: string;
  title?: string;
  description?: string;
  link: string;
  owner: IUser;
  reviewers: IUser[];
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
  link: string | undefined;
  owner: IUser;
  reviewers: IUser[];
  project: string;
  parent: string;
}

export interface INewPageResponse {
  copy_doc: string;
}
