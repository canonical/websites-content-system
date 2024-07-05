import { configDefaults, coverageConfigDefaults, defineConfig } from "vitest/config";
import * as path from "path";

export default defineConfig({
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./setupTests.ts"],
    exclude: [...configDefaults.exclude, "**/tests/**"],
    coverage: {
      // exclude index files as they're only used to export other files
      // exclude pages as they're covered by playwright tests
      exclude: [...coverageConfigDefaults.exclude, "**/index.ts", "src/mocks/**/*", "src/pages/**/*", "**/types.ts"],
      include: ["src/**/*.{ts,tsx}"],
      reporter: ["text", "json", "html"],
      all: true,
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80,
    },
    clearMocks: true,
  },
});
