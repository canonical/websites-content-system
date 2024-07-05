export type NavLink = {
  adminOnly?: boolean;
  highlight?: string | string[];
  icon?: string | React.ReactNode;
  label: string;
  url: string;
};

export type NavGroup = {
  navLinks: NavLink[];
  groupTitle?: string;
  groupIcon?: string | React.ReactNode;
};

export type NavItem = NavGroup | NavLink;
