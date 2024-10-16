import type { IPage } from "@/services/api/types/pages";

// recursively find the page in the tree by the given name (URL)
export function findPage(tree: IPage, pageName: string, prefix: string = ""): boolean {
  const parts = pageName.split("/");
  for (let i = 0; i < tree.children.length; i += 1) {
    if (tree.children[i].name === `${prefix}/${parts[1]}`) {
      if (parts.length > 2) {
        return findPage(tree.children[i], `/${parts.slice(2).join("/")}`, `${prefix}/${parts[1]}`);
      }
      return true;
    }
  }
  return false;
}

export * as TreeServices from "./pages";
