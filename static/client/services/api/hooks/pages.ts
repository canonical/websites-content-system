import { type UseQueryOptions, useQueries } from "react-query";

import config from "@/config";
import { PagesServices } from "@/services/api/services/pages";
import type { IPagesResponse } from "@/services/api/types/pages";
import type { IApiBasicError, IUseQueryHookRest } from "@/services/api/types/query";

export function usePages(): IUseQueryHookRest<IPagesResponse[]> {
  const results = useQueries<UseQueryOptions<IPagesResponse, IApiBasicError>[]>(
    config.projects.map((project) => {
      return {
        queryKey: ["pages", project],
        queryFn: () => PagesServices.getPages(project),
      };
    }),
  );
  const isLoading = results.some((result) => result.isLoading);
  const data = results.map((result) => result.data!);
  const error = results.find((result) => !!result.error)?.error!;

  return { isLoading, data, error };
}
