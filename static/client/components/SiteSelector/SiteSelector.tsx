import { useCallback, useEffect, useState } from "react";

import { Select, Spinner } from "@canonical/react-components";
import { useLocation } from "react-router-dom";

import { usePages } from "@/services/api/hooks/pages";
import { type IPagesResponse } from "@/services/api/types/pages";
import { useStore } from "@/store";

const SiteSelector = (): JSX.Element | null => {
  const location = useLocation();
  const { data, isLoading } = usePages();

  const [selectedProject, setSelectedProject] = useStore((state) => [state.selectedProject, state.setSelectedProject]);

  const [projects, setProjects] = useState<IPagesResponse["data"][]>([]);

  useEffect(() => {
    if (projects.length && !selectedProject) {
      const match = location.pathname.match(/\/webpage\/([^/]+)/);
      let projectFromPath;
      if (match) {
        projectFromPath = projects.find((p) => p.name === match[1]);
      }
      setSelectedProject(projectFromPath || projects[0]);
    }
  }, [location, projects, selectedProject, setSelectedProject]);

  useEffect(() => {
    // check that the data array actually has data in it
    const hasData = data?.every((project) => project?.data);
    if (!isLoading && data?.length && hasData && projects.length !== data.length) {
      setProjects(data.map((project) => project.data));
    }
  }, [data, isLoading, projects]);

  const handleProjectChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const project = projects.find((p) => p.name === e.target.value);
      if (project) setSelectedProject(project);
    },
    [projects, setSelectedProject],
  );

  if (isLoading || !projects.length)
    return (
      <>
        <Spinner />
        <span>&nbsp;&nbsp;Loading...</span>
      </>
    );

  return selectedProject ? (
    <Select
      defaultValue={selectedProject?.name}
      label="SELECT SITE"
      onChange={handleProjectChange}
      options={projects.map((project) => ({
        label: project.name,
        value: project.name,
      }))}
    />
  ) : null;
};

export default SiteSelector;
