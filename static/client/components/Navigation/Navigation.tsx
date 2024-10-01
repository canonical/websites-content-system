import React, { useCallback, useState } from "react";

import { Button } from "@canonical/react-components";
import classNames from "classnames";
import { useNavigate } from "react-router-dom";

import NavigationBanner from "./NavigationBanner";
import NavigationItems from "./NavigationItems";

import NavigationCollapseToggle from "@/components/Navigation/NavigationCollapseToggle";
import SiteSelector from "@/components/SiteSelector";

const Navigation = (): JSX.Element => {
  const navigate = useNavigate();
  const [isCollapsed, setIsCollapsed] = useState(true);

  const logout = useCallback(() => {
    window.open("/logout", "_self");
  }, []);

  const handleNewPageClick = useCallback(() => {
    navigate("/new-webpage");
  }, [navigate]);

  return (
    <>
      <header className="l-navigation-bar">
        <div className="p-panel is-dark">
          <div className="p-panel__header">
            <NavigationBanner />
            <div className="p-panel__controls u-nudge-down--small">
              <Button appearance="base" className="has-icon" onClick={() => setIsCollapsed(!isCollapsed)}>
                Menu
              </Button>
            </div>
          </div>
        </div>
      </header>
      <nav aria-label="main" className={classNames("l-navigation", { "is-collapsed": isCollapsed })} role="navigation">
        <div className="l-navigation__drawer">
          <div className="p-panel is-dark">
            <div className="p-panel__header is-sticky">
              <NavigationBanner />
              <div className="l-navigation__controls">
                <NavigationCollapseToggle isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
              </div>
              <SiteSelector />
              <Button appearance="" hasIcon onClick={handleNewPageClick}>
                <React.Fragment key=".0">
                  <i className="p-icon--plus" /> <span>Request new page</span>
                </React.Fragment>
              </Button>
            </div>
            <div className="p-panel__content">
              <NavigationItems />
            </div>
            <div className="p-panel__footer p-side-navigation--icons">
              <Button appearance="base" className="p-side-navigation__link" onClick={logout}>
                <i className="p-icon--logout is-light p-side-navigation__icon" />
                <span className="p-side-navigation__label">Log out</span>
              </Button>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
