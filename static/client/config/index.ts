const config = {
  projects: ["canonical.com", "ubuntu.com"],
  api: {
    path: "http://0.0.0.0:8104",
    FETCH_OPTIONS: {
      retry: false,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      optimisticResults: false,
      staleTime: 300000,
      cacheTime: 300000,
    },
  },
};

export default config;
