import type { INewPage, IPage } from "@/services/api/types/pages";

export function addNewPage(parentPage: IPage, newPage: INewPage) {
  if (parentPage.name === newPage.parent) {
    parentPage.children.push({
      name: newPage.name,
      link: newPage.link || "",
      owner: newPage.owner,
      reviewers: newPage.reviewers,
      children: [],
    });
  } else {
    parentPage.children.forEach((page) => {
      addNewPage(page, newPage);
    });
  }
}

export * as TreeServices from "./pages";
