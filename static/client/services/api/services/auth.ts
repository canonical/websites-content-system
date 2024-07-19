import { api } from "..";

export const login = (url: string) => {
  return api.auth.login(url);
};

export * as AuthServices from "./auth";
