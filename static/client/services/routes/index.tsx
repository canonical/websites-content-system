import React from "react";

import { Route } from "react-router-dom";

import MainLayout from "@/components/MainLayout";
import NewWebpage from "@/pages/NewWebpage";
import Webpage from "@/pages/Webpage";
import { type IPage } from "@/services/api/types/pages";

export function generateRoutes(project: string, pages: IPage[]): JSX.Element[] {
  return pages.map((page, index) => (
    <React.Fragment key={`${page.name}-${index}`}>
      <Route
        element={
          <MainLayout>
            <Webpage page={page} project={project} />
          </MainLayout>
        }
        key={page.name}
        path={`/webpage/${project}${page.name}`}
      />
      <Route
        element={
          <MainLayout>
            <NewWebpage />
          </MainLayout>
        }
        key="new-webpage"
        path="/new-webpage"
      />
      {page.children?.length && generateRoutes(project, page.children)}
    </React.Fragment>
  ));
}

export * as RoutesServices from ".";
