
import collections
from problem import Problem, MAX_NAMES

from google.auth.transport.requests import Request      # type: ignore
from google.oauth2.credentials import Credentials       # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build             # type: ignore
from googleapiclient.errors import HttpError            # type: ignore

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



class CredentialsError(Exception):
    pass

def cell_name_fn(column: int, row: int) -> str:
    return chr(ord('A') + column) + str(row + 1)

def main() -> None:
    spreadsheet_id = open("spreadsheet.id", "rt").read().strip()
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    if not creds.valid:
        raise CredentialsError("Credentials are not valid")

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        # Get a copy of the sheet
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                range="Input!{}:{}".format(
                        cell_name_fn(0, 0),
                        cell_name_fn(MAX_NAMES + 1, MAX_NAMES))).execute()
        values = result.get('values', [])
       
        # Convert to X, Y coordinates
        values2 = collections.defaultdict(lambda: "")
        for (y, row) in enumerate(values):
            for (x, col) in enumerate(row):
                values2[(x, y)] = col

        problem = Problem.from_spreadsheet(values2, cell_name_fn)
        print(problem.to_text())


    except HttpError as err:
        print(err)



if __name__ == '__main__':
    main()
