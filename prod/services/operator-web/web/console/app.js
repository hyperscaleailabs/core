// Live console for the Agent Simulation Control Plane (ASC-043).
// Talks to control-api; falls back to a local dev API when no runtime config is injected.
"use strict";

const CFG = window.ASC_CONFIG || {};
const API = (CFG.controlApiBaseUrl && CFG.controlApiBaseUrl.trim()) || "http://127.0.0.1:8010";
const GRAFANA = CFG.grafanaBaseUrl || "";
const SUPERSET = CFG.supersetBaseUrl || "";

const $ = (id) => document.getElementById(id);
const state = { experimentId: null, lastRunId: null };

async function api(path, opts) {
  const res = await fetch(API + path, {
    headers: { "content-type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${opts && opts.method || "GET"} ${path} -> ${res.status}`);
  return res.status === 204 ? null : res.json();
}

async function checkHealth() {
  const el = $("apiStatus");
  try {
    await api("/healthz");
    el.textContent = "control-api: connected";
    el.className = "status ok";
  } catch (e) {
    el.textContent = "control-api: unreachable (" + API + ")";
    el.className = "status err";
  }
}

// ---- tabs ----
document.querySelectorAll(".tab[data-tab]").forEach((t) =>
  t.addEventListener("click", () => {
    document.querySelectorAll(".tab[data-tab]").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    t.classList.add("active");
    $("tab-" + t.dataset.tab).classList.add("active");
  })
);

// ---- observability subtabs ----
function setFrame(which) {
  document.querySelectorAll(".subtab").forEach((s) => s.classList.toggle("active", s.dataset.frame === which));
  const base = which === "grafana" ? GRAFANA : SUPERSET;
  const frame = $("obsFrame");
  if (base) { frame.src = base; $("obsNote").classList.add("hidden"); }
  else { frame.removeAttribute("src"); $("obsNote").classList.remove("hidden"); }
}
document.querySelectorAll(".subtab").forEach((s) => s.addEventListener("click", () => setFrame(s.dataset.frame)));

// ---- runs ----
$("seedBtn").addEventListener("click", async () => {
  try {
    const r = await api("/experiments/seed-golden", { method: "POST" });
    state.experimentId = r.id;
    const label = $("expLabel");
    label.textContent = `${r.name} · ${r.id}`;
    label.classList.remove("hidden");
    $("runBtn").disabled = false;
  } catch (e) { alert("Seed failed: " + e.message); }
});

$("runBtn").addEventListener("click", async () => {
  if (!state.experimentId) return;
  $("runBtn").disabled = true;
  $("runBtn").textContent = "Running…";
  try {
    const body = JSON.stringify({
      experimentId: state.experimentId,
      harness: $("harness").value,
      iterations: Number($("iterations").value),
    });
    const started = await api("/runs", { method: "POST", body });
    state.lastRunId = started.runId;
    const result = await api(`/runs/${started.runId}/result`);
    renderResult(result);
    await renderLinks(started.runId);
    addRunRow(result);
  } catch (e) { alert("Run failed: " + e.message); }
  finally { $("runBtn").disabled = false; $("runBtn").textContent = "2 · Start run"; }
});

function renderResult(result) {
  $("result").classList.remove("hidden");
  const badge = $("decisionBadge");
  badge.textContent = result.status;
  badge.className = "badge " + result.status.replace(/\s+/g, "");
  const m = result.metrics;
  $("metrics").innerHTML = [
    ["Completed", m.completed],
    ["Validation", (m.validation_success_rate * 100).toFixed(1) + "%"],
    ["Terminal failures", (m.terminal_failure_rate * 100).toFixed(2) + "%"],
    ["Policy violations", m.policy_violations],
    ["P95 latency", m.p95_latency_ms + " ms"],
    ["Mean cost", "$" + m.mean_cost_usd.toFixed(4)],
  ].map(([k, v]) => `<div class="metric"><div class="v">${v}</div><div class="k">${k}</div></div>`).join("");

  const gates = (result.decision && result.decision.explanations) || [];
  $("scorecard").innerHTML =
    "<tr><th>Gate</th><th>Result</th></tr>" +
    gates.map((line) => {
      const sev = (line.match(/\[(.*?)\]/) || [])[1] || "";
      const pass = / PASS /.test(line);
      const text = line.replace(/\[.*?\]\s*/, "");
      return `<tr><td class="sev-${sev}">${sev}</td><td class="${pass ? "pass" : "fail"}">${text}</td></tr>`;
    }).join("");
}

async function renderLinks(runId) {
  try {
    const links = await api(`/observability/links?runId=${encodeURIComponent(runId)}`);
    $("grafanaLink").href = links.grafana;
    $("supersetLink").href = links.superset;
  } catch (_) { /* links are best-effort */ }
  $("exportLink").href = `${API}/runs/${runId}/result/export`;
}

function addRunRow(result) {
  const tb = $("runsTable").querySelector("tbody");
  const m = result.metrics;
  const tr = document.createElement("tr");
  tr.innerHTML =
    `<td>${result.runId}</td>` +
    `<td><span class="badge ${result.status.replace(/\s+/g, "")}" style="font-size:11px;padding:3px 10px">${result.status}</span></td>` +
    `<td>${m.policy_violations} violations</td><td>${(m.validation_success_rate * 100).toFixed(1)}% valid</td>`;
  tb.prepend(tr);
}

checkHealth();
