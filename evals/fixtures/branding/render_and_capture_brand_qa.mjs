#!/usr/bin/env node
"use strict";

import {spawnSync} from "node:child_process";

const args = process.argv.slice(2);
const value = name => {
  const index = args.indexOf(name);
  if (index < 0 || !args[index + 1]) throw new Error(`missing ${name}`);
  return args[index + 1];
};
const optionalValue = name => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
};
const run = (command, commandArgs) => {
  const completed = spawnSync(command, commandArgs, {encoding: "utf8"});
  if (completed.stdout) process.stdout.write(completed.stdout);
  if (completed.stderr) process.stderr.write(completed.stderr);
  if (completed.error) throw completed.error;
  if (completed.status !== 0) process.exit(completed.status ?? 1);
};

const template = value("--template");
const brandProfile = value("--brand-profile");
const html = value("--html");
const output = value("--output");
const artifactKind = value("--artifact-kind");
const nodeModules = optionalValue("--node-modules");

run("python3", [
  "skills/create-branded-html-artifact/scripts/render_branded_html.py",
  "--template", template,
  "--brand-profile", brandProfile,
  "--output", html,
]);
run("python3", [
  "skills/validate-visual-artifact/scripts/validate_html.py",
  html,
  "--json",
]);
const captureArgs = [
  "skills/validate-visual-artifact/scripts/capture_brand_qa.mjs",
  "--html", html,
  "--brand-profile", brandProfile,
  "--output", output,
  "--artifact-kind", artifactKind,
];
if (nodeModules) captureArgs.push("--node-modules", nodeModules);
run(process.execPath, captureArgs);
run("python3", [
  "skills/validate-visual-artifact/scripts/validate_html.py",
  html,
  "--brand-profile", brandProfile,
  "--brand-qa", output,
  "--json",
]);
