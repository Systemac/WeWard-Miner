import logging
import os
import random
import sys
import time

import schedule

from WeWard import WeWard

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
    datefmt="%d/%m %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.info("Usage: farm_points.py <jsonfile.json>")
        sys.exit(1)

    fpath = sys.argv[1]
    if fpath is not None and fpath.endswith(".json") and os.path.isfile(fpath):
        weward = WeWard()
        weward.load_session(fpath)

        schedule.every().hour.do(weward.ads_reward_v2)

        coordinates = [
            (41.90013975494311, 12.495371125919968),  # Roma
            (45.05355303045114, 7.6724869090132115),  # Torino
            (45.450640850469924, 9.163952126305784),  # Milano
            (43.75640335265113, 11.242131092957662),  # Firenze
            (40.87303484439868, 14.279195399113881),  # Napoli
        ]
        coordinate = random.choice(coordinates)
        schedule.every(12).to(48).hours.do(
            weward.random_location_campaign,
            latitude=coordinate[0],
            longitude=coordinate[1],
        )

        jobs = ["06:00", "09:00", "10:15", "13:30", "15:00", "18:30", "23:00"]
        for job_number in range(0, len(jobs)):
            schedule.every().day.at(jobs[job_number]).do(
                weward.push_and_validate_step, job_number=job_number
            )

        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        logger.error(f"Please review your .json file (2th arg): {fpath}")
