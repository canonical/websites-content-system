import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

import type { IStore } from "./types";

export const useStore = create<IStore>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        setUser: (u) => set({ user: u }),
      }),
      {
        name: "store",
      },
    ),
  ),
);
