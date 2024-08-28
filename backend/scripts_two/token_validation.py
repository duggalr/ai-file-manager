from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
import requests


def verify_access_token(access_token):
    userinfo_url = f'https://{os.environ['AUTH0_DOMAIN']}/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        user_info = response.json()
        return True, user_info
    except:
        return False, None
