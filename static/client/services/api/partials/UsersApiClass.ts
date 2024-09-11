import { BasicApiClass } from "./BasicApiClass";

import { ENDPOINTS, REST_TYPES } from "@/services/api/constants";
import { type IUsersResponse } from "@/services/api/types/users";

export class UsersApiClass extends BasicApiClass {
  public getUsers(username: string): Promise<IUsersResponse> {
    return this.callApi<IUsersResponse>(ENDPOINTS.getUsers(username), REST_TYPES.GET);
  }
}
