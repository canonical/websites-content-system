import { type MouseEvent, useCallback, useRef, useState } from "react";

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

  const searchRef = useRef<HTMLInputElement>(null);

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
        searchRef.current.value = "";
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

  // a callback that closes an options dropdown when focus is not on an input field
  const handleInputBlur = useCallback(() => {
    setMatches([]);
    if (searchRef?.current) {
      searchRef.current.value = "";
    }
  }, []);

  // this callback is needed for handleSelect to have higher priority than handleInputBlur when selecting an option
  const handleOptionMouseDown = useCallback((event: MouseEvent<HTMLLIElement>) => {
    event.preventDefault();
  }, []);

  return (
    <>
      <SearchBox
        autocomplete="off"
        className="l-search-box"
        disabled={!(data?.length && data[0]?.data)}
        onBlur={handleInputBlur}
        onChange={handleChange}
        placeholder="Search a webpage"
        ref={searchRef}
      />
      <div className="l-search-container">
        {matches.length >= 0 && (
          <ul className="l-search-dropdown">
            {matches.map((match) => (
              <li className="l-search-item" onClick={handleSelect(match)} onMouseDown={handleOptionMouseDown}>
                {`${match.project}${match.name}`} {match.title && `- ${match.title}`}
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
};

export default Search;
