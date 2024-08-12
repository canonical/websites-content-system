import { useLocation } from "react-router-dom";

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
          <Search />
          {location.pathname === "/" && (
            <>
              <h2>Welcome to the Content System</h2>
              <h4>Please select a page that you are looking for from the left sidebar</h4>
            </>
          )}
          {children}
        </main>
      </div>
    </>
  );
};

export default MainLayout;
