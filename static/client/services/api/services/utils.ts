export function debounce<T>(func: (arg: string) => Promise<T>, wait: number): (arg: string) => Promise<T> {
  let timeout: NodeJS.Timeout | undefined;

  return function (arg: string): Promise<T> {
    if (timeout) {
      clearTimeout(timeout);
    }

    return new Promise<T>((resolve, reject) => {
      timeout = setTimeout(async () => {
        try {
          const result = await func(arg);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, wait);
    });
  };
}

export * as UtilServices from "./utils";
