let staleTime = process.env.NODE_ENV === "production" ? 300000 : 30000;

const config = {
  projects: ["canonical.com", "ubuntu.com"],
  api: {
    path: "/",
    FETCH_OPTIONS: {
      retry: false,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      optimisticResults: false,
      staleTime: staleTime,
      cacheTime: staleTime,
    },
  },
  ghLink: (project: string) => `https://github.com/canonical/${project}/tree/main/templates`,
  copyStyleGuideLink: "https://docs.google.com/document/d/1AX-kSNztuAmShEoohe8L3LNLRnSKF7I0qkZGNeoGOok/edit?tab=t.0",
};

export default config;
