import type { IUser } from "./users";

export const PageStatus = {
  NEW: "NEW",
  AVAILABLE: "AVAILABLE",
  TO_DELETE: "TO_DELETE",
};

export interface IJiraTask {
  created_at: string;
  jira_id: string;
  id: number;
  name: string;
  status: string;
  summary: string;
}

export interface IPage {
  id?: number;
  name: string;
  title?: string;
  description?: string;
  copy_doc_link: string;
  owner: IUser;
  reviewers: IUser[];
  status: (typeof PageStatus)[keyof typeof PageStatus];
  jira_tasks: IJiraTask[];
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

export const ChangeRequestType = {
  COPY_UPDATE: 0,
  PAGE_REFRESH: 1,
  NEW_WEBPAGE: 2,
  PAGE_REMOVAL: 3,
};

export interface IRequestChanges {
  due_date: string;
  reporter_id: number;
  webpage_id: number;
  type: (typeof ChangeRequestType)[keyof typeof ChangeRequestType];
  summary?: string;
  description: string;
}

export interface IRequestRemoval {
  due_date: string;
  reporter_id: number;
  webpage_id: number;
  description: string;
}
