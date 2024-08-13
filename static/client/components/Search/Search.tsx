import { useCallback, useRef, useState } from "react";

import { SearchBox } from "@canonical/react-components";
import { useNavigate } from "react-router-dom";

import { SearchServices } from "./Search.services";
import type { IMatch } from "./Search.types";

import { usePages } from "@/services/api/hooks/pages";
import { useStore } from "@/store";

const Search = (): JSX.Element => {
  const { data } = usePages();
  const navigate = useNavigate();
  const [selectedProject, setSelectedProject] = useStore((state) => [state.selectedProject, state.setSelectedProject]);

  const [matches, setMatches] = useState<IMatch[]>([]);

  const searchRef = useRef(null);

  const handleChange = useCallback(
    (inputValue: string) => {
      if (inputValue.length > 2 && data?.length && data[0]?.data) {
        setMatches(SearchServices.searchForMatches(inputValue, data));
      } else if (inputValue.length === 0) {
        setMatches([]);
      }
    },
    [data],
  );

  const handleSelect = useCallback(
    (selectedItem: IMatch) => () => {
      setMatches([]);
      if (searchRef?.current) {
        (searchRef.current as any).value = "";
      }
      // if the selected webpage has a different project, propagate to the rest of the app via the store
      if (selectedItem.project !== selectedProject?.name) {
        const project = SearchServices.getProjectByName(data, selectedItem.project);
        if (project) setSelectedProject(project);
      }
      navigate(`/webpage/${selectedItem.project}${selectedItem.name}`);
    },
    [data, navigate, searchRef, selectedProject, setSelectedProject],
  );

  return (
    <div className="l-search-container">
      {
        <SearchBox
          disabled={!(data?.length && data[0]?.data)}
          onChange={handleChange}
          placeholder="Search a webpage"
          ref={searchRef}
        />
      }
      {matches.length >= 0 && (
        <ul className="l-search-dropdown">
          {matches.map((match) => (
            <li className="l-search-item" onClick={handleSelect(match)}>
              {match.name} - {match.title}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Search;
