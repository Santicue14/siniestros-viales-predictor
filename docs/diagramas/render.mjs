import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { render } from "pele";

const dir = dirname(fileURLToPath(import.meta.url));

for (const name of readdirSync(dir).filter((archivo) => archivo.endsWith(".mmd")).sort()) {
  const source = readFileSync(join(dir, name), "utf8");
  const { svg, type } = render(source);
  const out = name.replace(/\.mmd$/, ".svg");
  writeFileSync(join(dir, out), svg, "utf8");
  console.log(`${out} (${type}, ${svg.length} bytes)`);
}
