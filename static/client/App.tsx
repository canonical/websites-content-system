import { useEffect } from "react";

import { QueryClient, QueryClientProvider } from "react-query";
import { useNavigate } from "react-router-dom";

import "./App.scss";
import Main from "./pages/Main";
import { useStore } from "./store";

const queryClient = new QueryClient();

const App: React.FC = () => {
  const [user] = useStore((state) => [state.user]);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) navigate("/login");
  }, [user, navigate]);

  return (
    <QueryClientProvider client={queryClient}>
      <Main />
    </QueryClientProvider>
  );
};

export default App;
