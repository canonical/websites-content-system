import { useCallback, useEffect, useState } from "react";

import CustomSearchAndFilter from "./CustomSearchAndFilter";
import { useUsersRequest } from "./OwnerAndReviewers.hooks";
import type { IOwnerAndReviewersProps } from "./OwnerAndReviewers.types";

import { PagesServices } from "@/services/api/services/pages";
import { type IUser } from "@/services/api/types/users";

const Reviewers = ({ page }: IOwnerAndReviewersProps): JSX.Element => {
  const [currentReviewers, setCurrentReviewers] = useState<IUser[]>([]);
  const { options, setOptions, handleChange } = useUsersRequest();

  useEffect(() => {
    setCurrentReviewers(page.reviewers);
  }, [page]);

  const handleRemoveReviewer = useCallback(
    (option?: IUser) => () => {
      setCurrentReviewers((prev) => prev.filter((r) => r.id !== option?.id));
    },
    [],
  );

  const selectReviewer = useCallback(
    (option: IUser) => {
      if (!currentReviewers.find((r) => r.id === option.id)) {
        const newReviewers = [...currentReviewers, option];
        PagesServices.setReviewers(newReviewers, page.id);
        setOptions([]);
        setCurrentReviewers(newReviewers);
        // mutate the tree structure element to reflect the recent change
        page.reviewers = newReviewers;
      }
    },
    [page, currentReviewers, setOptions],
  );

  return (
    <>
      <CustomSearchAndFilter
        label="Reviewers"
        onChange={handleChange}
        onRemove={handleRemoveReviewer}
        onSelect={selectReviewer}
        options={options}
        placeholder="Select reviewers"
        selectedOptions={currentReviewers}
      />
    </>
  );
};

export default Reviewers;
