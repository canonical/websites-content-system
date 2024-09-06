import { BasicApiClass } from "./BasicApiClass";

import { ENDPOINTS, REST_TYPES } from "@/services/api/constants";
import type { IPagesResponse } from "@/services/api/types/pages";
import { type IUser } from "@/services/api/types/users";

export class PagesApiClass extends BasicApiClass {
  public getPages(domain: string): Promise<IPagesResponse> {
    return this.callApi<IPagesResponse>(ENDPOINTS.getPagesTree(domain), REST_TYPES.GET);
  }

  public setOwner(user: IUser, webpageId: number): Promise<void> {
    return this.callApi(ENDPOINTS.setOwner, REST_TYPES.POST, {
      user_struct: user,
      webpage_id: webpageId,
    });
  }

  public setReviewers(users: IUser[], webpageId: number): Promise<void> {
    return this.callApi(ENDPOINTS.setReviewers, REST_TYPES.POST, {
      user_structs: users,
      webpage_id: webpageId,
    });
  }
}
