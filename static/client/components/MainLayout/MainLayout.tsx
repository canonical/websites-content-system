import { useLocation } from "react-router-dom";

import Breadcrumbs from "@/components/Breadcrumbs";
import Navigation from "@/components/Navigation";
import Search from "@/components/Search";

interface IMainLayoutProps {
  children?: JSX.Element;
}

const MainLayout = ({ children }: IMainLayoutProps): JSX.Element => {
  const location = useLocation();

  return (
    <>
      <div className="l-application">
        <Navigation />
        <main className="l-main">
          <div className="row">
            <div className="col-7">
              <Breadcrumbs />
            </div>
            <div className="col-5">
              <Search />
            </div>
          </div>
          <hr />
          <div className="row">
            {location.pathname === "/" && (
              <>
                <h2>Welcome to the Content System</h2>
                <h3 className="p-heading--4">Please select a page that you are looking for from the left sidebar</h3>
              </>
            )}
            {children}
          </div>
        </main>
      </div>
    </>
  );
};

export default MainLayout;
