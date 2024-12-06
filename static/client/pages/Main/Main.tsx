import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import MainLayout from "@/components/MainLayout";
import { usePages } from "@/services/api/hooks/pages";
import { RoutesServices } from "@/services/routes";

const Main = (): React.ReactNode => {
  const { data } = usePages();

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />} path="/app" />
        <Route element={<Navigate to="/app" />} path="/" />
        {data?.length &&
          data.map(
            (project) =>
              project?.data?.templates && RoutesServices.generateRoutes(project.data.name, [project.data.templates]),
          )}
      </Routes>
    </BrowserRouter>
  );
};

export default Main;
