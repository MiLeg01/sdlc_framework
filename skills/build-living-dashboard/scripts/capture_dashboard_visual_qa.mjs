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
for (const name of ["html", "contract", "output", "screenshot-dir"]) {
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
const contract = JSON.parse(fs.readFileSync(path.resolve(args.contract), "utf8"));
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
let designFingerprint = null;
let brandProfileFingerprint = null;
let brandThemeFingerprint = null;
let brandAssetFingerprint = null;
let dataFingerprint = null;
let visibleBrandRoles = null;

for (const required of contract.required_rendered_states) {
  const [width, height] = required.viewport;
  const page = await browser.newPage({viewport: {width, height}, deviceScaleFactor: 1});
  const consoleErrors = [];
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("pageerror", error => consoleErrors.push(error.message));
  await page.goto(pathToFileURL(htmlPath).href, {waitUntil: "load"});
  await page.waitForTimeout(200);
  designFingerprint ||= await page.locator("html").getAttribute("data-dashboard-design-fingerprint");
  brandProfileFingerprint ||= await page.locator("html").getAttribute("data-brand-profile-fingerprint");
  brandThemeFingerprint ||= await page.locator("html").getAttribute("data-brand-theme-fingerprint");
  brandAssetFingerprint ||= await page.locator("html").getAttribute("data-brand-asset-fingerprint");
  if (!dataFingerprint) {
    const embedded = JSON.parse(await page.locator("#dashboard-data").textContent());
    dataFingerprint = embedded.fingerprint;
  }
  if (brandProfileFingerprint && !visibleBrandRoles) {
    visibleBrandRoles = await page.evaluate(() => {
      const root = getComputedStyle(document.documentElement);
      const logo = document.querySelector("[data-brand-logo]");
      const role = variable => ({value: root.getPropertyValue(variable).trim(), visible: true});
      return {
        primary: role("--accent"), secondary: role("--secondary"), highlight: role("--signature"),
        danger: role("--risk"), success: role("--good"), focus: role("--focus"), header: role("--charcoal"),
        identity: {visible: Boolean(logo && logo.getBoundingClientRect().width && logo.getBoundingClientRect().height),
          asset_fingerprint: document.documentElement.dataset.brandAssetFingerprint || ""},
      };
    });
  }
  if (required.selector === "#detail-dialog") {
    const openers = page.locator("[data-open]");
    for (let index = 0; index < await openers.count(); index += 1) {
      const opener = openers.nth(index);
      if (await opener.isVisible()) {
        await opener.click();
        break;
      }
    }
  }
  const target = page.locator(required.selector).first();
  const exists = await target.count();
  const visible = exists ? await target.isVisible() : false;
  if (visible) await target.scrollIntoViewIfNeeded();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  let mobileNavigation = true;
  if (required.id === "mobile-navigation" && exists) {
    mobileNavigation = await target.evaluate(node => {
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return style.position === "fixed" && Math.abs(innerHeight - rect.bottom) <= 2;
    });
  }
  const screenshotPath = path.join(screenshotDir, `${required.id}.png`);
  await page.screenshot({path: screenshotPath, fullPage: false});
  const status = visible && !overflow && mobileNavigation && consoleErrors.length === 0 ? "PASS" : "FAIL";
  states.push({
    id: required.id,
    viewport: required.viewport,
    ...(required.locale ? {locale: required.locale} : {}),
    selector: required.selector,
    screenshot: path.relative(path.dirname(outputPath), screenshotPath),
    status,
    checks: {visible, horizontal_overflow: overflow, mobile_navigation_fixed: mobileNavigation, console_errors: consoleErrors},
  });
  allConsoleErrors.push(...consoleErrors.map(error => `${required.id}: ${error}`));
  await page.close();
}
await browser.close();

const crypto = await import("node:crypto");
const htmlFingerprint = crypto.createHash("sha256").update(fs.readFileSync(htmlPath)).digest("hex");
const result = {
  schema_version: 2,
  status: states.every(state => state.status === "PASS") ? "PARTIAL" : "BLOCKED",
  fingerprints: {
    html: htmlFingerprint, design: designFingerprint, data: dataFingerprint,
    brand_profile: brandProfileFingerprint || null, brand_theme: brandThemeFingerprint || null,
    brand_asset: brandAssetFingerprint || null,
  },
  states,
  console_errors: allConsoleErrors,
  results: {
    VISUAL_QA_PASS: {status: states.every(state => state.status === "PASS") ? "PASS" : "FAIL", producer: "capture_dashboard_visual_qa.mjs"},
  },
  brand: brandProfileFingerprint ? {
    status: states.every(state => state.status === "PASS") ? "PASS" : "FAIL",
    profile_fingerprint: brandProfileFingerprint, theme_fingerprint: brandThemeFingerprint,
    asset_fingerprint: brandAssetFingerprint, visible_roles: visibleBrandRoles,
  } : null,
};
fs.mkdirSync(path.dirname(outputPath), {recursive: true});
fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + "\n");
console.log(`captured ${outputPath}`);
