import type { IMatch } from "./Search.types";

import type { IPage, IPagesResponse } from "@/services/api/types/pages";

const checkMatches = (pages: IPage[], value: string, matches: IMatch[], project: string) => {
  pages.forEach((page) => {
    if (page.name?.indexOf(value) >= 0 || page.title?.indexOf(value) >= 0) {
      matches.push({
        name: page.name,
        project,
        title: page.title,
      });
    }
    if (page.children?.length) {
      checkMatches(page.children, value, matches, project);
    }
  });
};

export const searchForMatches = (value: string, tree: IPagesResponse[]): IMatch[] => {
  const matches: IMatch[] = [];

  tree.forEach((project) => {
    if (project.data.templates.children?.length) {
      checkMatches(project.data.templates.children, value, matches, project.data.name);
    }
  });

  return matches;
};

export * as SearchServices from "./Search.services";
