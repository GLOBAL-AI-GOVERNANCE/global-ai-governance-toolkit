// End-to-end test of the Lead Agent console in a real browser.
// Usage: node web/tests/lead-agent-e2e.mjs <base-url> [chrome-path]
// Needs playwright-core (or playwright) resolvable from the working directory.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { chromium } from "playwright-core";
import { Ledger } from "../lead-agent/engine.mjs";

const base = (process.argv[2] || "http://127.0.0.1:8799/").replace(/\/?$/, "/");
const executablePath = process.argv[3] || process.env.CHROME_PATH || undefined;
const browser = await chromium.launch({ executablePath, args: ["--no-sandbox"] });
const results = [];
const check = async (name, fn) => { await fn(); results.push(name); console.log("PASS", name); };

try {
  for (const [label, viewport] of [["desktop", { width: 1280, height: 900 }], ["mobile", { width: 375, height: 740 }]]) {
    const context = await browser.newContext({ viewport, acceptDownloads: true });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("dialog", (d) => d.accept());
    await page.goto(base + "lead-agent/", { waitUntil: "networkidle" });
    const agents = () => page.locator("#fleet .la-node");

    await check(`${label}: page starts with only the lead agent`, async () => {
      await page.waitForSelector('#fleet .la-node[data-agent="agent.lead"]');
      assert.equal(await agents().count(), 1);
    });

    await check(`${label}: a typed goal (keyboard only) drives a fleet scenario`, async () => {
      await page.focus("#goal");
      await page.keyboard.type("Research agent governance on docs.example.org and draft a summary");
      await page.keyboard.press("Enter");
      await page.waitForFunction(() => document.querySelectorAll("#fleet .la-node").length >= 3);
      const parents = await page.$$eval("#fleet .la-node", (nodes) => nodes.map((n) => n.textContent));
      assert.ok(parents.some((t) => t.includes("agent.research-1") && t.includes("bound to agent.lead")));
      assert.ok(await page.locator('#calls .la-call[data-tool="fetch_url"][data-dec="approved"]').count() >= 1);
      assert.ok(await page.locator('#calls .la-call[data-tool="draft_text"][data-dec="allow"]').count() >= 1);
    });

    await check(`${label}: the guard denies a Level 5 spend`, async () => {
      await page.click('.la-chip[data-goal^="Buy"]');
      const denied = page.locator('#calls .la-call[data-tool="spend_funds"][data-dec="deny"]');
      await denied.first().waitFor();
      const text = await denied.first().textContent();
      assert.match(text, /Level 5/);
      assert.match(text, /LEVEL_5_NOT_PERMITTED/);
    });

    await check(`${label}: delegation depth is capped at 3`, async () => {
      await page.click('.la-chip[data-goal^="Delegate"]');
      await page.locator('#calls .la-call[data-tool="spawn_agent"][data-dec="deny"]').first().waitFor();
      const text = await page.locator('#calls .la-call[data-tool="spawn_agent"][data-dec="deny"]').first().textContent();
      assert.match(text, /SPAWN_WOULD_EXCEED_DEPTH/);
      const depths = await page.$$eval("#fleet .la-node .la-meta", (m) => m.map((x) => Number(/Depth (\d+)/.exec(x.textContent)[1])));
      assert.equal(Math.max(...depths), 3);
    });

    await check(`${label}: suspending the lead cascades to every child`, async () => {
      await page.click('#fleet button[data-action="suspend"][data-agent="agent.lead"]');
      await page.waitForFunction(() => [...document.querySelectorAll("#fleet .la-node")].every((n) => n.dataset.state === "SUSPENDED"));
      await page.fill("#goal", "Draft a short note");
      await page.click("#send");
      await page.waitForFunction(() => document.querySelector("#log").textContent.includes("lead agent is suspended"));
      await page.click('#fleet button[data-action="reinstate"][data-agent="agent.lead"]');
      await page.waitForFunction(() => [...document.querySelectorAll("#fleet .la-node")].every((n) => n.dataset.state === "ACTIVE"));
    });

    await check(`${label}: revoking a sub-agent stops its subtree only`, async () => {
      await page.click('#fleet button[data-action="revoke"][data-agent="agent.research-1"]');
      await page.waitForFunction(() => document.querySelector('#fleet .la-node[data-agent="agent.research-1"]').dataset.state === "REVOKED");
      const states = await page.$$eval("#fleet .la-node", (n) => Object.fromEntries(n.map((x) => [x.dataset.agent, x.dataset.state])));
      assert.equal(states["agent.lead"], "ACTIVE");
      assert.equal(states["agent.research-2"], "REVOKED");
      assert.equal(states["agent.writer-1"], "ACTIVE");
    });

    await check(`${label}: shutdown test passes`, async () => {
      await page.click("#shutdown");
      await page.waitForFunction(() => /Shutdown test PASS/.test(document.querySelector("#shutdown-result").textContent));
    });

    await check(`${label}: the audit ledger verifies, exports, and detects tampering`, async () => {
      await page.click("#verify");
      await page.waitForFunction(() => document.querySelector("#audit-result").dataset.ok === "true");
      const [download] = await Promise.all([page.waitForEvent("download"), page.click("#export")]);
      const file = path.join(os.tmpdir(), `lead-agent-audit-${label}.json`);
      await download.saveAs(file);
      const doc = JSON.parse(fs.readFileSync(file, "utf8"));
      assert.equal(doc.authority_effect, "NONE");
      assert.ok((await Ledger.verify(doc)).ok);
      doc.records[3].event.kind = "edited";
      const tampered = path.join(os.tmpdir(), `lead-agent-audit-${label}-tampered.json`);
      fs.writeFileSync(tampered, JSON.stringify(doc));
      await page.setInputFiles("#check-file", tampered);
      await page.waitForFunction(() => document.querySelector("#audit-result").dataset.ok === "false");
      console.log(`  exported ledger: ${file}`);
    });

    await check(`${label}: no horizontal scroll and no page errors`, async () => {
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth), 0);
      assert.deepEqual(errors, []);
    });
    await context.close();
  }
  const server = process.env.LEAD_AGENT_SERVER;
  if (server) {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    const requests = [];
    page.on("request", (r) => requests.push(new URL(r.url()).origin));
    await page.goto(base + "lead-agent/", { waitUntil: "networkidle" });
    await check("local server: connects, runs a goal through the server, and its ledger verifies", async () => {
      await page.fill("#server-url", server);
      await page.click("#connect");
      await page.waitForFunction(() => /^Connected/.test(document.querySelector("#connect-result").textContent));
      await page.fill("#goal", "Buy a $500 dataset licence");
      await page.click("#send");
      await page.locator('#calls .la-call[data-tool="spend_funds"][data-dec="deny"]').first().waitFor();
      await page.click("#verify");
      await page.waitForFunction(() => document.querySelector("#audit-result").dataset.ok === "true");
      const origins = new Set(requests);
      origins.delete(new URL(base).origin);
      origins.delete(new URL(server).origin);
      assert.deepEqual([...origins], [], "the page contacted only its own origin and the chosen server");
    });
    await context.close();
  }
} finally {
  await browser.close();
}
console.log(`${results.length} checks passed`);
