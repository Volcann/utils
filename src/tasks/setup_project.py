import io
import sys
from app import app
from environment.folder_setup import launch_workspace
from environment.listener import start_listeners


@app.task(bind=True, name="tools.setup_project")
def setup_project_task(self, project_name: str) -> str:
    self.update_state(
        state="PROGRESS", meta={"msg": f"Launching workspace {project_name}..."}
    )

    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        start_listeners()
        launch_workspace(project_name)
        return buf.getvalue() or f"✅ Workspace '{project_name}' setup."
    finally:
        sys.stdout = old_stdout
