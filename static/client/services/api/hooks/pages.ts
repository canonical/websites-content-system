import { useCallback } from "react";

import { type UseQueryOptions, useQueries } from "react-query";

import config from "@/config";
import { PagesServices } from "@/services/api/services/pages";
import type { IPagesResponse } from "@/services/api/types/pages";
import type { IApiBasicError, IUseQueryHookRest } from "@/services/api/types/query";

export function usePages(noCache: boolean = false): IUseQueryHookRest<IPagesResponse[]> {
  const results = useQueries<UseQueryOptions<IPagesResponse, IApiBasicError>[]>(
    config.projects.map((project) => {
      return {
        queryKey: ["pages", project],
        queryFn: () => PagesServices.getPages(project, noCache),
        staleTime: noCache ? 0 : 300000,
        cacheTime: noCache ? 0 : 300000,
        refetchOnMount: false,
        refetchOnWindowFocus: false,
        retry: false,
      };
    }),
  );

  const refetch = useCallback(() => {
    return Promise.all(results.map((result) => result.refetch()));
  }, [results]);

  const isLoading = results.some((result) => result.isLoading);
  const isFetching = results.some((result) => result.isFetching);
  const data = results.map((result) => result.data!);
  const error = results.find((result) => !!result.error)?.error!;

  return { isLoading, data, error, refetch, isFetching };
}
