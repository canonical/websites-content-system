import { BasicApiClass } from "./BasicApiClass";

import { ENDPOINTS, REST_TYPES } from "@/services/api/constants";
import type { IPagesResponse } from "@/services/api/types/pages";

export class PagesApiClass extends BasicApiClass {
  public getPages(domain: string): Promise<IPagesResponse> {
    return this.callApi<IPagesResponse>(ENDPOINTS.getPagesTree(domain), REST_TYPES.GET);
  }
}
