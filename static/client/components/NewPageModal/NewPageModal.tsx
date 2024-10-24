import { type ChangeEvent, useCallback, useState } from "react";

import { Button, Input, Modal, Spinner, Textarea } from "@canonical/react-components";

import type { INewPageModalProps } from "./NewPageModal.types";

import config from "@/config";
import { PagesServices } from "@/services/api/services/pages";
import { ChangeRequestType } from "@/services/api/types/pages";
import { DatesServices } from "@/services/dates";

const NewPageModal = ({ copyDocLink, onClose, webpage }: INewPageModalProps): JSX.Element => {
  const [dueDate, setDueDate] = useState<string>();
  const [checked, setChecked] = useState(false);
  const [summary, setSummary] = useState<string>();
  const [descr, setDescr] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChangeDueDate = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setDueDate(e.target.value);
  }, []);

  const handleChangeConsent = useCallback(() => {
    setChecked((prevValue) => !prevValue);
  }, []);

  const handleSummaryChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setSummary(e.target.value);
  }, []);

  const handleDescrChange = useCallback((e: ChangeEvent<HTMLTextAreaElement>) => {
    setDescr(e.target.value);
  }, []);

  const handleSubmit = useCallback(() => {
    if (dueDate && webpage?.id) {
      setIsLoading(true);
      PagesServices.requestChanges({
        due_date: dueDate,
        webpage_id: webpage.id,
        reporter_id: webpage.owner.id,
        type: ChangeRequestType.NEW_WEBPAGE,
        summary,
        description: `Copy doc link: ${webpage.copy_doc_link} \n${descr}`,
      }).then(() => {
        setIsLoading(false);
        onClose();
        window.location.reload();
      });
    }
  }, [dueDate, summary, descr, webpage, onClose]);

  return (
    <Modal
      buttonRow={
        <>
          <Button className="u-no-margin--bottom" onClick={onClose}>
            Cancel
          </Button>
          <Button appearance="positive" disabled={!dueDate || !checked} onClick={handleSubmit}>
            {isLoading ? <Spinner /> : "Submit"}
          </Button>
        </>
      }
      close={onClose}
      title="Submit new page for publication"
    >
      <Input label="Due date" min={DatesServices.getNowStr()} onChange={handleChangeDueDate} required type="date" />
      <Input label="Summary" onChange={handleSummaryChange} type="text" />
      <Textarea label="Description" onChange={handleDescrChange} />
      <Input
        checked={checked}
        label={
          <span>
            I have added all the content to the{" "}
            <a href={copyDocLink} rel="noreferrer" target="_blank">
              copy doc
            </a>
            , and it is consistent with our{" "}
            <a href={config.copyStyleGuideLink} rel="noreferrer" target="_blank">
              copy style guides
            </a>
          </span>
        }
        onChange={handleChangeConsent}
        required
        type="checkbox"
      />
    </Modal>
  );
};

export default NewPageModal;
