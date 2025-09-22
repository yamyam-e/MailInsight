from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def _load_creds(cred_path="/secrets/credentials.json", token_path="/secrets/token.json"):
    if not os.path.exists(token_path):
        raise FileNotFoundError("token.json not found in /secrets (run bootstrap on host)")
    return Credentials.from_authorized_user_file(token_path, SCOPES)

def gmail_search(query: str, max_results: int = 10) -> List[Dict]:
    creds = _load_creds()
    service = build('gmail', 'v1', credentials=creds)
    res = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = res.get('messages', [])
    out: List[Dict] = []
    for m in messages or []:
        msg = service.users().messages().get(userId='me', id=m['id']).execute()
        headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
        out.append({
            "id": m['id'],
            "date": headers.get("Date",""),
            "from": headers.get("From",""),
            "to": headers.get("To",""),
            "subject": headers.get("Subject",""),
            "snippet": msg.get("snippet",""),
        })
    return out
