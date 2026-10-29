#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
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
const cleanReference = (value) => decodeURIComponent(value.split(/[?#]/, 1)[0]);
const resolveAsset = (href, relativeRoot = assetRoot) => {
  const cleaned = cleanReference(href);
  return path.resolve(cleaned.startsWith("/") ? assetRoot : relativeRoot, cleaned.replace(/^\//, ""));
};
const encodeAsset = async (assetPath) => {
  const mime = mimeTypes.get(path.extname(assetPath).toLowerCase());
  if (!mime) throw new Error(`Unsupported standalone asset type: ${assetPath}`);
  const data = await readFile(assetPath);
  return `data:${mime};base64,${data.toString("base64")}`;
};
const inlineCssAssets = async (css, stylesheetPath) => {
  const matches = [...css.matchAll(/url\(\s*(["']?)(.*?)\1\s*\)/gi)];
  for (const match of matches) {
    const reference = match[2].trim();
    if (!reference || isEmbedded(reference)) continue;
    if (isExternal(reference)) throw new Error(`External CSS asset cannot be inlined: ${reference}`);
    const dataUrl = await encodeAsset(resolveAsset(reference, path.dirname(stylesheetPath)));
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
  const stylesheetPath = resolveAsset(href);
  const css = await inlineCssAssets(await readFile(stylesheetPath, "utf8"), stylesheetPath);
  html = html.replace(match[0], `<style>\n${css.replaceAll("</style>", "<\\/style>")}\n</style>`);
}

const scriptMatches = [...html.matchAll(scriptPattern)];
for (const match of scriptMatches) {
  const src = match[1];
  if (/^(?:https?:)?\/\//i.test(src)) throw new Error(`External script cannot be inlined: ${src}`);
  const javascript = await readFile(resolveAsset(src), "utf8");
  if (/\bimport\(\s*["'][^"']+["']\s*\)/.test(javascript)) {
    throw new Error(`Generated script contains a dynamic import; configure a single-chunk build before packaging: ${src}`);
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
