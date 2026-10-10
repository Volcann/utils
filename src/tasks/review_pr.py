import io
import sys

from app import app


@app.task(bind=True, name="tools.review_pr")
def review_pr_task(self, pr_number: int) -> str:
    self.update_state(state="PROGRESS", meta={"msg": f"Reviewing PR #{pr_number}..."})
    from pr_reviewer.reviewer import run_review

    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        run_review(pr_number)
        return buf.getvalue() or f"✅ PR #{pr_number} reviewed."
    finally:
        sys.stdout = old_stdout
