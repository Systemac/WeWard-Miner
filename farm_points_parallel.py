import os
import queue
import threading
import time
from functools import partial

import schedule

from WeWard import WeWard

if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "sessions")
    sessions_files = [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".json")
    ]
    sessions = []
    for fname in sessions_files:
        sessions.append(WeWard())
        sessions[-1].load_session(os.path.join(path, fname))

    jobqueue = queue.Queue()

    # https://schedule.readthedocs.io/en/stable/parallel-execution.html
    def worker_main():
        while 1:
            job_func = jobqueue.get()
            threading.Thread(target=job_func).start()
            jobqueue.task_done()

    jobs = ["06:00", "09:00", "10:15", "13:30", "15:30", "18:30", "23:00"]
    functions = []
    for i in range(len(sessions)):
        schedule.every().hour.do(jobqueue.put, sessions[i].ads_reward_v2)

        for job_number in range(0, len(jobs)):
            functions.append(
                partial(sessions[i].push_and_validate_step, job_number=job_number)
            )
            schedule.every().day.at(jobs[job_number]).do(jobqueue.put, functions[-1])

    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()

    while 1:
        schedule.run_pending()
        time.sleep(1)
