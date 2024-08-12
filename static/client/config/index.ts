let staleTime = process.env.NODE_ENV === "production" ? 300000 : 30000;

const config = {
  projects: ["canonical.com", "ubuntu.com"],
  api: {
    path: window.location.href,
    FETCH_OPTIONS: {
      retry: false,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      optimisticResults: false,
      staleTime: staleTime,
      cacheTime: staleTime,
    },
  },
};

export default config;
