from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
import requests


# def verify_access_token(access_token):
#     userinfo_url = f'https://{os.environ['AUTH0_DOMAIN']}/userinfo'
#     headers = {'Authorization': f'Bearer {access_token}'}
#     response = requests.get(userinfo_url, headers=headers)
#     response.raise_for_status()
#     print(response)
#     # try:
#     #     response = requests.get(userinfo_url, headers=headers)
#     #     response.raise_for_status()
#     #     user_info = response.json()
#     #     return True, user_info
#     # except:
#     #     return False, None


import jwt
from jwt import PyJWKClient
from django.http import JsonResponse
import os

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_AUDIENCE = os.environ['API_IDENTIFIER']


def verify_access_token(access_token):
    try:
        jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(
            access_token
        )
        # print(signing_key)
        decoded_token = jwt.decode(
            access_token,
            signing_key.key,
            algorithms = ["RS256"],
            audience = AUTH0_AUDIENCE,
            issuer = f'https://{AUTH0_DOMAIN}/'
        )
        return True, decoded_token
    except:
        return False, {'message': 'Invalid token'}


def get_user_profile(access_token):
    userinfo_url = f'https://{AUTH0_DOMAIN}/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        user_info = response.json()
        return True, user_info
    except:
        return False, None

