# gke-agent-sandbox

Demo code from the talk **"Unveiling Security Benefit from GKE Agent Sandbox,
Using Agentic AI vibe coding with Gemini and Antigravity"** by
**Muhammad Ghiyast Farisi** — Google Developer Group Indonesia, 1 August 2026.

Run the steps in order; each directory has its own README.

| Step | What |
|---|---|
| [`01_setup_cluster`](01_setup_cluster) | GKE Autopilot cluster with Agent Sandbox enabled |
| [`02_setup_sandbox_crd`](02_setup_sandbox_crd) | `SandboxTemplate` + `SandboxWarmPool` |
| [`03_setup_sandbox_router`](03_setup_sandbox_router) | Sandbox router Service + Deployment |
| [`04_run_pysandbox`](04_run_pysandbox) | Run code in a gVisor sandbox from Python |
| [`05_run_withadk`](05_run_withadk) | ADK agent writing code that runs in the sandbox |
