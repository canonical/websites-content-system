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
        <img alt="" src="https://assets.ubuntu.com/v1/26e08531-content-system-logo.svg" width="175px" />
      </Link>
      {children}
    </>
  );
};

export default NavigationBanner;
