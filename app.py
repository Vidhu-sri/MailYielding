import os
import requests
from dotenv import load_dotenv
import subprocess
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


chat_id = os.getenv("CHAT_ID")
auth_token = os.getenv("AUTH_TOKEN")
userId  =  'vsrivarenya@gmail.com'

def setup_cred():
    # subprocess.run(["python", 'quickstart.py'])

    with open('token.json', 'r') as auth:
        data = json.load(auth)
    return data['token']


YOUR_ACCESS_TOKEN = setup_cred()
credentials = Credentials(YOUR_ACCESS_TOKEN)
service = build('gmail', 'v1', credentials)
sender_email = 'technews-editor@acm.org'


def send_telegram_notification(message):
    max_size = 4096
    parts = [message[i:i+max_size] for i in range(0,len(message),max_size)]
    url = f'https://api.telegram.org/bot{auth_token}/sendMessage'   

    for part in parts:
        payload = {
            'chat_id': chat_id,
            'text': part,
            'parse_mode': 'html' 
        }

        requests.post(url, json=payload)
    


# message = "Hello from Python!"
# send_telegram_notification(message)

def get_msg_ids():
    query = f"from:{sender_email} to:{userId}"
    results = service.users().messages().list(userId = userId, q = query).execute()

    if results['messages']:
        message_ids = [message['id'] for message in results['messages']]
        return message_ids
    else:
        print('no messages from this email')


def retrieve_gmail_message(message):
    payload = message['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    
def main():

    message_ids = get_msg_ids()
    msg = service.users().messages().get(userId=userId, id = message_ids[0], format='full').execute()
    message_body = retrieve_gmail_message(msg)
    send_telegram_notification(message_body)




if __name__ == '__main__':
    main()

