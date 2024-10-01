import { useCallback, useEffect, useState } from "react";

import CustomSearchAndFilter from "./CustomSearchAndFilter";
import { useUsersRequest } from "./OwnerAndReviewers.hooks";
import type { IOwnerAndReviewersProps } from "./OwnerAndReviewers.types";

import { PagesServices } from "@/services/api/services/pages";
import { type IUser } from "@/services/api/types/users";

const Reviewers = ({ page, onSelectReviewers }: IOwnerAndReviewersProps): JSX.Element => {
  const [currentReviewers, setCurrentReviewers] = useState<IUser[]>([]);
  const { options, setOptions, handleChange } = useUsersRequest();

  useEffect(() => {
    if (page) setCurrentReviewers(page.reviewers);
  }, [page]);

  const handleRemoveReviewer = useCallback(
    (option?: IUser) => () => {
      const newReviewers = currentReviewers.filter((r) => r.id !== option?.id);
      setCurrentReviewers(newReviewers);
      if (page) PagesServices.setReviewers(newReviewers, page.id);
      if (onSelectReviewers) onSelectReviewers(newReviewers);
    },
    [currentReviewers, page, onSelectReviewers],
  );

  const selectReviewer = useCallback(
    (option: IUser) => {
      // check if a person with the same email already exists
      // proceed with setting the reviewer only if not
      if (!currentReviewers.find((r) => r.email === option.email)) {
        const newReviewers = [...currentReviewers, option];
        if (page) {
          PagesServices.setReviewers(newReviewers, page.id);
          // mutate the tree structure element to reflect the recent change
          page.reviewers = newReviewers;
        }
        setOptions([]);
        setCurrentReviewers(newReviewers);
        if (onSelectReviewers) onSelectReviewers(newReviewers);
      }
    },
    [page, currentReviewers, setOptions, onSelectReviewers],
  );

  return (
    <CustomSearchAndFilter
      label="Reviewers"
      onChange={handleChange}
      onRemove={handleRemoveReviewer}
      onSelect={selectReviewer}
      options={options}
      placeholder="Select reviewers"
      selectedOptions={currentReviewers}
    />
  );
};

export default Reviewers;
