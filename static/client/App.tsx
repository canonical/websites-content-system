import { QueryClient, QueryClientProvider } from "react-query";

import "./App.scss";
import Main from "./pages/Main";

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Main />
    </QueryClientProvider>
  );
};

export default App;
