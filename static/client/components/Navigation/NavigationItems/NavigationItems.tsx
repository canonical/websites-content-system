import { useCallback, useState } from "react";

import { useNavigate } from "react-router-dom";

import type { INavigationItemsProps } from "./NavigationItems.types";

import NavigationElement from "@/components/Navigation/NavigationElement/NavigationElement";
import { useStore } from "@/store";

const NavigationItems = ({ onSelectPage }: INavigationItemsProps): React.ReactNode => {
  const selectedProject = useStore((state) => state.selectedProject);
  const [activePageName, setActivePageName] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSelectPage = useCallback(
    (path: string) => {
      setActivePageName(path);
      if (onSelectPage) {
        onSelectPage(path);
      } else {
        if (selectedProject) navigate(`/webpage/${selectedProject.name}${path}`);
      }
    },
    [selectedProject, onSelectPage, navigate],
  );

  return selectedProject ? (
    <ul aria-multiselectable="true" className="p-list-tree" key={selectedProject.name} role="tree">
      {selectedProject.templates?.children?.length &&
        selectedProject.templates.children.map((page) => (
          <NavigationElement
            activePageName={activePageName}
            onSelect={handleSelectPage}
            page={page}
            project={selectedProject.name}
          />
        ))}
    </ul>
  ) : null;
};

export default NavigationItems;
