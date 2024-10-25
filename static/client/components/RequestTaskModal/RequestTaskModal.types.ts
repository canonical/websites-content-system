import type { ChangeRequestType, IPage } from "@/services/api/types/pages";

export interface IRequestTaskModalProps {
  changeType: (typeof ChangeRequestType)[keyof typeof ChangeRequestType];
  copyDocLink: string;
  onClose: () => void;
  onTypeChange: React.Dispatch<React.SetStateAction<number>>;
  webpage: IPage;
}
