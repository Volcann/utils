# Developer Tools Manager (Utils)

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tooling: uv](https://img.shields.io/badge/tooling-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Task Queue: Celery](https://img.shields.io/badge/task%20queue-celery-green.svg)](https://docs.celeryq.dev/)

**Centralized monorepo and async task manager for automated developer utilities.**
_One workspace. Unified dependencies, shared toolkits, and Celery-powered task distribution._

[Quick Start](#-quickstart--installation) · [The Problem](#-the-problem) · [What It Does](#-what-it-does) · [Included Tools](#-included-tools) · [Architecture](#-repository-structure)

---

## 🛑 The Problem

Modern engineering teams rely on a variety of CLI tools and automated scripts to speed up their workflow — from generating daily status reports to automating PR reviews or provisioning local environments.

When these tools are spread across multiple repositories, maintaining them becomes a burden:
- **Dependency Hell**: Managing separate virtual environments, `pip` installations, and conflicting dependencies across different directories.
- **Scattered Execution**: Running commands manually from different folders instead of triggering them centrally.
- **Duplicated Logic**: Every tool re-implementing its own GitHub API client, configuration loader, or CLI parser.
- **No Orchestration**: Difficult to trigger these tools programmatically or run them asynchronously in the background.

## 💡 What It Does

This `utils` project acts as a **unified workspace and task orchestrator** for a suite of developer productivity tools. 

Powered by `uv` workspaces for blazing-fast dependency management and `Celery` for async execution, it groups standalone CLI utilities into a single, cohesive ecosystem.

- Unifies dependencies across `lazy-reviewer`, `workedTask`, and `environment` using a single `pyproject.toml`.
- Provides a centralized `ghToolkit` library, sharing high-performance GitHub interactions across all tools.
- Wraps standalone tools into asynchronous Celery tasks (`setup_project`, `review_pr`, `report_status`) so they can be triggered programmatically.
- Exposes a unified `Makefile` for setting up environments, syncing dependencies, and starting integrated services.

---

## 🛠 Included Tools

The monorepo contains the following workspace members:

### 1. [ghToolkit](./ghToolkit/)
A high-performance, zero-dependency Python facade over the GitHub CLI (`gh`) and Git. Replaces duplicated API integrations across all tools with sub-second local Git fast paths and robust exception handling.

### 2. [workedTask (status-reporter)](./workedTask/)
An automated daily engineering status reporter. Queries GitHub for commits, PRs, and reviews across repositories and uses Gemini AI to compile a clean, formatted daily status report. 

### 3. [lazy-reviewer (pr-reviewer)](./lazy-reviewer/)
An automated AI code review tool. Pulls down PR diffs and posts structured, inline code review suggestions directly to GitHub.

### 4. [environment](./environment/)
Developer workspace provisioning and listener utility. Automatically maps configurations, sets up project workspaces, and launches system listeners.

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.11+
- `uv` package manager
- Redis (for Celery broker, running on `127.0.0.1:6382/0`)

### Setup

```bash
# Navigate to the repository
cd utils

# Sync all workspace packages and dependencies using uv
make setup
```

### Starting the Services

To boot up the main application wrapper and associated services (e.g., `volcanai` Django backend):

```bash
make start
```
This script binds cleanup traps to gracefully shut down background processes when exited.

---

## 💻 CLI Usage (Makefile)

The unified `Makefile` provides quick access to workspace operations:

```bash
# Sync dependencies across the entire monorepo
make setup

# Start the main application wrapper
make start

# Setup a specific project folder via the 'environment' tool
make folder_setup PROJECT=1x2

# Run curl setup via the 'environment' tool
make curl_setup PROJECT=1x2

# Run ruff linting across lazy-reviewer and workedTask
make lint

# Display available commands
make help
```

---

## 🔄 Celery Task Architecture

The root directory acts as an async task broker for the included tools. Tasks are defined in `src/tasks/` and registered with the `tools_manager` Celery app.

### Available Tasks (`src/tasks/`)
- `tools.list_tools`: Returns the schema and descriptions of all available tasks.
- `tools.setup_project`: Triggers `environment.folder_setup.launch_workspace` to scaffold a project.
- `tools.review_pr`: Triggers `pr_reviewer.reviewer.run_review` to execute an AI code review on a PR.
- `tools.report_status`: Triggers `status_reporter.cli.commands.main` to generate a daily status report.

All tasks capture standard output (`sys.stdout`) natively and report progression state seamlessly back to the Celery broker.

---

## 📁 Repository Structure

```text
utils/
├── pyproject.toml             # uv workspace definition and core dependencies
├── Makefile                   # Unified orchestration commands
├── start.sh                   # Startup script for attached services
├── src/
│   ├── app.py                 # Celery app initialization (tools_manager)
│   └── tasks/                 # Celery task definitions
│       ├── list_tools.py      # Task registry discovery
│       ├── report_status.py   # Wrapper for workedTask/status-reporter
│       ├── review_pr.py       # Wrapper for lazy-reviewer
│       └── setup_project.py   # Wrapper for environment setup
├── ghToolkit/                 # Core GitHub CLI wrapper library
├── workedTask/                # Automated daily status reporting CLI
├── lazy-reviewer/             # Automated AI PR reviewer
└── environment/               # System and workspace configuration tool
```

---

## 💡 The Idea in One Sentence

> **This project transforms scattered, standalone developer utilities into a unified, high-performance ecosystem backed by a single package manager and an asynchronous task queue.**

---

## 📜 License

MIT. Built for engineering teams that want fast, safe, and unified automation across all their tools and agents.