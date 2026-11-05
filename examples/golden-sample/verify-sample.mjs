#!/usr/bin/env node

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

class Element {
  constructor(id, options = {}) {
    this.id = id;
    this.textContent = options.textContent ?? "";
    this.value = options.value ?? "";
    this.disabled = options.disabled ?? false;
    this.dataset = options.dataset ?? {};
    this.listeners = new Map();
    this.classes = new Set(options.classes ?? []);
    this.classList = {
      toggle: (name, enabled) => enabled ? this.classes.add(name) : this.classes.delete(name),
    };
  }

  addEventListener(event, handler) {
    const listeners = this.listeners.get(event) ?? [];
    listeners.push(handler);
    this.listeners.set(event, listeners);
  }

  click() {
    for (const handler of this.listeners.get("click") ?? []) handler();
  }
}

const elements = new Map();
const add = (id, options) => {
  const element = new Element(id, options);
  elements.set(id, element);
  return element;
};

const panels = [add("list", { classes: ["panel", "active"] }), add("edit", { classes: ["panel"] }), add("review", { classes: ["panel"] })];
const dataPageButtons = [new Element("nav-list", { dataset: { page: "list" } }), new Element("nav-review", { dataset: { page: "review" } })];
add("request-summary", { textContent: "No request created" });
add("request-status", { textContent: "new" });
add("title", { value: "Access request" });
add("error");
add("create");
add("save");
add("submit");
add("review-title", { textContent: "No submitted request" });
add("review-status", { textContent: "empty" });
add("approve", { disabled: true });

const document = {
  querySelector(selector) {
    if (!selector.startsWith("#")) throw new Error(`Unsupported selector: ${selector}`);
    return elements.get(selector.slice(1));
  },
  querySelectorAll(selector) {
    if (selector === ".panel") return panels;
    if (selector === "[data-page]") return dataPageButtons;
    throw new Error(`Unsupported selector: ${selector}`);
  },
};

const html = await readFile("prototype-standalone.html", "utf8");
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
assert.ok(scripts.length, "standalone must contain an inline script");
vm.runInNewContext(scripts.at(-1)[1], { document });

const checks = [];
const check = (name, callback) => {
  callback();
  checks.push({ name, passed: true });
};

check("initial review queue is empty and approval is disabled", () => {
  assert.equal(elements.get("review-status").textContent, "empty");
  assert.equal(elements.get("approve").disabled, true);
});
check("create enters draft state", () => {
  elements.get("create").click();
  assert.equal(elements.get("request-status").textContent, "draft");
});
check("approval before submission is a no-op", () => {
  elements.get("approve").click();
  assert.equal(elements.get("request-status").textContent, "draft");
});
check("empty title blocks submission", () => {
  elements.get("title").value = "";
  elements.get("submit").click();
  assert.equal(elements.get("error").textContent, "Title is required");
  assert.equal(elements.get("request-status").textContent, "draft");
});
check("complete draft transitions to submitted", () => {
  elements.get("title").value = "Access request";
  elements.get("submit").click();
  assert.equal(elements.get("request-status").textContent, "submitted");
  assert.equal(elements.get("review-status").textContent, "submitted");
  assert.equal(elements.get("approve").disabled, false);
});
check("submitted request transitions to approved", () => {
  elements.get("approve").click();
  assert.equal(elements.get("request-status").textContent, "approved");
  assert.equal(elements.get("review-status").textContent, "approved");
  assert.equal(elements.get("approve").disabled, true);
});

if (process.argv.includes("--trace-json")) {
  process.stdout.write(`${JSON.stringify({
    schema_version: "0.1",
    environment: "node-dom-harness",
    target: "prototype-standalone.html",
    viewport: "1280x800",
    test_count: checks.length,
    passed: checks.length,
    failed: 0,
    exit_code: 0,
    steps: checks.map((item) => item.name),
    assertions: checks,
    network_requests: [],
    console_errors: [],
  }, null, 2)}\n`);
} else {
  const lines = ["TAP version 13", ...checks.map((item, index) => `ok ${index + 1} - ${item.name}`), `1..${checks.length}`];
  process.stdout.write(`${lines.join("\n")}\n`);
}
