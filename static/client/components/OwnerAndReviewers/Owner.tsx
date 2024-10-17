import { useCallback, useEffect, useState } from "react";

import CustomSearchAndFilter from "./CustomSearchAndFilter";
import { useUsersRequest } from "./OwnerAndReviewers.hooks";
import type { IOwnerAndReviewersProps } from "./OwnerAndReviewers.types";

import { PagesServices } from "@/services/api/services/pages";
import { type IUser } from "@/services/api/types/users";

const Owner = ({ page, onSelectOwner }: IOwnerAndReviewersProps): JSX.Element => {
  const [currentOwner, setCurrentOwner] = useState<IUser | null>(null);
  const { options, setOptions, handleChange } = useUsersRequest();

  useEffect(() => {
    if (page) setCurrentOwner(page.owner);
  }, [page]);

  const handleRemoveOwner = useCallback(
    () => () => {
      setCurrentOwner(null);
      if (page?.id) PagesServices.setOwner({}, page.id);
      if (onSelectOwner) onSelectOwner(null);
    },
    [page, onSelectOwner],
  );

  const selectOwner = useCallback(
    (option: IUser) => {
      if (page?.id) {
        PagesServices.setOwner(option, page.id);
        // mutate the tree structure element to reflect the recent change
        page.owner = option;
      }
      setOptions([]);
      setCurrentOwner(option);
      if (onSelectOwner) onSelectOwner(option);
    },
    [page, setOptions, onSelectOwner],
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
