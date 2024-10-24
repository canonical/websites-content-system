import type { IPage } from "@/services/api/types/pages";

export interface INewPageModalProps {
  copyDocLink: string;
  onClose: () => void;
  webpage: IPage;
}
