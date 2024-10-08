import { useCallback, useEffect, useState } from "react";

import { Button, Input, Spinner } from "@canonical/react-components";
import { useNavigate } from "react-router-dom";

import NavigationItems from "@/components/Navigation/NavigationItems";
import OwnerAndReviewers from "@/components/OwnerAndReviewers";
import { usePages } from "@/services/api/hooks/pages";
import { PagesServices } from "@/services/api/services/pages";
import type { IUser } from "@/services/api/types/users";
import { TreeServices } from "@/services/tree/pages";
import { useStore } from "@/store";

const errorMessage = "Please specify the URL title";

const NewWebpage = (): JSX.Element => {
  const [titleValue, setTitleValue] = useState<string>();
  const [copyDoc, setCopyDoc] = useState<string>();
  const [owner, setOwner] = useState<IUser | null>();
  const [reviewers, setReviewers] = useState<IUser[]>([]);
  const [location, setLocation] = useState<string>();
  const [buttonDisabled, setButtonDisabled] = useState(true);
  const [loading, setLoading] = useState(false);

  const project = useStore((state) => state.selectedProject);
  const { data } = usePages();
  const navigate = useNavigate();

  useEffect(() => {
    if (titleValue && location && owner) {
      setButtonDisabled(false);
    }
  }, [titleValue, location, copyDoc, owner, reviewers, project]);

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
    if (titleValue && owner && project && location) {
      setLoading(true);
      const newPage = {
        name: `${location}/${titleValue}`,
        link: copyDoc,
        owner,
        reviewers,
        project: project.name,
        parent: location,
      };
      PagesServices.createPage(newPage).then((response) => {
        const currentProjectTree = data?.find((p) => p.data.name === project.name)?.data;
        if (currentProjectTree) {
          TreeServices.addNewPage(currentProjectTree.templates, {
            ...newPage,
            link: response.copy_doc,
          });
        }
        setLoading(false);
        navigate(`/webpage/${project}${location}/${titleValue}`);
      });
    }
  }, [titleValue, location, copyDoc, owner, reviewers, project, data, navigate]);

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
      <Button appearance="positive" className="l-new-webpage--submit" disabled={buttonDisabled} onClick={handleSubmit}>
        {loading ? <Spinner /> : `Save${copyDoc ? "" : " and generate copy doc"}`}
      </Button>
    </div>
  );
};

export default NewWebpage;
