import firebase_admin
from firebase_admin import credentials, db
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import sys
import json

cred = credentials.Certificate("/Users/dev/Desktop/mini-f8aad-firebase-adminsdk-r6nm9-037189ee66.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mini-f8aad-default-rtdb.firebaseio.com/'  # Replace with your Realtime Database URL
})

CLIENT_SECRETS_FILE_TRIEU = "/Users/dev/Desktop/trieu.json"
CLIENT_SECRETS_FILE_BEN = "/Users/dev/Desktop/ben.json"

ALLOWED_USERS = ['trieut415@gmail.com', 'bhsu25@bu.edu']

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

def get_user_credentials(client_secrets_file):
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def verify_user_token(creds):
    token = creds.token
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)

    if response.status_code != 200:
        print(
            f"Failed to fetch user info: {response.status_code}, {response.text}")
        sys.exit(1)

    user_info = response.json()

    user_email = user_info.get('email')
    print(f"User signed in with email: {user_email}")

    if user_email not in ALLOWED_USERS:
        print(
            f"Access denied for {user_email}. This account is not authorized to use this application.")
        sys.exit(1) 

    return user_email

def get_user_data(user_email):
    ref = db.reference(f"users/{user_email.replace('.', ',')}")
    user_data = ref.get()
    if user_data:
        print(f"User Data for {user_email}: {user_data}")
    else:
        print(f"No data found for {user_email}")

def print_all_data():
    ref = db.reference('/')
    all_data = ref.get()
    if all_data:
        print("All data in Realtime Database:")
        print(all_data)
    else:
        print("The Realtime Database is empty.")

def upload_email_to_db(user_email):
    ref = db.reference('email')    
    ref.set(user_email)
    print(f"Uploaded {user_email} to the database as the value for 'email'.")

def parse_and_display_scores(user_email):
    ref = db.reference('/')
    all_data = ref.get()

    if isinstance(all_data, dict):
        for key, value in all_data.items():
            if key.startswith("score") and isinstance(value, dict):
                for inner_key, score_entry in value.items():
                    if isinstance(score_entry, dict) and score_entry.get('email') == user_email:
                        print(f"Score data for {user_email}:")
                        print(json.dumps(score_entry))
                        return
        print(f"No scores found for {user_email}")
    else:
        print("No scores data found or data is not in the expected format.")

def main():
    print("Sign in as Trieu")
    creds_trieu = get_user_credentials(CLIENT_SECRETS_FILE_TRIEU)
    trieu_email = verify_user_token(creds_trieu)
    get_user_data(trieu_email)
    print_all_data()
    upload_email_to_db(trieu_email)
    parse_and_display_scores(trieu_email)

if __name__ == "__main__":
    main()
