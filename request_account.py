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
    if len(sys.argv) != 2:
        logger.info("Usage: request_account.py <email>")
        sys.exit(1)
    weward = WeWard()
    email = sys.argv[1].strip()
    weward.request_signin_with_email(email)
    time.sleep(5)
    url = input('Put here the link in the weward mail : \n')
    custom_token = weward.parse_token_from_url(url)
    session_path = weward.signin(custom_token)
    weward.load_session(session_path)
    weward.complete_sponsorship_step()
    profile_data = weward.get_profile()
    logger.info(profile_data)
