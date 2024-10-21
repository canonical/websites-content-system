import React, { type MouseEvent, useCallback, useEffect, useRef, useState } from "react";

import { useLocation } from "react-router-dom";

import { type INavigationElementProps } from "./NavigationElement.types";

import type { IPage } from "@/services/api/types/pages";
import { NavigationServices } from "@/services/navigation";

const NavigationElement = ({ activePageName, page, project, onSelect }: INavigationElementProps): JSX.Element => {
  const [expanded, setExpanded] = useState(false);
  const [childrenHidden, setChildrenHidden] = useState(true);
  const [children, setChildren] = useState<IPage[]>([]);

  const location = useLocation();

  const expandButtonRef = useRef<HTMLButtonElement>(null);

  const toggleElement = useCallback(
    (e: MouseEvent<HTMLButtonElement>) => {
      const buttonRect = expandButtonRef.current?.getBoundingClientRect();
      if (buttonRect && e.clientX < buttonRect.left + 35) {
        setExpanded((prevValue) => !prevValue);
        setChildrenHidden((prevValue) => !prevValue);
      } else {
        onSelect(page.name);
      }
    },
    [expandButtonRef, page, onSelect],
  );

  const handleSelect = useCallback(() => {
    onSelect(page.name);
  }, [page, onSelect]);

  useEffect(() => {
    if (page.name === "" || location.pathname.indexOf(`${project}${page.name}`) > 0) {
      setExpanded(true);
      setChildrenHidden(false);
    }
  }, [page, project, location]);

  useEffect(() => {
    if (page?.children.length) {
      setChildren(
        page.children.sort((c1, c2) =>
          NavigationServices.formatPageName(c1.name) < NavigationServices.formatPageName(c2.name) ? -1 : 1,
        ),
      );
    }
  }, [page?.children]);

  return (
    <li
      aria-selected={page.name === activePageName}
      className={`p-list-tree__item ${children.length ? "p-list-tree__item--group" : ""} ${page.name === activePageName ? "is-active" : ""}`}
      role="treeitem"
    >
      {children.length ? (
        <>
          <>
            <button
              aria-controls={page.name}
              aria-expanded={expanded}
              className={`p-list-tree__toggle ${page.name === activePageName ? "is-active" : ""}`}
              id={`${page.name}-btn`}
              onClick={toggleElement}
              ref={expandButtonRef}
            >
              {NavigationServices.formatPageName(page.name)}
            </button>
          </>
          <ul
            aria-hidden={childrenHidden}
            aria-labelledby={`${page.name}-btn`}
            className="p-list-tree"
            id={page.name}
            role="group"
          >
            {children.map((page, index) => (
              <React.Fragment key={`${page.name}-${index}`}>
                <NavigationElement activePageName={activePageName} onSelect={onSelect} page={page} project={project} />
              </React.Fragment>
            ))}
          </ul>
        </>
      ) : (
        <div className={`p-list-tree__link ${page.name === activePageName ? "is-active" : ""}`} onClick={handleSelect}>
          {NavigationServices.formatPageName(page.name)}
        </div>
      )}
    </li>
  );
};

export default NavigationElement;
