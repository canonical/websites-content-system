import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "react-query";
import { MemoryRouter } from "react-router-dom";

import Navigation from "./Navigation";

const renderWithQuery = (children: JSX.Element) => {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{children}</QueryClientProvider>);
};

describe("Navigation", () => {
  it("displays navigation", () => {
    renderWithQuery(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  it("is collapsed by default", () => {
    renderWithQuery(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation")).toHaveClass("is-collapsed");
  });
});
