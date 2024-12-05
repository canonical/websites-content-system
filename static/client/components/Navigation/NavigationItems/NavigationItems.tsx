import { useCallback, useEffect, useState } from "react";

import { useLocation, useNavigate } from "react-router-dom";

import type { INavigationItemsProps } from "./NavigationItems.types";

import NavigationElement from "@/components/Navigation/NavigationElement/NavigationElement";
import { useStore } from "@/store";

const NavigationItems = ({ onSelectPage }: INavigationItemsProps): React.ReactNode => {
  const selectedProject = useStore((state) => state.selectedProject);
  const [activePageName, setActivePageName] = useState<string | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  const handleSelectPage = useCallback(
    (path: string) => {
      setActivePageName(path);
      if (onSelectPage) {
        onSelectPage(path);
      } else {
        if (selectedProject) navigate(`/app/webpage/${selectedProject.name}${path}`);
      }
    },
    [selectedProject, onSelectPage, navigate],
  );

  // set active page whenever the location changes
  useEffect(() => {
    const parts = location.pathname.split("/");
    if (parts.length > 4 && parts[2] === "webpage") {
      const path = `/${parts.slice(3).join("/")}`;
      setActivePageName(path);
    } else {
      setActivePageName(null);
    }
  }, [location]);

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
