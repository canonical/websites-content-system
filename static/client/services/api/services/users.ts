import { api } from "@/services/api";
import type { IUsersResponse } from "@/services/api/types/users";

export const getUsers = async (username: string): Promise<IUsersResponse> => {
  return api.users.getUsers(username);
};

export * as UsersServices from "./users";
