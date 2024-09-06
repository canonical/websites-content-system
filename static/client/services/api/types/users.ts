export interface IUser {
  id: number;
  name: string;
  email: string;
  jobTitle: string;
  department: string;
  team: string;
}

export interface IUsersResponse {
  data: IUser[];
}
