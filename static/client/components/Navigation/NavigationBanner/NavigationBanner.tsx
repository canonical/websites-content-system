import { Link, useLocation } from "react-router-dom";

import { isSelected } from "@/components/Navigation/utils";

interface NavigationBannerProps {
  children?: React.ReactNode;
}

const NavigationBanner = ({ children }: NavigationBannerProps): JSX.Element => {
  const location = useLocation();
  const homepageLink = { url: "/", label: "Homepage" };
  return (
    <>
      <Link
        aria-current={isSelected(location.pathname, homepageLink)}
        aria-label={homepageLink.label}
        className="p-panel__logo"
        to={homepageLink.url}
      >
        <img
          alt=""
          className="is-fading-when-collapsed"
          src="https://assets.ubuntu.com/v1/26e08531-content-system-logo.svg"
          width="175px"
        />
        <img
          alt=""
          className="l-logo__collapsed"
          src="https://assets.ubuntu.com/v1/6e28b173-canonical-brand-tile.png"
          width="22px"
        />
      </Link>
      {children}
    </>
  );
};

export default NavigationBanner;
