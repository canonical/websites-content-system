import type { IPage } from "@/services/api/types/pages";

export interface INavigationElementProps {
  activePageName: string | null;
  page: IPage;
  project: string;
  onSelect: (path: string) => void;
}
