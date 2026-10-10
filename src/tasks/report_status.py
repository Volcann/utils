import io
import sys
from app import app


@app.task(bind=True, name="tools.report_status")
def report_status_task(self, date: str = None) -> str:
    self.update_state(state="PROGRESS", meta={"msg": "Generating status report..."})
    from cli.commands import main as status_main

    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        args = [date] if date else []
        try:
            status_main(args)
        except SystemExit:
            pass
        return buf.getvalue() or "✅ Status report generated."
    finally:
        sys.stdout = old_stdout
