import { AuthApiClass } from "./partials/AuthApiClass";
import { PagesApiClass } from "./partials/PagesApiClass";

class ApiClass {
  public pages: PagesApiClass;
  public auth: AuthApiClass;

  constructor() {
    this.pages = new PagesApiClass();
    this.auth = new AuthApiClass();
  }
}

export const api = new ApiClass();
