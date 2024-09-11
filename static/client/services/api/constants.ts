export const ENDPOINTS = {
  getPagesTree: (domain: string) => `/get-tree/${domain}`,
  getUsers: (inputStr: string) => `/get-users/${inputStr}`,
  setOwner: "/set-owner",
  setReviewers: "/set-reviewers",
};

export const REST_TYPES = {
  GET: "get",
  POST: "post",
  PUT: "put",
  DELETE: "delete",
  PATCH: "patch",
};
