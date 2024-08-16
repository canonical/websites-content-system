import React, { useEffect, useState } from "react";

import { useLocation } from "react-router-dom";

import { type IBreadcrumb } from "./Breadcrumbs.types";

const Breadcrumbs = () => {
  const location = useLocation();
  const [breadcrumbs, setBreadcrumbs] = useState<IBreadcrumb[]>([]);

  useEffect(() => {
    const pageIndex = location.pathname.indexOf("webpage/");
    if (pageIndex > 0) {
      const parts = location.pathname.substring(pageIndex + 8).split("/");
      if (parts.length) {
        let accumulatedPath = "";
        const paths = parts?.map((part) => {
          accumulatedPath = `${accumulatedPath}/${part}`;
          return {
            name: part,
            link: `/webpage${accumulatedPath}`,
          };
        });
        setBreadcrumbs(paths);
      }
    } else {
      setBreadcrumbs([]);
    }
  }, [location]);

  return (
    <div className="l-breadcrumbs">
      {breadcrumbs.map((bc, index) => (
        <React.Fragment key={`bc-${index}`}>
          {index < breadcrumbs.length - 1 ? (
            <a className="p-text--small-caps" href={bc.link}>
              {bc.name}
            </a>
          ) : (
            <span className="p-text--small-caps">{bc.name}</span>
          )}
          {index < breadcrumbs.length - 1 && <span>&nbsp;/&nbsp;</span>}
        </React.Fragment>
      ))}
    </div>
  );
};

export default Breadcrumbs;
