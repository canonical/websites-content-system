import { PagesApiClass } from "./partials/PagesApiClass";
import { UsersApiClass } from "./partials/UsersApiClass";

class ApiClass {
  public pages: PagesApiClass;
  public users: UsersApiClass;

  constructor() {
    this.pages = new PagesApiClass();
    this.users = new UsersApiClass();
  }
}

export const api = new ApiClass();
