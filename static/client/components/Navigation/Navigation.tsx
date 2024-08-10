import { useState } from "react";

import { Button } from "@canonical/react-components";
import classNames from "classnames";

import NavigationBanner from "./NavigationBanner";
import NavigationItems from "./NavigationItems";

import NavigationCollapseToggle from "@/components/Navigation/NavigationCollapseToggle";

const Navigation = (): JSX.Element => {
  const [isCollapsed, setIsCollapsed] = useState(true);

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
            </div>
            <div className="p-panel__content">
              <NavigationItems />
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
