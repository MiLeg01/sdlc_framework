#!/usr/bin/env node
import fs from "node:fs";
import {createRequire} from "node:module";
import path from "node:path";
import process from "node:process";
import {pathToFileURL} from "node:url";

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, values) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), values[index + 1]]);
  return pairs;
}, []));
for (const name of ["html", "states", "output", "screenshot-dir"]) {
  if (!args[name]) throw new Error(`missing --${name}`);
}

const nodeModules = args["node-modules"] || process.env.AGENT_COMMONS_NODE_MODULES;
const require = createRequire(nodeModules ? path.join(path.resolve(nodeModules), "package.json") : import.meta.url);
let chromium;
try {
  ({chromium} = require("playwright"));
} catch (error) {
  throw new Error("Playwright is required; install it locally or pass --node-modules <path containing playwright>", {cause: error});
}

const htmlPath = path.resolve(args.html);
const statesDocument = JSON.parse(fs.readFileSync(path.resolve(args.states), "utf8"));
const requiredStates = Array.isArray(statesDocument) ? statesDocument : statesDocument.states;
if (!Array.isArray(requiredStates) || !requiredStates.length) throw new Error("states must contain a non-empty array");
const outputPath = path.resolve(args.output);
const screenshotDir = path.resolve(args["screenshot-dir"]);
fs.mkdirSync(screenshotDir, {recursive: true});

const browserOptions = {
  headless: true,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-crash-reporter", "--no-zygote", "--disable-gpu"],
  ...(args["browser-executable"] ? {executablePath: path.resolve(args["browser-executable"])} : {}),
};
async function launchBrowser() {
  let lastError;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      return await chromium.launch(browserOptions);
    } catch (error) {
      lastError = error;
      if (attempt < 3) {
        console.warn(`Chromium launch attempt ${attempt} failed; retrying`);
        await new Promise(resolve => setTimeout(resolve, attempt * 500));
      }
    }
  }
  throw lastError;
}
const browser = await launchBrowser();
const states = [];
const allConsoleErrors = [];

for (const required of requiredStates) {
  const [width, height] = required.viewport;
  const page = await browser.newPage({viewport: {width, height}, deviceScaleFactor: 1});
  const consoleErrors = [];
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("pageerror", error => consoleErrors.push(error.message));
  await page.goto(pathToFileURL(htmlPath).href, {waitUntil: "load"});
  await page.waitForTimeout(200);
  const selector = required.selector || "body";
  if (selector === "#detail-dialog") {
    const opener = page.locator("[data-open], [aria-haspopup=dialog]").first();
    if (await opener.count() && await opener.isVisible()) await opener.click();
  }
  const target = page.locator(selector).first();
  const exists = await target.count();
  const visible = exists ? await target.isVisible() : false;
  if (visible) await target.scrollIntoViewIfNeeded();
  const overflow = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const sources = [...document.querySelectorAll("body *")].flatMap(element => {
      const rect = element.getBoundingClientRect();
      if (rect.right <= viewportWidth + 1 && rect.left >= -1) return [];
      const identity = element.id
        ? `#${element.id}`
        : `${element.tagName.toLowerCase()}${[...element.classList].map(name => `.${name}`).join("")}`;
      return [{
        element: identity,
        left: Math.round(rect.left * 10) / 10,
        right: Math.round(rect.right * 10) / 10,
        width: Math.round(rect.width * 10) / 10,
      }];
    }).slice(0, 10);
    return {
      horizontal: document.documentElement.scrollWidth > viewportWidth + 1,
      document_width: document.documentElement.scrollWidth,
      viewport_width: viewportWidth,
      sources,
    };
  });
  const horizontalOverflow = overflow.horizontal;
  const screenshotPath = path.join(screenshotDir, `${required.id}.png`);
  await page.screenshot({path: screenshotPath, fullPage: false});
  const status = visible && !horizontalOverflow && consoleErrors.length === 0 ? "PASS" : "FAIL";
  states.push({
    id: required.id,
    viewport: required.viewport,
    ...(required.locale ? {locale: required.locale} : {}),
    selector,
    screenshot: path.relative(path.dirname(outputPath), screenshotPath),
    status,
    checks: {
      visible,
      horizontal_overflow: horizontalOverflow,
      overflow_sources: overflow.sources,
      document_width: overflow.document_width,
      viewport_width: overflow.viewport_width,
      console_errors: consoleErrors,
    },
  });
  allConsoleErrors.push(...consoleErrors.map(error => `${required.id}: ${error}`));
  await page.close();
}
await browser.close();

const result = {
  schema_version: 1,
  status: states.every(state => state.status === "PASS") ? "PASS" : "FAIL",
  artifact: path.relative(path.dirname(outputPath), htmlPath),
  browser: {engine: "chromium"},
  states,
  console_errors: allConsoleErrors,
};
fs.mkdirSync(path.dirname(outputPath), {recursive: true});
fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + "\n");
console.log(`captured ${outputPath}`);
