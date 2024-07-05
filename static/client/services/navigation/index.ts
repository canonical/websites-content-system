export function formatPageName(fullName: string): string {
  let output = fullName.split("").reverse().join("");
  if (output[0] === "/") {
    output = output.substring(1);
  }
  const slashPos = output.indexOf("/");
  return (slashPos > 0 ? output.substring(0, slashPos) : output).split("").reverse().join("");
}

export * as NavigationServices from ".";
