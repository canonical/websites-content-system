// the existing SearchAndFilter component provided by react-components did not provide ability to have dynamic options
import { type MouseEvent, useCallback, useEffect, useRef, useState } from "react";

import type { ICustomSearchAndFilterProps } from "./OwnerAndReviewers.types";

import type { IUser } from "@/services/api/types/users";

const CustomSearchAndFilter = ({
  label,
  options,
  selectedOptions,
  placeholder,
  onChange,
  onRemove,
  onSelect,
}: ICustomSearchAndFilterProps): JSX.Element => {
  const [dropdownHidden, setDropdownHidden] = useState(true);
  const [containerExpanded, setContainerExpanded] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setDropdownHidden(!options.length);
    setContainerExpanded(!!options.length);
  }, [options]);

  const handleSelect = useCallback(
    (option: IUser) => () => {
      onSelect(option);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    },
    [onSelect],
  );

  // a callback that closes an options dropdown when focus is not on an input field
  const handleInputBlur = useCallback(() => {
    setDropdownHidden(true);
    setContainerExpanded(false);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }, []);

  // this callback is needed for handleSelect to have higher priority than handleInputBlur when selecting an option
  const handleOptionMouseDown = useCallback((event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  }, []);

  return (
    <div className="p-search-and-filter">
      <p className="p-text--small-caps" id="owner-input">
        {label}
      </p>
      <div
        aria-expanded={containerExpanded}
        className="p-search-and-filter__search-container"
        data-active="true"
        data-empty="true"
      >
        {selectedOptions?.map(
          (option) =>
            option && (
              <span className="p-chip">
                <span className="p-chip__value">{option.name}</span>
                <button className="p-chip__dismiss" onClick={onRemove(option)}>
                  Dismiss
                </button>
              </span>
            ),
        )}
        <form className="p-search-and-filter__box" data-overflowing="false">
          <input
            aria-labelledby="owner-input"
            autoComplete="off"
            className="p-search-and-filter__input"
            id="search"
            name="search"
            onBlur={handleInputBlur}
            onChange={onChange}
            placeholder={placeholder}
            ref={inputRef}
            type="search"
          />
        </form>
      </div>
      <div aria-hidden={dropdownHidden} className="p-search-and-filter__panel">
        <div className="p-filter-panel-section">
          <div aria-expanded="false" className="p-filter-panel-section__chips">
            {options.map((option) => (
              <button className="p-chip" onClick={handleSelect(option)} onMouseDown={handleOptionMouseDown}>
                <span className="p-chip__value">{option.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomSearchAndFilter;
