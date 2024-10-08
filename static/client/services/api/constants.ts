export const ENDPOINTS = {
  getPagesTree: (domain: string) => `/api/get-tree/${domain}`,
  getUsers: (inputStr: string) => `/api/get-users/${inputStr}`,
  setOwner: "/api/set-owner",
  setReviewers: "/api/set-reviewers",
  createNewPage: "/api/create-page",
};

export const REST_TYPES = {
  GET: "get",
  POST: "post",
  PUT: "put",
  DELETE: "delete",
  PATCH: "patch",
};
