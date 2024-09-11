import { useCallback } from "react";

import { Button } from "@canonical/react-components";

import { type IWebpageProps } from "./Webpage.types";

import OwnerAndReviewers from "@/components/OwnerAndReviewers";
import config from "@/config";

const Webpage = ({ page, project }: IWebpageProps): JSX.Element => {
  const openCopyDoc = useCallback(() => {
    window.open(page.link);
  }, [page]);

  const openGitHub = useCallback(() => {
    if (page.children.length) {
      window.open(`${config.ghLink(project)}${page.name}/index.html`);
    } else {
      window.open(`${config.ghLink(project)}${page.name}.html`);
    }
  }, [page, project]);

  return (
    <div className="l-webpage">
      <div>
        <p className="p-text--small-caps" id="page-title">
          Title
        </p>
        <h1 aria-labelledby="page-title" className="u-no-padding--top">
          {page.title || "-"}
        </h1>
      </div>
      <div>
        <a href={`https://${project}${page.name}`} rel="noopener noreferrer" target="_blank">
          {`${project}${page.name}`}&nbsp;
          <i className="p-icon--external-link" />
        </a>
      </div>
      <div className="l-webpage--buttons">
        {page.link && (
          <>
            <Button appearance="neutral" onClick={openCopyDoc}>
              Edit copy doc&nbsp;
              <i className="p-icon--external-link" />
            </Button>
            <Button appearance="neutral" onClick={openGitHub}>
              Inspect code on GitHub&nbsp;
              <i className="p-icon--external-link" />
            </Button>
          </>
        )}
      </div>
      <div className="row">
        <div className="col-7">
          <p className="p-text--small-caps" id="page-descr">
            Description
          </p>
          <p aria-labelledby="page-descr">{page.description || "-"}</p>
        </div>
        <div className="col-5">
          <OwnerAndReviewers page={page} />
        </div>
      </div>
    </div>
  );
};

export default Webpage;
