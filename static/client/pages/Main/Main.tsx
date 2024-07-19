import { BrowserRouter, Route, Routes } from "react-router-dom";

import Login from "@/components/Login";
import MainLayout from "@/components/MainLayout";
import { usePages } from "@/services/api/hooks/pages";
import { RoutesServices } from "@/services/routes";

const Main = (): React.ReactNode => {
  const { data } = usePages();

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />} path="/" />
        <Route element={<Login />} path="/login" />
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
