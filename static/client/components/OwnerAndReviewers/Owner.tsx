import { useCallback, useEffect, useState } from "react";

import CustomSearchAndFilter from "./CustomSearchAndFilter";
import { useUsersRequest } from "./OwnerAndReviewers.hooks";
import type { IOwnerAndReviewersProps } from "./OwnerAndReviewers.types";

import { PagesServices } from "@/services/api/services/pages";
import { type IUser } from "@/services/api/types/users";

const Owner = ({ page }: IOwnerAndReviewersProps): JSX.Element => {
  const [currentOwner, setCurrentOwner] = useState<IUser | null>(null);
  const { options, setOptions, handleChange } = useUsersRequest();

  useEffect(() => {
    setCurrentOwner(page.owner);
  }, [page]);

  const handleRemoveOwner = useCallback(
    () => () => {
      setCurrentOwner(null);
      PagesServices.setOwner({}, page.id);
    },
    [page],
  );

  const selectOwner = useCallback(
    (option: IUser) => {
      PagesServices.setOwner(option, page.id);
      setOptions([]);
      setCurrentOwner(option);
      // mutate the tree structure element to reflect the recent change
      page.owner = option;
    },
    [page, setOptions],
  );

  return (
    <CustomSearchAndFilter
      label="Owner"
      onChange={handleChange}
      onRemove={handleRemoveOwner}
      onSelect={selectOwner}
      options={options}
      placeholder="Select an owner"
      selectedOptions={currentOwner ? [currentOwner] : []}
    />
  );
};

export default Owner;
