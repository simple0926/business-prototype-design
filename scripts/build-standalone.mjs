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

const resolveAsset = (href) => path.resolve(assetRoot, href.replace(/^\//, ""));
const stylesheetPattern = /<link\b(?=[^>]*\brel=["']stylesheet["'])(?=[^>]*\bhref=["']([^"']+)["'])[^>]*>/gi;
const scriptPattern = /<script\b(?=[^>]*\bsrc=["']([^"']+)["'])[^>]*>\s*<\/script>/gi;

const stylesheetMatches = [...html.matchAll(stylesheetPattern)];
for (const match of stylesheetMatches) {
  const href = match[1];
  if (/^(?:https?:)?\/\//i.test(href)) throw new Error(`External stylesheet cannot be inlined: ${href}`);
  const css = await readFile(resolveAsset(href), "utf8");
  html = html.replace(match[0], `<style>\n${css.replaceAll("</style>", "<\\/style>")}\n</style>`);
}

const scriptMatches = [...html.matchAll(scriptPattern)];
for (const match of scriptMatches) {
  const src = match[1];
  if (/^(?:https?:)?\/\//i.test(src)) throw new Error(`External script cannot be inlined: ${src}`);
  const javascript = await readFile(resolveAsset(src), "utf8");
  const type = /\btype=["']module["']/i.test(match[0]) ? ' type="module"' : "";
  html = html.replace(match[0], `<script${type}>\n${javascript.replaceAll("</script>", "<\\/script>")}\n</script>`);
}

if (stylesheetMatches.length === 0 || scriptMatches.length === 0) {
  throw new Error("Expected at least one generated stylesheet and script in the built HTML.");
}

await writeFile(outputPath, html, "utf8");
console.log(outputPath);
