


from dotenv import load_dotenv
from fastapi import HTTPException
from jose import JWTError
load_dotenv()
import os
import requests


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_OAUTH2_URL = "https://oauth2.googleapis.com/tokeninfo?id_token="

def verify_google_token(token: str):
    try:
        # Try verifying as ID Token first
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
        
        # If that fails (e.g. 400), try as Access Token
        if response.status_code != 200:
             response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={token}")

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google Token")
        
        token_info = response.json()

        # Check if the token was issued to your app's client
        # For ID tokens, client ID is in 'aud'
        # For Access tokens, client ID is in 'aud' or 'azp'
        aud = token_info.get("aud")
        azp = token_info.get("azp")
        
        if aud != GOOGLE_CLIENT_ID and azp != GOOGLE_CLIENT_ID:
             # Double check logic: sometimes aud is an array?
             # But usually for these tokens it's a string.
             # If strictly checking:
             if str(aud) != str(GOOGLE_CLIENT_ID) and str(azp) != str(GOOGLE_CLIENT_ID):
                raise HTTPException(status_code=400, detail="Token not issued for this app!")
        
        if not token_info.get("email_verified") == "true" and not token_info.get("email_verified") is True:
             # Google returns boolean true for id_token, string "true" for access_token sometimes? 
             # Let's be safe.
             raise HTTPException(status_code=400, detail="Email is not verified!")

        return token_info

    except JWTError as e:
        raise HTTPException(status_code=400, detail="Token verification failed")