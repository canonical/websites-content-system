const path = require("path");

module.exports = {
  root: true,
  plugins: ["prettier", "no-relative-import-paths"],
  extends: [
    "./.eslintrc-auto-import.json",
    "react-app", // Use the recommended rules from CRA.
    "plugin:import/errors",
    "plugin:import/warnings",
    "plugin:import/typescript",
    "eslint-config-prettier", // Ensure this is last in the list.
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 2018,
    sourceType: "module",
  },
  rules: {
    "prettier/prettier": "error",
    "no-relative-import-paths/no-relative-import-paths": [
      "warn",
      { allowSameFolder: true, rootDir: "static/client", prefix: "@" },
    ],
  },
  settings: {
    react: {
      version: "detect",
    },
    "import/resolver": {
      typescript: {
        alias: { "@": path.resolve(__dirname, "static/client") },
      },
      node: {
        extensions: [".js", ".jsx", ".ts", ".tsx"],
      },
    },
  },
  globals: {
    usabilla_live: false,
  },
  overrides: [
    {
      files: ["static/client/**/*.ts?(x)"],
      extends: [
        "prettier",
        "plugin:import/errors",
        "plugin:import/warnings",
        "plugin:import/typescript",
        "plugin:prettier/recommended", // Ensure this is last in the list.
      ],
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
        ecmaVersion: 2018,
        sourceType: "module",
      },
      rules: {
        "prettier/prettier": "error",
        "@typescript-eslint/no-unused-vars": [
          "error",
          {
            args: "none",
            ignoreRestSiblings: true,
          },
        ],
        "no-restricted-syntax": [
          "error",
          {
            selector: "TSEnumDeclaration",
            message: "Avoid enums, use const or string literal instead",
          },
        ],
        "@typescript-eslint/consistent-type-imports": 2,
        "import/namespace": "off",
        "import/no-named-as-default": 0,
        "import/order": [
          "error",
          {
            pathGroups: [
              {
                pattern: "react",
                group: "external",
                position: "before",
              },
              {
                pattern: "~/app",
                group: "internal",
              },
            ],
            pathGroupsExcludedImportTypes: ["react"],
            "newlines-between": "always",
            alphabetize: {
              order: "asc",
            },
          },
        ],
        "no-console": "warn",
        "react/forbid-component-props": [
          "error",
          {
            forbid: [
              {
                propName: "data-test",
                message: "Use `data-testid` instead of `data-test` attribute",
              },
            ],
          },
        ],
        "react/forbid-dom-props": [
          "error",
          {
            forbid: [
              {
                propName: "data-test",
                message: "Use `data-testid` instead of `data-test` attribute",
              },
            ],
          },
        ],
        "react/jsx-sort-props": "error",
      },
      settings: {
        "import/resolver": {
          node: {
            paths: ["static/client"],
            extensions: [".js", ".jsx", ".ts", ".tsx"],
          },
        },
        react: {
          version: "detect",
        },
      },
    },
    {
      files: ["static/client/**/*.js?(x)"],
      rules: {
        "no-unused-vars": 2,
      },
    },
    {
      files: ["static/client/**/*.tsx"],
      rules: {
        "react/no-multi-comp": ["error", { ignoreStateless: true }],
      },
    },
    {
      files: ["static/client/**/*.test.[jt]s?(x)"],
      extends: ["plugin:testing-library/react"],
      plugins: ["no-only-tests"],
      rules: {
        "no-only-tests/no-only-tests": "error",
        "testing-library/prefer-find-by": "off",
        "testing-library/prefer-explicit-assert": "error",
        "testing-library/prefer-user-event": [
          "error",
          {
            // Remove once sliders can be updated with user-event
            // https://github.com/testing-library/user-event/issues/871
            allowedMethods: ["change"],
          },
        ],
        "react/no-multi-comp": "off",
      },
    },
  ],
};
