/* eslint-disable testing-library/no-node-access */
import { waitFor } from "@testing-library/react";
import { act } from "react-dom/test-utils";

describe("main", () => {
  beforeAll(() => {
    const rootElement = document.createElement("div");
    rootElement.setAttribute("id", "root");
    document.body.appendChild(rootElement);
  });

  it("renders the app in the root element", async () => {
    await act(() => import("./main"));
    const container = document.getElementById("root") as HTMLElement;
    await waitFor(() => expect(container.querySelector(".l-application")).toBeInTheDocument());
  });
});
