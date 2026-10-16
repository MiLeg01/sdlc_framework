#!/usr/bin/env node
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, values) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), values[index + 1]]);
  return pairs;
}, []));
for (const name of ["html", "brand-profile", "output", "artifact-kind"]) {
  if (!args[name]) throw new Error(`missing --${name}`);
}
if (!["dashboard", "presentation"].includes(args["artifact-kind"])) throw new Error("artifact kind must be dashboard or presentation");
const nodeModules = args["node-modules"] || process.env.AGENT_COMMONS_NODE_MODULES;
const require = createRequire(nodeModules ? path.join(path.resolve(nodeModules), "package.json") : import.meta.url);
let chromium;
try {
  ({chromium} = require("playwright"));
} catch (error) {
  throw new Error("Playwright is required; install it locally or pass --node-modules <path containing playwright>", {cause: error});
}

const htmlPath = path.resolve(args.html);
const profilePath = path.resolve(args["brand-profile"]);
const outputPath = path.resolve(args.output);
const suppliedProfile = JSON.parse(fs.readFileSync(profilePath, "utf8"));
const screenshotPath = path.resolve(args.screenshot || path.join(path.dirname(outputPath), `${args["artifact-kind"]}-brand-qa.png`));
// Brand fidelity has to hold at the widths the artifact is actually delivered at, so identity, reflow,
// and console health are captured per named viewport rather than at one desktop width.
const VIEWPORTS = [
  {id: "desktop", width: 1440, height: 1000},
  {id: "tablet", width: 768, height: 1024},
  {id: "mobile", width: 390, height: 844},
];
const viewportScreenshot = id => (
  id === "desktop"
    ? screenshotPath
    : path.join(path.dirname(screenshotPath), `${path.basename(screenshotPath, ".png")}-${id}.png`)
);
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
const selectors = args["artifact-kind"] === "dashboard" ? {
  body: "body",
  header: "[data-brand-validation-role=header]",
  navigation: "[data-brand-validation-role=navigation]",
  link: "a",
  button: "button:not([hidden])",
  focus: "button:not([hidden]), a",
  status: "[data-brand-validation-role=status]",
  panel: ".status-panel, .panel, .metric, .generic-item",
  table: "table, [role=table], .record-list",
  footer: "footer",
} : {
  body: "body",
  header: "[data-brand-validation-role=header]",
  navigation: "[data-brand-validation-role=navigation]",
  link: "a",
  button: "button:not([hidden])",
  focus: "button:not([hidden]), a",
  panel: ".proof, section",
  footer: "footer",
};

async function captureViewport(browser, viewport) {
  const page = await browser.newPage({
    viewport: {width: viewport.width, height: viewport.height},
    deviceScaleFactor: 1,
  });
  const consoleErrors = [];
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("pageerror", error => consoleErrors.push(error.message));
  await page.goto(pathToFileURL(htmlPath).href, {waitUntil: "load"});
  await page.waitForTimeout(250);
  const embeddedProfile = await page.evaluate(() => {
    const direct = document.getElementById("brand-profile")?.textContent?.trim();
    if (direct) return JSON.parse(direct);
    const dashboard = document.getElementById("dashboard-data")?.textContent?.trim();
    return dashboard ? JSON.parse(dashboard).brand_profile : null;
  });

  const elements = [];
  for (const [role, selector] of Object.entries(selectors)) {
    const locator = page.locator(selector).first();
    const count = await locator.count();
    if (!count) {
      elements.push({role, selector, visible: false, styles: {}});
      continue;
    }
    if (role === "focus") await locator.focus();
    const result = await locator.evaluate(node => {
      const style = getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return {
        visible: rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none",
        styles: {
          color: style.color,
          backgroundColor: style.backgroundColor,
          borderTopColor: style.borderTopColor,
          borderBottomColor: style.borderBottomColor,
          outlineColor: style.outlineColor,
          textDecorationColor: style.textDecorationColor,
          fontFamily: style.fontFamily,
          boxShadow: style.boxShadow,
        },
      };
    });
    elements.push({role, selector, ...result});
  }

  const logo = page.locator("[data-brand-logo]").first();
  const logoVisible = await logo.count() ? await logo.evaluate(node => {
    const rect = node.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && node.getAttribute("src")?.startsWith("data:image/");
  }) : false;
  const overflow = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const sources = [...document.querySelectorAll("body *")].flatMap(element => {
      const rect = element.getBoundingClientRect();
      if (rect.right <= viewportWidth + 1 && rect.left >= -1) return [];
      const identity = element.id
        ? `#${element.id}`
        : `${element.tagName.toLowerCase()}${[...element.classList].map(name => `.${name}`).join("")}`;
      return [{element: identity, left: Math.round(rect.left * 10) / 10, right: Math.round(rect.right * 10) / 10}];
    }).slice(0, 10);
    return {
      horizontal: document.documentElement.scrollWidth > viewportWidth + 1,
      document_width: document.documentElement.scrollWidth,
      viewport_width: viewportWidth,
      sources,
    };
  });
  const shot = viewportScreenshot(viewport.id);
  await page.screenshot({path: shot, fullPage: true});
  await page.close();
  return {
    id: viewport.id,
    viewport: [viewport.width, viewport.height],
    embeddedProfile,
    elements,
    logoVisible,
    consoleErrors,
    horizontal_overflow: overflow.horizontal,
    document_width: overflow.document_width,
    viewport_width: overflow.viewport_width,
    overflow_sources: overflow.sources,
    screenshot: path.relative(path.dirname(outputPath), shot),
  };
}

const browser = await launchBrowser();
const captures = [];
for (const viewport of VIEWPORTS) captures.push(await captureViewport(browser, viewport));
await browser.close();

const desktop = captures.find(capture => capture.id === "desktop");
const profile = desktop.embeddedProfile || suppliedProfile;
const consoleErrors = captures.flatMap(
  capture => capture.consoleErrors.map(error => `${capture.id}: ${error}`),
);
const crypto = await import("node:crypto");
const htmlSha256 = crypto.createHash("sha256").update(fs.readFileSync(htmlPath)).digest("hex");
const result = {
  schema_version: 2,
  artifact_kind: args["artifact-kind"],
  profile_fingerprint: profile.profile_fingerprint,
  theme_fingerprint: profile.theme_fingerprint,
  asset_fingerprint: profile.asset_fingerprint,
  html_sha256: htmlSha256,
  assets: {favicon: profile.assets.favicon.sha256, logo: profile.assets.logo.sha256},
  browser: {
    engine: "chromium",
    viewport: desktop.viewport,
    viewports: captures.map(capture => capture.viewport),
    console_errors: consoleErrors,
  },
  elements: desktop.elements,
  responsive: captures.map(capture => ({
    id: capture.id,
    viewport: capture.viewport,
    brand_visible: capture.logoVisible,
    horizontal_overflow: capture.horizontal_overflow,
    document_width: capture.document_width,
    viewport_width: capture.viewport_width,
    overflow_sources: capture.overflow_sources,
    console_errors: capture.consoleErrors,
    elements: capture.elements,
    screenshot: capture.screenshot,
  })),
  browser_render: {
    brand_visible: captures.every(capture => capture.logoVisible) && consoleErrors.length === 0,
    screenshot: desktop.screenshot,
  },
};
fs.mkdirSync(path.dirname(outputPath), {recursive: true});
fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + "\n");
console.log(`captured ${outputPath}`);
