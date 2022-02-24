import sys
import time
import logging

from WeWard import WeWard

if __name__ == '__main__':
    if len(sys.argv) != 3:
        logger.info("Usage: farm_accounts.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1].strip()
    password = sys.argv[2].strip()

    WeWard.request_signin_with_email(email)
    time.sleep(5)

    url = WeWard.get_url_from_email(email, password)
    while url is None:
        time.sleep(15)
        url = WeWard.get_url_from_email(email, password)

    custom_token = WeWard.parse_token_from_url(url)

    session_path = WeWard.signup(custom_token)

    weward = WeWard(session_path)

    weward.save_consents()
    weward.update_step_source()
    weward.upload_profile_informations()

    weward.complete_sponsorship_step()

    profile_data = weward.get_profile()
    print(profile_data)