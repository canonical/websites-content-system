import type { ChangeEvent, Dispatch, SetStateAction } from "react";

import type { IPage } from "@/services/api/types/pages";
import type { IUser } from "@/services/api/types/users";

export interface IOwnerAndReviewersProps {
  page: IPage;
}

export interface ICustomSearchAndFilterProps {
  label: string;
  options: IUser[];
  selectedOptions: IUser[];
  placeholder: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onRemove: (option?: IUser) => () => void;
  onSelect: (option: IUser) => void;
}

export interface IUseUsersRequest {
  options: IUser[];
  setOptions: Dispatch<SetStateAction<IUser[]>>;
  handleChange: (event: ChangeEvent<HTMLInputElement>) => void;
}
