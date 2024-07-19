export const ENDPOINTS = {
  getPagesTree: (domain: string) => `/get-tree/${domain}`,
  login: (url: string) => `/login?next=${url}`,
};

export const REST_TYPES = {
  GET: "get",
  POST: "post",
  PUT: "put",
  DELETE: "delete",
  PATCH: "patch",
};
