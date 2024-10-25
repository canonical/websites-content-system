import { useCallback, useMemo, useState } from "react";

import { Button } from "@canonical/react-components";

import { type IWebpageProps } from "./Webpage.types";

import JiraTasks from "@/components/JiraTasks";
import OwnerAndReviewers from "@/components/OwnerAndReviewers";
import RequestTaskModal from "@/components/RequestTaskModal";
import config from "@/config";
import { ChangeRequestType, PageStatus } from "@/services/api/types/pages";

const Webpage = ({ page, project }: IWebpageProps): JSX.Element => {
  const [modalOpen, setModalOpen] = useState(false);
  const [changeType, setChangeType] = useState<(typeof ChangeRequestType)[keyof typeof ChangeRequestType]>(
    ChangeRequestType.COPY_UPDATE,
  );

  const openCopyDoc = useCallback(() => {
    window.open(page.copy_doc_link);
  }, [page]);

  const openGitHub = useCallback(() => {
    if (page.children.length) {
      window.open(`${config.ghLink(project)}${page.name}/index.html`);
    } else {
      window.open(`${config.ghLink(project)}${page.name}.html`);
    }
  }, [page, project]);

  const createNewPage = useCallback(() => {
    setChangeType(ChangeRequestType.NEW_WEBPAGE);
    setModalOpen(true);
  }, []);

  const requestChanges = useCallback(() => {
    setChangeType(ChangeRequestType.COPY_UPDATE);
    setModalOpen(true);
  }, []);

  const requestRemoval = useCallback(() => {
    setChangeType(ChangeRequestType.PAGE_REMOVAL);
    setModalOpen(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setModalOpen(false);
  }, []);

  const isNew = useMemo(() => page.status === PageStatus.NEW, [page]);
  const pageName = useMemo(() => page.name.split("/").reverse()[0], [page]);
  const hasJiraTasks = useMemo(() => page.jira_tasks?.length, [page]);

  return (
    <div className="l-webpage">
      {isNew ? (
        <h1>New page: {pageName}</h1>
      ) : (
        <>
          <p className="p-text--small-caps" id="page-title">
            Title
          </p>
          <h1 aria-labelledby="page-title" className="u-no-padding--top">
            {page.title || "-"}
          </h1>
        </>
      )}
      <div>
        {isNew ? (
          <p>{`${project}${page.name}`}</p>
        ) : (
          <a href={`https://${project}${page.name}`} rel="noopener noreferrer" target="_blank">
            {`${project}${page.name}`}&nbsp;
            <i className="p-icon--external-link" />
          </a>
        )}
      </div>
      <div className="l-webpage--buttons">
        <>
          {isNew && !hasJiraTasks && (
            <Button appearance="positive" onClick={createNewPage}>
              Submit for publication...
            </Button>
          )}
          {!isNew && (
            <Button appearance="positive" onClick={requestChanges}>
              Request changes
            </Button>
          )}
          {page.copy_doc_link && (
            <Button appearance="neutral" onClick={openCopyDoc}>
              Edit copy doc&nbsp;
              <i className="p-icon--external-link" />
            </Button>
          )}
          {!isNew && (
            <Button appearance="neutral" onClick={openGitHub}>
              Inspect code on GitHub&nbsp;
              <i className="p-icon--external-link" />
            </Button>
          )}
          <Button appearance="neutral" onClick={requestRemoval}>
            Request removal
          </Button>
        </>
      </div>
      <div className="row">
        {!isNew && (
          <div className="col-7">
            <p className="p-text--small-caps" id="page-descr">
              Description
            </p>
            <p aria-labelledby="page-descr">{page.description || "-"}</p>
          </div>
        )}
        <div className={isNew ? "col-12" : "col-5"}>
          <OwnerAndReviewers page={page} />
        </div>
      </div>
      {page.jira_tasks?.length ? (
        <div className="l-webpage--tasks row">
          <p className="p-text--small-caps">Related Jira Tickets</p>
          <JiraTasks tasks={page.jira_tasks} />
        </div>
      ) : null}
      {modalOpen && (
        <RequestTaskModal
          changeType={changeType}
          copyDocLink={page.copy_doc_link}
          onClose={handleModalClose}
          onTypeChange={setChangeType}
          webpage={page}
        />
      )}
    </div>
  );
};

export default Webpage;
