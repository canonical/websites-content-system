import { type ChangeEvent, useCallback, useState } from "react";

import type { IUseUsersRequest } from "./OwnerAndReviewers.types";

import { UsersServices } from "@/services/api/services/users";
import { UtilServices } from "@/services/api/services/utils";
import type { IUser } from "@/services/api/types/users";

const debouncedRequest = UtilServices.debounce(UsersServices.getUsers, 500);

export const useUsersRequest = (): IUseUsersRequest => {
  const [options, setOptions] = useState<IUser[]>([]);

  const handleChange = useCallback(async (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    if (value.length >= 2) {
      const users = await debouncedRequest(value);
      if (users?.data?.length) {
        setOptions(users.data);
      }
    } else {
      setOptions([]);
    }
  }, []);

  return { options, setOptions, handleChange };
};
