#!/usr/bin/env node

import { readFile, realpath, writeFile } from "node:fs/promises";
import path from "node:path";

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${key}`);
    args[key.slice(2)] = value;
    index += 1;
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (!args.input || !args.output) {
  throw new Error("Usage: node build-standalone.mjs --input <built-index.html> --output <standalone.html>");
}

const inputPath = path.resolve(args.input);
const outputPath = path.resolve(args.output);
const assetRoot = path.dirname(inputPath);
const assetRootReal = await realpath(assetRoot);
let html = await readFile(inputPath, "utf8");

const mimeTypes = new Map([
  [".avif", "image/avif"],
  [".gif", "image/gif"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".webp", "image/webp"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
  [".ttf", "font/ttf"],
  [".otf", "font/otf"],
  [".mp3", "audio/mpeg"],
  [".mp4", "video/mp4"],
]);

const isEmbedded = (value) => /^(?:data:|#|javascript:)/i.test(value);
const isExternal = (value) => /^(?:https?:)?\/\//i.test(value) || /^blob:/i.test(value);
const codeMask = (value, { css = false } = {}) => {
  const output = [...value];
  let mode = "code";
  let templateDepth = null;
  for (let index = 0; index < value.length;) {
    const char = value[index];
    const following = value[index + 1] ?? "";
    if (mode === "code") {
      if (!css && char === "/" && following === "/") {
        output[index] = output[index + 1] = " "; mode = "lineComment"; index += 2; continue;
      }
      if (char === "/" && following === "*") {
        output[index] = output[index + 1] = " "; mode = "blockComment"; index += 2; continue;
      }
      if (char === "'" || char === '"') {
        output[index] = " "; mode = char === "'" ? "single" : "double"; index += 1; continue;
      }
      if (!css && char === "`") {
        output[index] = " "; mode = "template"; index += 1; continue;
      }
      if (templateDepth !== null) {
        if (char === "{") templateDepth += 1;
        if (char === "}" && --templateDepth === 0) {
          output[index] = " "; templateDepth = null; mode = "template";
        }
      }
      index += 1; continue;
    }
    output[index] = char === "\n" ? "\n" : " ";
    if (mode === "lineComment" && char === "\n") mode = "code";
    else if (mode === "blockComment" && char === "*" && following === "/") {
      output[index + 1] = " "; mode = "code"; index += 2; continue;
    } else if (["single", "double", "template"].includes(mode) && char === "\\") {
      if (index + 1 < value.length) output[index + 1] = value[index + 1] === "\n" ? "\n" : " ";
      index += 2; continue;
    } else if (mode === "single" && char === "'") mode = "code";
    else if (mode === "double" && char === '"') mode = "code";
    else if (mode === "template" && char === "`") mode = "code";
    else if (mode === "template" && char === "$" && following === "{") {
      output[index + 1] = " "; templateDepth = 1; mode = "code"; index += 2; continue;
    }
    index += 1;
  }
  return output.join("");
};
const decodeCssIdentifiers = (value) => value
  .replace(/\\([0-9a-f]{1,6})\s?/gi, (_, codepoint) => String.fromCodePoint(Number.parseInt(codepoint, 16)))
  .replace(/\\([^0-9a-f\n])/gi, "$1");
const cleanReference = (value) => decodeURIComponent(value.split(/[?#]/, 1)[0]);
const resolveAsset = async (href, relativeRoot = assetRoot) => {
  const cleaned = cleanReference(href);
  const candidate = path.resolve(cleaned.startsWith("/") ? assetRoot : relativeRoot, cleaned.replace(/^\//, ""));
  const resolved = await realpath(candidate);
  const relative = path.relative(assetRootReal, resolved);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error(`Standalone asset escapes the build root: ${href}`);
  }
  return resolved;
};
const encodeAsset = async (assetPath) => {
  const mime = mimeTypes.get(path.extname(assetPath).toLowerCase());
  if (!mime) throw new Error(`Unsupported standalone asset type: ${assetPath}`);
  const data = await readFile(assetPath);
  return `data:${mime};base64,${data.toString("base64")}`;
};
const inlineCssAssets = async (css, stylesheetPath) => {
  const cssAtRules = decodeCssIdentifiers(codeMask(css, { css: true }));
  if (/@import\b/i.test(cssAtRules)) {
    throw new Error("CSS @import must be bundled before standalone packaging.");
  }
  const matches = [...css.matchAll(/url\(\s*(["']?)(.*?)\1\s*\)/gi)];
  for (const match of matches) {
    const reference = match[2].trim();
    if (!reference || isEmbedded(reference)) continue;
    if (isExternal(reference)) throw new Error(`External CSS asset cannot be inlined: ${reference}`);
    const dataUrl = await encodeAsset(await resolveAsset(reference, path.dirname(stylesheetPath)));
    css = css.replaceAll(match[0], `url("${dataUrl}")`);
  }
  return css;
};

const stylesheetPattern = /<link\b(?=[^>]*\brel=["']stylesheet["'])(?=[^>]*\bhref=["']([^"']+)["'])[^>]*>/gi;
const scriptPattern = /<script\b(?=[^>]*\bsrc=["']([^"']+)["'])[^>]*>\s*<\/script>/gi;

const stylesheetMatches = [...html.matchAll(stylesheetPattern)];
for (const match of stylesheetMatches) {
  const href = match[1];
  if (/^(?:https?:)?\/\//i.test(href)) throw new Error(`External stylesheet cannot be inlined: ${href}`);
  const stylesheetPath = await resolveAsset(href);
  const css = await inlineCssAssets(await readFile(stylesheetPath, "utf8"), stylesheetPath);
  html = html.replace(match[0], `<style>\n${css.replaceAll("</style>", "<\\/style>")}\n</style>`);
}

const scriptMatches = [...html.matchAll(scriptPattern)];
for (const match of scriptMatches) {
  const src = match[1];
  if (/^(?:https?:)?\/\//i.test(src)) throw new Error(`External script cannot be inlined: ${src}`);
  const javascript = await readFile(await resolveAsset(src), "utf8");
  const dependencyScan = codeMask(javascript);
  if (/(?<![\w$.])import\b(?!\s*\.\s*meta\b)/.test(dependencyScan)) {
    throw new Error(`Generated script contains an import dependency; configure a single-chunk build before packaging: ${src}`);
  }
  if (/(?:^|[;\n])\s*export\b[^;\n]*\bfrom\b/i.test(dependencyScan)) {
    throw new Error(`Generated script contains an export-from dependency; configure a single-chunk build before packaging: ${src}`);
  }
  const type = /\btype=["']module["']/i.test(match[0]) ? ' type="module"' : "";
  html = html.replace(match[0], `<script${type}>\n${javascript.replaceAll("</script>", "<\\/script>")}\n</script>`);
}

if (stylesheetMatches.length === 0 && !/<style\b[^>]*>[\s\S]*?\S[\s\S]*?<\/style>/i.test(html)) {
  throw new Error("Expected a generated stylesheet or a nonempty inline style.");
}
if (scriptMatches.length === 0 && !/<script\b(?![^>]*\bsrc=)[^>]*>[\s\S]*?\S[\s\S]*?<\/script>/i.test(html)) {
  throw new Error("Expected a generated script or a nonempty inline script.");
}

await writeFile(outputPath, html, "utf8");
console.log(outputPath);
