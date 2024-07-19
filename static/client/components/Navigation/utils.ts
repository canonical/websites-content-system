import { matchPath } from "react-router-dom";

import type { NavLink, NavItem, NavGroup } from "./types";

export const isSelected = (path: string, link: NavLink): boolean => {
  // Use the provided highlight(s) or just use the url.
  let highlights = link.highlight || link.url;
  // If the provided highlights aren't an array then make them one so that we
  // can loop over them.
  if (!Array.isArray(highlights)) {
    highlights = [highlights];
  }
  // Check if one of the highlight urls matches the current path.
  return highlights.some((highlight) =>
    // Check the full path, for both legacy/new clients as sometimes the lists
    // are in one client and the details in the other.
    matchPath({ path: highlight, end: false }, path),
  );
};

export const isNavGroup = (item: NavItem): item is NavGroup => "navLinks" in item;
