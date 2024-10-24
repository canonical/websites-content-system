import { useCallback, useEffect, useState } from "react";

import { Button, Input, Spinner } from "@canonical/react-components";

import NavigationItems from "@/components/Navigation/NavigationItems";
import OwnerAndReviewers from "@/components/OwnerAndReviewers";
import { usePages } from "@/services/api/hooks/pages";
import { PagesServices } from "@/services/api/services/pages";
import type { IUser } from "@/services/api/types/users";
import { TreeServices } from "@/services/tree/pages";
import { useStore } from "@/store";

const errorMessage = "Please specify the URL title";

const LoadingState = {
  INITIAL: 0,
  LOADING: 1,
  DONE: 2,
};

const NewWebpage = (): JSX.Element => {
  const [titleValue, setTitleValue] = useState<string>();
  const [copyDoc, setCopyDoc] = useState<string>();
  const [owner, setOwner] = useState<IUser | null>();
  const [reviewers, setReviewers] = useState<IUser[]>([]);
  const [location, setLocation] = useState<string>();
  const [buttonDisabled, setButtonDisabled] = useState(true);
  const [reloading, setReloading] = useState<(typeof LoadingState)[keyof typeof LoadingState]>(LoadingState.INITIAL);

  const [selectedProject, setSelectedProject] = useStore((state) => [state.selectedProject, state.setSelectedProject]);
  const { data, isFetching, refetch } = usePages(true);

  useEffect(() => {
    if (titleValue && location && owner) {
      setButtonDisabled(false);
    }
  }, [titleValue, location, owner]);

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
    if (titleValue && owner && selectedProject && location) {
      setReloading(LoadingState.LOADING);
      const newPage = {
        name: `${location}/${titleValue}`,
        copy_doc_link: copyDoc,
        owner,
        reviewers,
        project: selectedProject.name,
        parent: location,
      };
      PagesServices.createPage(newPage).then(() => {
        // refetch the tree from the backend after a new webpage is added to the database
        refetch &&
          refetch().then(() => {
            setReloading(LoadingState.DONE);
          });
      });
    }
  }, [titleValue, location, copyDoc, owner, reviewers, selectedProject, refetch]);

  // update navigation after new page is added to the tree on the backend
  useEffect(() => {
    if (!isFetching && reloading === LoadingState.DONE && data?.length && selectedProject) {
      const project = data.find((p) => p.data.name === selectedProject.name)?.data;
      if (project) {
        const isNewPageExist = TreeServices.findPage(project.templates, `${location}/${titleValue}`);
        if (isNewPageExist) {
          console.log("new page exists, should redirect");
          // TODO: there is a max depth React error on this line, needs more investigation
          setSelectedProject(project);
          window.location.href = `/webpage/${project.name}${location}/${titleValue}`;
        }
      }
    }
  }, [data, isFetching, reloading, selectedProject, setSelectedProject, location, titleValue]);

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
        {reloading === LoadingState.LOADING ? <Spinner /> : `Save${copyDoc ? "" : " and generate copy doc"}`}
      </Button>
    </div>
  );
};

export default NewWebpage;
