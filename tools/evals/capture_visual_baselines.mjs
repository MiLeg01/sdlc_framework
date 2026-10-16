#!/usr/bin/env node
/** Capture representative dashboard and presentation states without changing either visual system. */

import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import {spawnSync} from "node:child_process";
import {createRequire} from "node:module";
import {pathToFileURL} from "node:url";

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, values) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), values[index + 1]]);
  return pairs;
}, []));
const root = path.resolve(args.root || process.cwd());
const outputDir = path.resolve(args.output || path.join(root, "evals/fixtures/visual-regression/screenshots"));
const manifestPath = path.resolve(args.manifest || path.join(root, "evals/fixtures/visual-regression/manifest.json"));
const reportPath = args.report ? path.resolve(args.report) : null;
const update = process.argv.includes("--update");
const nodeModules = args["node-modules"] || process.env.AGENT_COMMONS_NODE_MODULES;
if (!nodeModules) throw new Error("pass --node-modules or set AGENT_COMMONS_NODE_MODULES");
const require = createRequire(path.join(path.resolve(nodeModules), "package.json"));
const {chromium} = require("playwright");
const pixelmatchModule = require("pixelmatch");
const pixelmatch = pixelmatchModule.default || pixelmatchModule;
const {PNG} = require("pngjs");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "agent-commons-visual-"));
const dashboard = path.join(temporary, "dashboard.html");
const captureDir = update || args.output ? outputDir : path.join(temporary, "captures");
fs.mkdirSync(captureDir, {recursive: true});
const built = spawnSync("python3", [
  path.join(root, "skills/build-living-dashboard/scripts/build_dashboard.py"),
  "--data", path.join(root, "skills/build-living-dashboard/assets/dashboard-data.example.json"),
  "--dashboard-mode", "full-legacy-modernization",
  "--output", dashboard,
], {cwd: root, encoding: "utf8"});
if (built.status !== 0) throw new Error(built.stderr || built.stdout);

const states = [
  {id: "dashboard-overview", artifact: "dashboard", file: dashboard, selector: "#overview", viewport: [1440, 1000]},
  {id: "dashboard-architecture", artifact: "dashboard", file: dashboard, selector: "#application-map", viewport: [1440, 1000]},
  {id: "dashboard-requirements", artifact: "dashboard", file: dashboard, selector: "#requirements", viewport: [1440, 1000]},
  {id: "dashboard-estimation", artifact: "dashboard", file: dashboard, selector: "#modernization", viewport: [1440, 1000]},
  {id: "dashboard-detail-opener", artifact: "dashboard", file: dashboard, selector: "#detail-dialog", viewport: [1440, 1000], openDetail: true},
  {id: "dashboard-mobile", artifact: "dashboard", file: dashboard, selector: "#overview", viewport: [390, 844]},
  {id: "presentation-opening", artifact: "presentation", file: path.join(root, "presentation/index.html"), selector: "#start", viewport: [1440, 900]},
  {id: "presentation-concepts", artifact: "presentation", file: path.join(root, "presentation/index.html"), selector: "#engine", viewport: [1440, 900]},
  {id: "presentation-graph", artifact: "presentation", file: path.join(root, "presentation/index.html"), selector: "#network", viewport: [1440, 900]},
  {id: "presentation-navigator", artifact: "presentation", file: path.join(root, "presentation/index.html"), selector: "#inside", viewport: [1440, 900]},
  {id: "presentation-technical", artifact: "presentation", file: path.join(root, "presentation/index.html"), selector: "#architecture", viewport: [1440, 900]},
  {id: "presentation-closing", artifact: "presentation", file: path.join(root, "presentation/index.html"), selector: "#closing", viewport: [1440, 900]},
];

const browser = await chromium.launch({headless: true});
const results = [];
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const byId = Object.fromEntries(manifest.states.map(state => [state.id, state]));
const visualTolerance = Number(manifest.comparison_policy?.perceptual_difference_threshold ?? 0.01);
for (const state of states) {
  const page = await browser.newPage({viewport: {width: state.viewport[0], height: state.viewport[1]}, deviceScaleFactor: 1});
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(pathToFileURL(state.file).href, {waitUntil: "load"});
  await page.addStyleTag({content: "*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}"});
  await page.waitForTimeout(150);
  if (state.artifact === "presentation") {
    await page.evaluate(() => {
      const identity = document.querySelector("#start .hero-kicker span:last-child");
      if (identity) identity.textContent = "AGENT COMMONS | V1.0.0";
    });
  }
  if (state.openDetail) {
    const opener = page.locator("[data-open]:visible").first();
    if (await opener.count()) await opener.click();
  }
  const target = page.locator(state.selector).first();
  if (!(await target.count()) || !(await target.isVisible())) {
    throw new Error(`${state.id} target is not visible: ${state.selector}`);
  }
  await target.scrollIntoViewIfNeeded();
  await page.waitForTimeout(100);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  const semantic = await target.evaluate(node => ({
    text_length: (node.textContent || "").replace(/\s+/g, " ").trim().length,
    heading_count: node.querySelectorAll("h1,h2,h3").length,
    interactive_count: node.querySelectorAll("a,button,input,select,[role=button]").length,
  }));
  const grammar = await page.evaluate(artifact => artifact === "dashboard"
    ? Boolean(document.querySelector("nav.rail") && document.querySelector("main#main") && document.querySelector("[data-canonical-section]"))
    : Boolean(document.querySelector("nav.chapter-nav") && document.querySelector("main#main") && document.querySelector("section.chapter")), state.artifact);
  const destination = path.join(captureDir, `${state.id}.png`);
  if (state.artifact === "presentation") await target.screenshot({path: destination});
  else await page.screenshot({path: destination, fullPage: false});
  const payload = fs.readFileSync(destination);
  const sha256 = crypto.createHash("sha256").update(payload).digest("hex");
  const dimensions = [payload.readUInt32BE(16), payload.readUInt32BE(20)];
  const expected = byId[state.id];
  const baselineExists = expected && fs.existsSync(path.join(root, expected.screenshot));
  let pixelDifferenceRatio = null;
  if (!update && baselineExists) {
    const baselineImage = PNG.sync.read(fs.readFileSync(path.join(root, expected.screenshot)));
    const capturedImage = PNG.sync.read(payload);
    if (baselineImage.width === capturedImage.width && baselineImage.height === capturedImage.height) {
      pixelDifferenceRatio = pixelmatch(
        baselineImage.data,
        capturedImage.data,
        null,
        baselineImage.width,
        baselineImage.height,
        {threshold: 0.1, includeAA: false},
      ) / (baselineImage.width * baselineImage.height);
    }
  }
  const checks = {
    target_visible: true,
    no_horizontal_overflow: !overflow,
    no_browser_errors: errors.length === 0,
    required_content_present: semantic.text_length >= 20 && (semantic.heading_count >= 1 || semantic.interactive_count >= 1),
    canonical_design_grammar: grammar,
    dimensions_match: update || JSON.stringify(dimensions) === JSON.stringify(expected?.captured_dimensions),
    visual_difference_within_tolerance: update || (pixelDifferenceRatio !== null && pixelDifferenceRatio <= visualTolerance),
  };
  results.push({
    id: state.id,
    screenshot: update ? destination : expected?.screenshot,
    evidence_screenshot: args.output && !update ? destination : null,
    captured_sha256: sha256,
    captured_dimensions: dimensions,
    pixel_difference_ratio: pixelDifferenceRatio,
    semantic,
    baseline_hash_match: update || (baselineExists && sha256 === expected?.sha256),
    checks,
    status: Object.values(checks).every(Boolean) ? "PASS" : "FAIL",
    horizontal_overflow: overflow,
    console_errors: errors,
  });
  await page.close();
}
await browser.close();
if (update) {
  for (const result of results) {
    byId[result.id].sha256 = result.captured_sha256;
    byId[result.id].captured_dimensions = result.captured_dimensions;
  }
  manifest.capture_tool = "tools/evals/capture_visual_baselines.mjs";
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + "\n");
}
const report = {
  schema_version: 1,
  mode: update ? "update" : "verify",
  status: results.every(item => item.status === "PASS") ? "PASS" : "FAIL",
  results,
};
if (reportPath) {
  fs.mkdirSync(path.dirname(reportPath), {recursive: true});
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
}
fs.rmSync(temporary, {recursive: true, force: true});
console.log(JSON.stringify(report, null, 2));
process.exitCode = report.status === "PASS" ? 0 : 1;
