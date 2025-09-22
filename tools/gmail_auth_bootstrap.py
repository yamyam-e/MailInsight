from __future__ import print_function
import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

home = pathlib.Path.home()
secrets_dir = home / '.mailinsight'
secrets_dir.mkdir(parents=True, exist_ok=True)

cred_path = secrets_dir / 'credentials.json'
token_path = secrets_dir / 'token.json'

if not cred_path.exists():
    raise FileNotFoundError(f"credentials.json not found at {cred_path}")

flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
creds = flow.run_local_server(port=0)  # 브라우저 열림
token_path.write_text(creds.to_json())
print(f"[OK] Saved token to {token_path}")
