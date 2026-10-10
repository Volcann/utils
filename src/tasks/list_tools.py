from app import app


@app.task(name="tools.list_tools")
def list_tools_task() -> list[dict]:
    return [
        {
            "name": "setup_project",
            "description": "Setup and launch a project workspace by project name.",
            "inputSchema": {
                "type": "object",
                "properties": {"project_name": {"type": "string"}},
                "required": ["project_name"],
            },
        },
        {
            "name": "review_pr",
            "description": "Review a GitHub Pull Request using the lazy-reviewer tool.",
            "inputSchema": {
                "type": "object",
                "properties": {"pr_number": {"type": "integer"}},
                "required": ["pr_number"],
            },
        },
        {
            "name": "report_status",
            "description": "Generate a daily status report (workedTask).",
            "inputSchema": {
                "type": "object",
                "properties": {"date": {"type": "string", "description": "YYYY-MM-DD"}},
                "required": [],
            },
        },
    ]
