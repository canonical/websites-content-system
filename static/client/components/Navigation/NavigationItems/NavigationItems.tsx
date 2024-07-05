import NavigationElement from "@/components/Navigation/NavigationElement/NavigationElement";
import { usePages } from "@/services/api/hooks/pages";

const NavigationItems = (): React.ReactNode => {
  const { data, isLoading } = usePages();

  if (isLoading) return "...Loading";

  return (
    <>
      {data?.length &&
        data
          .filter((project) => !!project?.data?.name)
          .map((project) => (
            <ul aria-multiselectable="true" className="p-list-tree" key={project.data.name} role="tree">
              <NavigationElement isRoot page={project.data.templates} project={project.data.name} />
            </ul>
          ))}
    </>
  );
};

export default NavigationItems;
