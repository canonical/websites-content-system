import Owner from "./Owner";
import type { IOwnerAndReviewersProps } from "./OwnerAndReviewers.types";
import Reviewers from "./Reviewers";

const OwnerAndReviewers = ({ page }: IOwnerAndReviewersProps): JSX.Element => (
  <>
    <Owner page={page} />
    <div className="u-sv3" />
    <Reviewers page={page} />
  </>
);

export default OwnerAndReviewers;
