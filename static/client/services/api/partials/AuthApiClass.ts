import { BasicApiClass } from "./BasicApiClass";

import { ENDPOINTS, REST_TYPES } from "@/services/api/constants";

export class AuthApiClass extends BasicApiClass {
  public login(url: string) {
    return this.callApi(ENDPOINTS.login(url), REST_TYPES.GET);
  }
}
