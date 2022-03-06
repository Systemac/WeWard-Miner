import os
import queue
import random
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

    coordinates = [
        (41.90013975494311, 12.495371125919968),  # Roma
        (45.05355303045114, 7.6724869090132115),  # Torino
        (45.450640850469924, 9.163952126305784),  # Milano
        (43.75640335265113, 11.242131092957662),  # Firenze
        (40.87303484439868, 14.279195399113881),  # Napoli
    ]
    jobs = ["06:00", "09:00", "10:15", "13:30", "15:30", "18:30", "23:00"]
    for i in range(len(sessions)):
        schedule.every().hour.do(jobqueue.put, sessions[i].ads_reward_v2)

        coordinate = random.choice(coordinates)
        f = partial(
            sessions[i].random_location_campaign,
            latitude=coordinate[0],
            longitude=coordinate[1],
        )
        schedule.every(12).to(48).hours.do(jobqueue.put, f)

        for job_number in range(0, len(jobs)):
            f = partial(sessions[i].push_and_validate_step, job_number=job_number)
            schedule.every().day.at(jobs[job_number]).do(jobqueue.put, f)

    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()

    while 1:
        schedule.run_pending()
        time.sleep(1)
