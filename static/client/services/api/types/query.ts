import type { QueryObserverResult } from "react-query";

import type { IPagesResponse } from "./pages";

export interface IApiBasicError {
  type: string;
  title: string;
  status: number;
  detail: string;
}

interface IUseQueryHookBase<T extends unknown> {
  isLoading: boolean;
  data: T | undefined;
  refetch?: () => Promise<QueryObserverResult<IPagesResponse, IApiBasicError>[]>;
  isFetching?: boolean;
}

export interface IUseQueryHookRest<T extends unknown> extends IUseQueryHookBase<T> {
  error: IApiBasicError | null;
}
