import logging
import sys
import time

from WeWard import WeWard

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
    datefmt="%d/%m %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: farm_accounts.py <email> <password>")
        sys.exit(1)

    weward = WeWard()
    email = sys.argv[1].strip()
    password = sys.argv[2].strip()

    weward.request_signin_with_email(email)
    time.sleep(5)

    url = weward.get_url_from_email(email, password)
    while url is None:
        time.sleep(15)
        url = weward.get_url_from_email(email, password)

    custom_token = weward.parse_token_from_url(url)

    session_path = weward.signup(custom_token)

    weward.load_session(session_path)

    weward.save_consents()
    weward.update_step_source()
    weward.upload_profile_informations()

    weward.complete_sponsorship_step()

    profile_data = weward.get_profile()
    logger.info(profile_data)
