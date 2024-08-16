import NavigationElement from "@/components/Navigation/NavigationElement/NavigationElement";
import { useStore } from "@/store";

const NavigationItems = (): React.ReactNode => {
  const selectedProject = useStore((state) => state.selectedProject);

  return selectedProject ? (
    <ul aria-multiselectable="true" className="p-list-tree" key={selectedProject.name} role="tree">
      <NavigationElement isRoot page={selectedProject.templates} project={selectedProject.name} />
    </ul>
  ) : null;
};

export default NavigationItems;
