from celery import Celery

BROKER = "redis://127.0.0.1:6382/0"
app = Celery(
    "tools_manager",
    broker=BROKER,
    backend=BROKER,
    include=[
        "tasks.list_tools",
        "tasks.setup_project",
        "tasks.review_pr",
        "tasks.report_status",
    ],
)
