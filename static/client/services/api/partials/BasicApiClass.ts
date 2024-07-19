import axios from "axios";

import config from "@/config";
import type { REST_TYPES } from "@/services/api/constants";

export class BasicApiClass {
  private basePath = "";
  private headers = {};
  private timeout = 0;

  constructor() {
    this.basePath = config.api.path;
    this.timeout = 5 * 60 * 1000;
    this.headers = {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    };
  }

  protected async callApi<T extends any>(
    to: string,
    type: (typeof REST_TYPES)[keyof typeof REST_TYPES],
    params?: any,
  ): Promise<T> {
    const instance = axios.create({
      baseURL: this.basePath,
      timeout: this.timeout,
      headers: this.headers,
    });

    return instance({
      method: type,
      url: to,
      withCredentials: false,
      ...(params ? { data: params } : {}),
    });
  }
}
