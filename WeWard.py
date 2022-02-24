import requests
import json
import os
import sys
import random
import datetime
import time
import logging
import imaplib
import email
import jwt
import re
import string

from urllib import parse
from email.header import decode_header
from bs4 import BeautifulSoup

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
    datefmt="%d/%m %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

class WeWard:
    headers = {
        "Host": "backend.prod.weward.fr",
        "user-agent": "okhttp/4.9.1",
        "content-type": "application/json",

        'ww_device_country': 'IT',
        'ww_user_language': 'it',
    }

    def __init__(self, session_path):
        data = json.load(open(session_path))
        for k in data:
            setattr(self, k, data[k])

        session_name = session_path.split("/")[-1].strip(".json")

        self.headers.update({"authorization": self.authorization})
        self.challenge_level = 1

        self.get_profile()
        time.sleep(5)
        self.print_missing_challenge()

        self.strict_challenges = []
        self.last_steps = 0

    def update_request_timestamp(self):
        self.headers.update({ "ww_device_ts": str(int(time.time())) })

    @classmethod
    def request_signin_with_email(cls, email):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/request_signin_with_email"
        cls.update_request_timestamp(cls)
        unique_device_id = "".join(random.sample(string.printable[:61], 16))
        logger.info(f"Unique device id: {unique_device_id}")
        cls.headers.update({"ww-unique-device-id": unique_device_id})
        response = requests.post(url, headers=cls.headers, json={"email": email})
        response = response.json()
        logger.info(response["message"])

    @classmethod
    def signin_with_id_token(cls, id_token):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/signin_with_id_token"
        cls.update_request_timestamp(cls)
        response = requests.post(url, headers=cls.headers, json={"id_token": id_token})
        response = response.json()
        logger.info(response["token"])

        devices = json.load(open("devices.json"))
        device = random.choice(devices)

        session = {
            "authorization": response["token"],
            "device_id": device['model'],
            "device_manufacturer": device['manufacturer'],
            "device_model": device['model'],
            "device_product": f"{device['manufacturer']}_{device['model'].replace(' ', '_')}",
            "device_system_name": "Android",
            "device_system_version": f"{random.randint(7, 11)}.0",
        }

        decoded = jwt.decode(id_token, options={"verify_signature": False})
        username = re.sub("@[^\s]+", " ", decoded['email']).strip()

        session_path = os.path.join(os.getcwd(), "sessions", f"{username}.json")
        with open(session_path, "w") as f:
            f.write(json.dumps(session, indent=4))
        logger.info(f"Session {session_path} saved")
        return session_path

    @classmethod
    def google_verify_custom_token(cls, custom_token):
        headers = {
            'X-Android-Package': 'com.weward',
            'Accept-Language': 'en-US',
            'X-Client-Version': 'Android/Fallback/X21000001/FirebaseCore-Android',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; WeWard - kolobovalada88 Build/OPR6.170623.017)',
            'Host': 'www.googleapis.com',
        }

        params = (
            ('key', 'AIzaSyBpVnvwRMvz9lP9A2cVBKIIutli4ZuCmm4'),
        )

        json_data = {
            'token': custom_token,
            'returnSecureToken': True,
        }
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken'
        response = requests.post(url, headers=headers, params=params, json=json_data)
        return response.json()

    @classmethod
    def google_get_id_token(cls, refresh_token):
        headers = {
            'X-Android-Package': 'com.weward',
            'X-Android-Cert': '5D08264B44E0E53FBCCC70B4F016474CC6C5AB5C',
            'Accept-Language': 'en-US',
            'X-Client-Version': 'Android/Fallback/X21000001/FirebaseCore-Android',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; WeWard - kolobovalada88 Build/OPR6.170623.017)',
            'Host': 'securetoken.googleapis.com',
        }

        params = (
            ('key', 'AIzaSyBpVnvwRMvz9lP9A2cVBKIIutli4ZuCmm4'),
        )

        json_data = {
            'grantType': 'refresh_token',
            'refreshToken': refresh_token,
        }

        url = 'https://securetoken.googleapis.com/v1/token'
        response = requests.post(url, headers=headers, params=params, json=json_data)
        return response.json()

    @classmethod
    def signup(cls, custom_token):
        response = cls.google_verify_custom_token(custom_token)
        refresh_token = response["refreshToken"]
        response = cls.google_get_id_token(refresh_token)
        id_token = response["id_token"]
        return cls.signin_with_id_token(id_token)

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
                        email_msg = email.message_from_bytes(response[1]) if sys.version_info[0] > 2 else email.message_from_string(response[1])
                        sender = email_msg.get("From")
                        subject = decode_header(email_msg["Subject"])[0][0]  # email_msg.get("Subject")
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        if "weward" in f"{sender} {subject}".lower():
                            content_type = email_msg.get_content_type()
                            body = email_msg.get_payload(decode=True).decode() if sys.version_info[0] > 2 else email_msg.get_payload(decode=True)
                            if content_type == "text/html":
                                soup = BeautifulSoup(body, features="html.parser")
                                anchor_tag = soup.findAll("a")
                                for href in anchor_tag:
                                    href = href.get("href")
                                    if href.startswith("https://www.weward.app/signin_with_email"):
                                        imap.close()
                                        imap.logout()
                                        return href

    @staticmethod
    def parse_token_from_url(url):
        args = dict(parse.parse_qsl(parse.urlsplit(url).query))
        return args["custom_token"]

    def save_consents(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/save_consents"
        self.update_request_timestamp()
        response = requests.post(url, headers=self.headers, json={"cgu_consent": True, "rewards_consent": True, "ads_consent": True, "offers_consent": True})
        response = response.json()
        logger.info(response["message"])

    def update_step_source(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/update_step_source"
        self.update_request_timestamp()
        response = requests.post(url, headers=self.headers, json={"step_source": "GoogleFit"})

    def upload_profile_informations(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/upload_profile_informations"
        gender = random.choice(["male", "female"])
        day = str(random.randint(1, 28)).zfill(2)
        month = str(random.randint(1, 12)).zfill(2)
        year = random.randint(1960, 2002)
        birth_date = f"{day}-{month}-{year}"
        self.update_request_timestamp()
        response = requests.post(url, headers=self.headers, json={
            "gender": gender,
            "birth_date": birth_date
        })
        response = response.json()
        logger.info(response["message"])

    def complete_sponsorship_step(self, sponsorship_code="ALEX-ugRUk"):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/complete_sponsorship_step"
        self.update_request_timestamp()
        response = requests.post(url, headers=self.headers, json={"sponsorship_code": sponsorship_code})

    def get_profile(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/get_profile"
        self.update_request_timestamp()
        response = requests.get(url, headers=self.headers)
        response = response.json()
        logger.info(
            f"{response['username']} ({response['email']}), today_balance={response['today_balance']} ({response['today_balance'] * response['kward_to_eur']} Eur), balance={response['balance']} ({response['balance'] * response['kward_to_eur']} Eur), challenge_level={response['challenge_level']}"
        )
        self.challenge_level = response["challenge_level"]
        return response

    def print_missing_challenge(self):
        try:
            url = "https://backend.prod.weward.fr/api/v1.0/challenges_v2"
            self.update_request_timestamp()
            response = requests.get(url, headers=self.headers)
            response = response.json()
            challenges = [c for c in response if c["level"] == self.challenge_level]
            missing = [c for c in challenges if c["completed"] is False]
            self.strict_challenges = [c['id'] for c in missing]
            logger.info(f"Challenge missing: {len(missing)}/{len(challenges)}")
            for i in range(0, len(missing)):
                logger.info(
                    f"{i+1}. Reward: {missing[i]['reward']}\t{missing[i]['title']}"
                )
        except Exception as e:
            logger.exception(e)

    def ads_reward_v2(self):
        try:
            time.sleep(60 * random.randint(1, 5))
            url = "https://backend.prod.weward.fr/api/v1.0/ads_reward_v2"
            self.update_request_timestamp()
            response = requests.post(url, headers=self.headers)
            response = response.json()
            logger.info(response["message"])
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
        self.update_request_timestamp()
        response = requests.post(url, headers=self.headers, json=payload)
        logger.info(response.text)

    def valid_step(self):
        url = "https://backend.prod.weward.fr/api/v1.0/valid_step"
        self.update_request_timestamp()
        response = requests.post(url, headers=self.headers)
        response = response.json()
        logger.info(response["message"])
        self.last_steps = response['valid_step'] if response['valid_step'] < 20000 else 0

    def challenge_steps_intime(self, sleep):
        self.push_step_record(self.last_steps + random.randint(0, 500))
        self.valid_step()
        time.sleep(sleep)

    """
    "id":"5K_steps_half_hour", "title":"Convalida 5.000 passi in 30 minuti",
    "id":"7K_steps_one_hour", "title":"Convalida 7.000 passi in 1 ora",
    "id":"8K_steps_one_hour", "title":"Convalida 8.000 passi in 1 ora",
    "id":"10K_steps_one_hour", "title":"Convalida 10.000 passi in 1 ora",
    "id":"3K_step_between_6_8", "title":"Convalida 3.000 passi prima delle 7 del mattino",
    "id":"10K_steps_before_12", "title":"Convalida di almeno 10.000 passi prima di mezzogiorno",
    "id":"4K_steps_between_12_and_14", "title":"Convalida 4.000 passi tra le 12:00 e le 14:00",
    """
    def push_and_validate_step(self, job_number, steps=None):
        try:
            skip_sleep = False
            if steps is None:
                if job_number == 0:
                    steps = (3000 + random.randint(100, 500)) if "3K_step_between_6_8" in self.strict_challenges else random.randint(250, 1000)
                elif job_number == 1:
                    steps = random.randint(1550, 2500)
                elif job_number == 2:
                    if "validate_steps_between_12_13" in self.strict_challenges:
                        time.sleep((60 * 2) + random.randint(0, 30))
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
                    steps = (10101 + random.randint(-9, 9)) if "10101_steps" in self.strict_challenges else random.randint(10453, 14657)
                elif job_number == 5:
                    steps = (15151 + random.randint(-9, 9)) if "15151_steps" in self.strict_challenges else random.randint(15345, 17456)
                elif job_number == 6:
                    if "45K_steps" in self.strict_challenges:
                        steps = random.randint(45000, 47000)
                    elif "30K_steps_one_day" in self.strict_challenges:
                        steps = random.randint(30000, 32000)
                    elif "15151_steps" in self.strict_challenges:
                        steps = (23456 + random.randint(-9, 9))
                    else:
                        steps = random.randint(20567, 23467)

            if steps > self.last_steps:
                if skip_sleep is False:
                    sleep = 60 * random.uniform(15, 45)
                    logger.info(
                        f"Job number: {job_number}, steps: {steps}. Sleep for {sleep // 60}m"
                    )
                    time.sleep(sleep)

                self.push_step_record(steps)
                self.valid_step()

                time.sleep(5)
                self.get_profile()

                time.sleep(5)
                self.print_missing_challenge()
            else:
                logger.info(f"We should convalidate: {steps}, but we have already convalidate: {self.last_steps}")
        except Exception as e:
            logger.exception(e)