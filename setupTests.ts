import { config } from "dotenv";
import { expect, afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import matchers from "@testing-library/jest-dom/matchers";
import { TextEncoder as NodeTextEncoder, TextDecoder as NodeTextDecoder } from "util";

config({ path: "./.env" });

// extends Vitest's expect method with methods from react-testing-library
expect.extend(matchers);

if (!globalThis.TextEncoder || !globalThis.TextDecoder) {
  globalThis.TextEncoder = NodeTextEncoder;
  // @ts-expect-error
  globalThis.TextDecoder = NodeTextDecoder;
}

// runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});
