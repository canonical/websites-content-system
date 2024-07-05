export interface IApiBasicError {
  type: string;
  title: string;
  status: number;
  detail: string;
}

interface IUseQueryHookBase<T extends unknown> {
  isLoading: boolean;
  data: T | undefined;
  refetch?: () => void;
}

export interface IUseQueryHookRest<T extends unknown> extends IUseQueryHookBase<T> {
  error: IApiBasicError | null;
}
