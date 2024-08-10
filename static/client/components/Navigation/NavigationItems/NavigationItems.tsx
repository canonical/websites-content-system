import { useCallback, useEffect, useState } from "react";

import { Select, Spinner } from "@canonical/react-components";
import { useLocation } from "react-router-dom";

import NavigationElement from "@/components/Navigation/NavigationElement/NavigationElement";
import { usePages } from "@/services/api/hooks/pages";
import type { IPagesResponse } from "@/services/api/types/pages";

const NavigationItems = (): React.ReactNode => {
  const location = useLocation();

  const { data, isLoading } = usePages();
  const [projects, setProjects] = useState<IPagesResponse["data"][]>([]);
  const [selectedProject, setSelectedProject] = useState<IPagesResponse["data"]>();

  useEffect(() => {
    const hasData = data?.every((project) => project?.data);
    if (!isLoading && data?.length && hasData && projects.length !== data.length) {
      setProjects(data.map((project) => project.data));
    }
  }, [data, isLoading, projects]);

  useEffect(() => {
    if (projects.length) {
      const match = location.pathname.match(/\/webpage\/([^/]+)/);
      let projectFromPath;
      if (match) {
        projectFromPath = projects.find((p) => p.name === match[1]);
      }
      setSelectedProject(projectFromPath || projects[0]);
    }
  }, [location, projects]);

  const handleProjectChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const project = projects.find((p) => p.name === e.target.value);
      setSelectedProject(project);
    },
    [projects],
  );

  if (isLoading)
    return (
      <>
        <Spinner />
        <span>&nbsp;Loading...</span>
      </>
    );

  return (
    !!projects.length && (
      <>
        {selectedProject && (
          <Select
            defaultValue={selectedProject?.name}
            label="SELECT SITE"
            onChange={handleProjectChange}
            options={projects.map((project) => ({
              label: project.name,
              value: project.name,
            }))}
          />
        )}
        {selectedProject && (
          <ul aria-multiselectable="true" className="p-list-tree" key={selectedProject.name} role="tree">
            <NavigationElement isRoot page={selectedProject.templates} project={selectedProject.name} />
          </ul>
        )}
      </>
    )
  );
};

export default NavigationItems;
