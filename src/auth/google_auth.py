import os.path
import sys


# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/tasks"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "config/credentials.json"


class GoogleAuthManager:
    """Manages Google OAuth authentication and credential management."""
    
    def __init__(self, scopes=None, token_file=None, credentials_file=None):
        """Initialize the auth manager with configurable paths."""
        self.scopes = scopes or SCOPES
        self.token_file = token_file or TOKEN_FILE
        self.credentials_file = credentials_file or CREDENTIALS_FILE
        self._credentials = None
    
    def get_credentials(self) -> Credentials:
        """Retrieve and refresh OAuth credentials."""
        if self._credentials and self._credentials.valid:
            return self._credentials
            
        creds = None
        
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            except Exception:
                # If token is corrupted, remove it and start fresh
                os.remove(self.token_file)
                creds = None
            
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    # If refresh fails, force re-authentication
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                except FileNotFoundError:
                    raise FileNotFoundError(
                        f"Error: {self.credentials_file} not found. Please download it from Google Cloud Console."
                    )
                    
                # Save the credentials for the next run
                with open(self.token_file, "w") as token:
                    token.write(creds.to_json())
        
        self._credentials = creds
        return creds
    
    def refresh_credentials(self) -> Credentials:
        """Force refresh of credentials by removing token file."""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        self._credentials = None
        return self.get_credentials()
        
    def build_service(self, api_name='tasks', api_version='v1', force_refresh=False):
        """Build and return a Google API service."""
        if force_refresh:
            self.refresh_credentials()
        
        creds = self.get_credentials()
        return build(api_name, api_version, credentials=creds)
