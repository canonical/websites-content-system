export interface IStore {
  user: string | null;
  setUser: (u: string) => void;
}
