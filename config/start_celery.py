import os
import subprocess

def start_worker():
    if os.environ.get("CELERY_STARTED"):
        return

    os.environ["CELERY_STARTED"] = "1"

    subprocess.Popen(
        [
            "celery",
            "-A",
            "config",
            "worker",
            "--loglevel=info",
            "--concurrency=2",
        ]
    )
