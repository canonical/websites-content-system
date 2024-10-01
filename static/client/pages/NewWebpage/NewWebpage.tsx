import { useCallback, useState } from "react";

import { Button, Input } from "@canonical/react-components";

import NavigationItems from "@/components/Navigation/NavigationItems";
import OwnerAndReviewers from "@/components/OwnerAndReviewers";
import type { IUser } from "@/services/api/types/users";

const errorMessage = "Please specify the URL title";

const NewWebpage = (): JSX.Element => {
  const [titleValue, setTitleValue] = useState<string>();
  const [copyDoc, setCopyDoc] = useState<string>();
  const [owner, setOwner] = useState<IUser | null>();
  const [reviewers, setReviewers] = useState<IUser[]>();
  const [location, setLocation] = useState<string>();

  const handleTitleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setTitleValue(event.target.value || "");
  }, []);

  const handleCopyDocChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setCopyDoc(event.target.value || "");
  }, []);

  const handleSelectOwner = useCallback((user: IUser | null) => {
    setOwner(user);
  }, []);

  const handleSelectReviewers = useCallback((users: IUser[]) => {
    setReviewers(users);
  }, []);

  const handleSelectPage = useCallback((path: string) => {
    setLocation(path);
  }, []);

  const handleSubmit = useCallback(() => {
    console.log({
      titleValue,
      location,
      copyDoc,
      owner,
      reviewers,
    });
  }, [titleValue, location, copyDoc, owner, reviewers]);

  return (
    <div className="l-new-webpage">
      <h1>New page</h1>
      <div>
        <p className="p-text--small-caps" id="url-title">
          URL Title (lowercase, hyphenated)
        </p>
        <Input
          aria-labelledby="url-title"
          error={titleValue ? null : errorMessage}
          onChange={handleTitleChange}
          type="text"
          value={titleValue}
        />
      </div>
      <div className="l-new-webpage--location">
        <p className="p-text--small-caps">Location</p>
        <NavigationItems onSelectPage={handleSelectPage} />
      </div>
      <div>
        <p className="p-text--small-caps" id="copy-doc">
          Copy doc
        </p>
        <Input
          aria-labelledby="copy-doc"
          help="If no copy doc is provided, a new one will be created when you save."
          onChange={handleCopyDocChange}
          type="text"
          value={copyDoc}
        />
      </div>
      <OwnerAndReviewers onSelectOwner={handleSelectOwner} onSelectReviewers={handleSelectReviewers} />
      <Button
        appearance="positive"
        className="l-new-webpage--submit"
        onClick={handleSubmit}
      >{`Save${copyDoc ? "" : " and generate copy doc"}`}</Button>
    </div>
  );
};

export default NewWebpage;
