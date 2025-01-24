from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for the application
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

# Path to the credentials file
CREDENTIALS_FILE = 'client_key.json'

def main():
    # Create the flow using the client secrets file from the Google API Console
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)

    # Make sure that the redirect URL is authorized in the oAuth client configuration
    flow.redirect_uri = "http://localhost:8888/"

    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    # Print the URL and instruct the user
    print("Please open the following URL in a new incognito/private window:")
    print(auth_url)

    # Prompt the user to paste the full redirect URL
    full_redirect_url = input('Enter the full redirect URL: ')

    parsed_url = urlparse(full_redirect_url)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get('code', [''])[0]

    # Exchange the code for a token
    flow.fetch_token(code=code)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(flow.credentials.to_json())

    print('Authentication successful. Refresh token and credentials are saved in token.json')

if __name__ == '__main__':
    main()
