import datetime
import email
import imaplib
import json
import logging
import os
import random
import re
import string
import sys
import time
from email.header import decode_header
from urllib import parse

import jwt
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
    datefmt="%d/%m %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class WeWard:
    def __init__(self):
        self.headers = {
            "Host": "backend.prod.weward.fr",
            "user-agent": "okhttp/4.9.1",
            "content-type": "application/json",
            "ww_device_country": "IT",
            "ww_user_language": "it",
        }

    def load_session(self, session_path):
        data = json.load(open(session_path))
        for k in data:
            setattr(self, k, data[k])

        self.headers.update({"authorization": self.authorization})
        self.challenge_level = 1

        self.user_data = None
        self.get_profile()
        self.load_challenges()

        self.strict_challenges = []
        self.already_visited = []
        self.last_steps = 0

    def logger_info(self, message):
        logger.info(
            f"{self.user_data['username']} ({self.user_data['email']}) - {message}"
        )

    def change_country(self, country):
        self.headers.update(
            {
                "ww_device_country": country.upper(),
                "ww_user_language": country.lower(),
            }
        )

    def request_signin_with_email(self, email):
        url = (
            "https://backend.prod.weward.fr/api/v1.0/customer/request_signin_with_email"
        )
        unique_device_id = "".join(random.sample(string.printable[:61], 16))
        logger.info(f"Unique device id: {unique_device_id}")
        self.headers.update({"ww-unique-device-id": unique_device_id})
        response = requests.post(url, headers=self.headers, json={"email": email})
        response = response.json()
        logger.info(response["message"])

    def signin_with_id_token(self, id_token):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/signin_with_id_token"
        response = requests.post(url, headers=self.headers, json={"id_token": id_token})
        response = response.json()
        logger.info(response["token"])

        devices = json.load(open("devices.json"))
        device = random.choice(devices)

        session = {
            "authorization": response["token"],
            "device_id": device["model"],
            "device_manufacturer": device["manufacturer"],
            "device_model": device["model"],
            "device_product": f"{device['manufacturer']}_{device['model'].replace(' ', '_')}",
            "device_system_name": "Android",
            "device_system_version": f"{random.randint(7, 11)}.0",
        }

        decoded = jwt.decode(id_token, options={"verify_signature": False})
        username = re.sub(r"@[^\s]+", " ", decoded["email"]).strip()

        session_path = os.path.join(os.getcwd(), "sessions", f"{username}.json")
        with open(session_path, "w") as f:
            f.write(json.dumps(session, indent=4))
        logger.info(f"Session {session_path} saved")
        return session_path

    def google_verify_custom_token(self, custom_token):
        headers = {
            "X-Android-Package": "com.weward",
            "Accept-Language": "en-US",
            "X-Client-Version": "Android/Fallback/X21000001/FirebaseCore-Android",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.0.0; WeWard - kolobovalada88 Build/OPR6.170623.017)",
            "Host": "www.googleapis.com",
        }

        params = (("key", "AIzaSyBpVnvwRMvz9lP9A2cVBKIIutli4ZuCmm4"),)

        json_data = {
            "token": custom_token,
            "returnSecureToken": True,
        }
        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken"
        response = requests.post(url, headers=headers, params=params, json=json_data)
        return response.json()

    def google_get_id_token(self, refresh_token):
        headers = {
            "X-Android-Package": "com.weward",
            "X-Android-Cert": "5D08264B44E0E53FBCCC70B4F016474CC6C5AB5C",
            "Accept-Language": "en-US",
            "X-Client-Version": "Android/Fallback/X21000001/FirebaseCore-Android",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.0.0; WeWard - kolobovalada88 Build/OPR6.170623.017)",
            "Host": "securetoken.googleapis.com",
        }

        params = (("key", "AIzaSyBpVnvwRMvz9lP9A2cVBKIIutli4ZuCmm4"),)

        json_data = {
            "grantType": "refresh_token",
            "refreshToken": refresh_token,
        }

        url = "https://securetoken.googleapis.com/v1/token"
        response = requests.post(url, headers=headers, params=params, json=json_data)
        return response.json()

    def signup(self, custom_token):
        response = self.google_verify_custom_token(custom_token)
        refresh_token = response["refreshToken"]
        response = self.google_get_id_token(refresh_token)
        try:
            id_token = response["id_token"]
        except:
            id_token = response["idToken"]
        return self.signin_with_id_token(id_token)

    def signin(self, custom_token):
        response = self.google_verify_custom_token(custom_token)
        id_token = response["idToken"]
        return self.signin_with_id_token(id_token)

    @staticmethod
    def get_url_from_email(username, password, host="imap.mail.ru", top_email=5):
        imap = imaplib.IMAP4_SSL(host)
        status, message = imap.login(username, password)
        logger.info(f"[Email Login] Status: {status}, Message: {message}")
        if status == "OK":
            status, message = imap.select("INBOX")
            logger.info(f"[Email Inbox] Status: {status}, Message: {message}")
            messages_count = int(message[0])
            for i in range(messages_count, messages_count - top_email, -1):
                time.sleep(0.2)
                res, msg = imap.fetch(str(i), "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        email_msg = (
                            email.message_from_bytes(response[1])
                            if sys.version_info[0] > 2
                            else email.message_from_string(response[1])
                        )
                        sender = email_msg.get("From")
                        subject = decode_header(email_msg["Subject"])[0][
                            0
                        ]  # email_msg.get("Subject")
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        if "weward" in f"{sender} {subject}".lower():
                            content_type = email_msg.get_content_type()
                            body = (
                                email_msg.get_payload(decode=True).decode()
                                if sys.version_info[0] > 2
                                else email_msg.get_payload(decode=True)
                            )
                            if content_type == "text/html":
                                soup = BeautifulSoup(body, features="html.parser")
                                anchor_tag = soup.findAll("a")
                                for href in anchor_tag:
                                    href = href.get("href")
                                    if href.startswith(
                                        "https://www.weward.app/signin_with_email"
                                    ):
                                        imap.close()
                                        imap.logout()
                                        return href

    @staticmethod
    def parse_token_from_url(url):
        args = dict(parse.parse_qsl(parse.urlsplit(url).query))
        return args["custom_token"]

    def save_consents(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/save_consents"
        response = requests.post(
            url,
            headers=self.headers,
            json={
                "cgu_consent": True,
                "rewards_consent": True,
                "ads_consent": True,
                "offers_consent": True,
            },
        )
        response = response.json()
        self.logger_info(response["message"])

    def update_step_source(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/update_step_source"
        requests.post(url, headers=self.headers, json={"step_source": "GoogleFit"})

    def upload_profile_informations(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/upload_profile_informations"
        gender = random.choice(["male", "female"])
        day = str(random.randint(1, 28)).zfill(2)
        month = str(random.randint(1, 12)).zfill(2)
        year = random.randint(1960, 2002)
        birth_date = f"{day}-{month}-{year}"
        response = requests.post(
            url, headers=self.headers, json={"gender": gender, "birth_date": birth_date}
        )
        response = response.json()
        self.logger_info(response["message"])

    def complete_sponsorship_step(self, sponsorship_code="ALEX-ugRUk"):
        url = (
            "https://backend.prod.weward.fr/api/v1.0/customer/complete_sponsorship_step"
        )
        requests.post(
            url, headers=self.headers, json={"sponsorship_code": sponsorship_code}
        )

    def get_profile(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/get_profile"
        response = requests.get(url, headers=self.headers)
        self.user_data = response = response.json()
        self.challenge_level = response["challenge_level"]
        self.logger_info(
            f"today_balance={response['today_balance']} ({response['today_balance'] * response['kward_to_eur']} Eur), balance={response['balance']} ({response['balance'] * response['kward_to_eur']} Eur), challenge_level={response['challenge_level']}"
        )
        return response

    def load_challenges(self, print_challenges=False):
        try:
            url = "https://backend.prod.weward.fr/api/v1.0/challenges_v2"
            response = requests.get(url, headers=self.headers)
            response = response.json()
            challenges = [c for c in response if c["level"] == self.challenge_level]
            missing = [c for c in challenges if c["completed"] is False]
            self.strict_challenges = [c["id"] for c in missing]
            self.logger_info(f"Challenge missing: {len(missing)}/{len(challenges)}")
            if print_challenges is True:
                for i in range(0, len(missing)):
                    self.logger_info(
                        f"{i+1}. Reward: {missing[i]['reward']}\t{missing[i]['title']}"
                    )
        except Exception as e:
            logger.exception(e)

    def location_campaign(self, latitude, longitude, per_page=50):
        try:
            params = (
                ("latitude", latitude),
                ("longitude", longitude),
                ("per_page", per_page),
            )

            url = "https://backend.prod.weward.fr/api/v1.0/location_campaign"
            response = requests.get(url, headers=self.headers, params=params)
            response = response.json()
            return response["campaigns"]
        except Exception as e:
            logger.exception(e)

    def reward_visit_campaign(self, latitude, longitude, campaign_id):
        try:
            url = (
                "https://backend.prod.weward.fr/api/v1.0/location/reward_visit_campaign"
            )
            payload = {
                "latitude": latitude,
                "longitude": longitude,
                "campaign_id": campaign_id,
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response = response.json()
            self.logger_info(response["message"])
        except Exception as e:
            logger.exception(e)

    def ads_reward_v2(self, retry=True):
        try:
            url = "https://backend.prod.weward.fr/api/v1.0/ads_reward_v2"
            response = requests.post(url, headers=self.headers)
            response = response.json()
            self.logger_info(response["message"])
            if response["time_remaining_sec"] > 0 and retry is True:
                self.logger_info(
                    f"Retry after {response['time_remaining_sec'] + 30} seconds"
                )
                time.sleep(response["time_remaining_sec"] + 30)
                self.ads_reward_v2()
        except Exception as e:
            logger.exception(e)

    def push_step_record(self, steps):
        now = datetime.datetime.now()
        boot = datetime.datetime(
            2022, now.month, now.day, random.randint(6, 7), random.randint(0, 59), 00
        )
        url = "https://backend.prod.weward.fr/api/v1.0/push_step_record"
        payload = {
            "amount": steps,
            "steps_needing_validation": None,
            "device_id": self.device_id,
            "device_manufacturer": self.device_manufacturer,
            "device_model": self.device_model,
            "device_product": self.device_product,
            "device_system_name": self.device_system_name,
            "device_system_version": self.device_system_version,
            "device_uptime_ms": str((now - boot).seconds * 1000),
            "googlefit_steps": steps,
            "steps_source": "googlefit",
            "data_sources": ["STEP_COUNTER"],
        }
        response = requests.post(url, headers=self.headers, json=payload)
        self.logger_info(f"steps={steps} {response.text}")

    def valid_step(self):
        url = "https://backend.prod.weward.fr/api/v1.0/valid_step"
        response = requests.post(url, headers=self.headers)
        response = response.json()
        self.logger_info(response["message"])
        self.last_steps = (
            response["valid_step"] if response["valid_step"] < 20000 else 0
        )

    def challenge_steps_intime(self, sleep):
        self.push_step_record(self.last_steps + random.randint(0, 500))
        self.valid_step()
        time.sleep(sleep)

    """
    5K_steps_half_hour              Convalida 5.000 passi in 30 minuti
    7K_steps_one_hour               Convalida 7.000 passi in 1 ora
    8K_steps_one_hour               Convalida 8.000 passi in 1 ora
    10K_steps_one_hour              Convalida 10.000 passi in 1 ora
    3K_step_between_6_8             Convalida 3.000 passi prima delle 7 del mattino
    10K_steps_before_12             Convalida di almeno 10.000 passi prima di mezzogiorno
    4K_steps_between_12_and_14      Convalida 4.000 passi tra le 12:00 e le 14:00
    """

    """
    06:00   job_number=0
    09:00   job_number=1
    10:15   job_number=2
    13:30   job_number=3
    15:00   job_number=4
    18:30   job_number=5
    23:00   job_number=6
    """

    def push_and_validate_step(self, job_number, steps=None):
        try:
            skip_sleep = False
            if steps is None:
                if job_number == 0:
                    steps = (
                        (3000 + random.randint(100, 500))
                        if "3K_step_between_6_8" in self.strict_challenges
                        else random.randint(250, 1000)
                    )
                elif job_number == 1:
                    steps = random.randint(1550, 2500)
                elif job_number == 2:
                    if "validate_steps_between_12_13" in self.strict_challenges:
                        time.sleep((60 * 60 * 2) + random.randint(0, 30))
                        skip_sleep = True

                    if "5K_steps_half_hour" in self.strict_challenges:
                        self.challenge_steps_intime(60 * 30)
                        steps = self.last_steps + 5000
                        skip_sleep = True
                    elif "7K_steps_one_hour" in self.strict_challenges:
                        self.challenge_steps_intime(60 * 60)
                        steps = self.last_steps + 7000
                        skip_sleep = True
                    elif "8K_steps_one_hour" in self.strict_challenges:
                        self.challenge_steps_intime(60 * 60)
                        steps = self.last_steps + 8000
                        skip_sleep = True
                    elif "10K_steps_before_12" in self.strict_challenges:
                        steps = random.randint(10453, 11567)
                    else:
                        steps = random.randint(3678, 5796)
                elif job_number == 3:
                    if "10K_steps_one_hour" in self.strict_challenges:
                        self.challenge_steps_intime(60 * 60)
                        steps = self.last_steps + 10000
                        skip_sleep = True
                    elif "4K_steps_between_12_and_14" in self.strict_challenges:
                        steps = 4000 + random.randint(100, 500)
                    else:
                        steps = random.randint(6346, 8564)
                elif job_number == 4:
                    steps = (
                        (10101 + random.randint(-9, 9))
                        if "10101_steps" in self.strict_challenges
                        else random.randint(10453, 14657)
                    )
                elif job_number == 5:
                    steps = (
                        (15151 + random.randint(-9, 9))
                        if "15151_steps" in self.strict_challenges
                        else random.randint(15345, 17456)
                    )
                elif job_number == 6:
                    if "45K_steps" in self.strict_challenges:
                        steps = random.randint(45000, 47000)
                    elif "30K_steps_one_day" in self.strict_challenges:
                        steps = random.randint(30000, 32000)
                    elif "15151_steps" in self.strict_challenges:
                        steps = 23456 + random.randint(-9, 9)
                    else:
                        steps = random.randint(20567, 23467)

            if steps > self.last_steps:
                if skip_sleep is False:
                    sleep = 60 * random.uniform(15, 45)
                    self.logger_info(
                        f"Job number: {job_number}, steps: {steps}. Sleep for {sleep // 60}m"
                    )
                    time.sleep(sleep)

                self.push_step_record(steps)
                self.valid_step()

                time.sleep(5)
                self.get_profile()
                self.load_challenges()
            else:
                self.logger_info(
                    f"We should convalidate: {steps}, but we have already convalidate: {self.last_steps}"
                )
        except Exception as e:
            logger.exception(e)

    # For the truth, skip_night It is useless, as we often watch videos even at night
    def random_location_campaign(self, latitude, longitude, skip_night=True):
        morning = datetime.datetime.now().replace(hour=8, minute=00)
        evening = datetime.datetime.now().replace(hour=21, minute=00)
        if (
            datetime.datetime.now() >= morning
            and datetime.datetime.now() <= evening
            or skip_night is False
        ):
            campaigns = self.location_campaign(latitude, longitude)
            campaigns = [
                c
                for c in campaigns
                if c["id"] not in self.already_visited and c["reward"] > 0
            ]
            if campaigns != []:
                """
                for i in range(0, len(campaigns)):
                    self.logger_info(f"{i+1}. Reward: {campaigns[i]['reward']}\t{campaigns[i]['title']} ({campaigns[i]['address']})")
                """
                selected = random.choice(campaigns)
                self.logger_info(
                    f"Reward: {selected['reward']}\t{selected['title']} ({selected['address']})"
                )
                campaign_latitude = selected["location_config"]["latitude"] + (
                    random.randint(-5000, 5000) / 100000000000
                )
                campaign_longitude = selected["location_config"]["longitude"] + (
                    random.randint(-5000, 5000) / 100000000000
                )
                self.reward_visit_campaign(
                    campaign_latitude, campaign_longitude, selected["id"]
                )
                self.already_visited.append(selected["id"])
            else:
                self.logger_info(
                    f"0 Campaigns left with this coordinate ({latitude}, {longitude})"
                )
        else:
            self.logger_info("Probably we should sleep at this time")
