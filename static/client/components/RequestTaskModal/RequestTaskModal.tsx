import { type ChangeEvent, useCallback, useMemo, useState } from "react";

import { Button, Input, Modal, RadioInput, Spinner, Textarea } from "@canonical/react-components";

import type { IRequestTaskModalProps } from "./RequestTaskModal.types";

import config from "@/config";
import { PagesServices } from "@/services/api/services/pages";
import { ChangeRequestType } from "@/services/api/types/pages";
import { DatesServices } from "@/services/dates";

const RequestTaskModal = ({
  changeType,
  copyDocLink,
  onTypeChange,
  onClose,
  webpage,
}: IRequestTaskModalProps): JSX.Element => {
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

  const handleTypeChange = useCallback(
    (type: (typeof ChangeRequestType)[keyof typeof ChangeRequestType]) => () => {
      onTypeChange(type);
    },
    [onTypeChange],
  );

  const handleSubmit = useCallback(() => {
    if (dueDate && webpage?.id) {
      setIsLoading(true);
      PagesServices.requestChanges({
        due_date: dueDate,
        webpage_id: webpage.id,
        reporter_id: webpage.owner.id,
        type: changeType,
        summary,
        description: `Copy doc link: ${webpage.copy_doc_link} \n${descr}`,
      }).then(() => {
        setIsLoading(false);
        onClose();
        window.location.reload();
      });
    }
  }, [changeType, dueDate, summary, descr, webpage, onClose]);

  const title = useMemo(() => {
    switch (changeType) {
      case ChangeRequestType.COPY_UPDATE:
        return "Submit changes for copy update";
      case ChangeRequestType.PAGE_REFRESH:
        return "Submit changes for page refresh";
      case ChangeRequestType.NEW_WEBPAGE:
        return "Submit new page for publication";
      default:
        return "Submit request";
    }
  }, [changeType]);

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
      title={title}
    >
      {[ChangeRequestType.COPY_UPDATE, ChangeRequestType.PAGE_REFRESH].indexOf(changeType) >= 0 && (
        <>
          <RadioInput
            checked={changeType === ChangeRequestType.COPY_UPDATE}
            label="Copy update"
            onClick={handleTypeChange(ChangeRequestType.COPY_UPDATE)}
          />
          <RadioInput
            checked={changeType === ChangeRequestType.PAGE_REFRESH}
            label="Page refresh"
            onClick={handleTypeChange(ChangeRequestType.PAGE_REFRESH)}
          />
        </>
      )}
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

export default RequestTaskModal;
