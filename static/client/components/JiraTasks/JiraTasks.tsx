import type { IJiraTasksProps } from "./JiraTasks.types";

import config from "@/config";
import { DatesServices } from "@/services/dates";

const JiraTasks = ({ tasks }: IJiraTasksProps): JSX.Element => {
  return (
    <table>
      {tasks.map((task) => (
        <tr>
          <td>
            <a href={`${config.jiraTaskLink}${task.jira_id}`} rel="noreferrer" target="_blank">
              {task.jira_id}
            </a>
          </td>
          <td>{task.summary}</td>
          <td className="u-text--muted">{DatesServices.beatifyDate(task.created_at)}</td>
          <td>{task.status}</td>
        </tr>
      ))}
    </table>
  );
};

export default JiraTasks;
