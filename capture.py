
import collections
import sys
import json
import os
from problem import Problem, MAX_NAMES, Cell, Spreadsheet
from solve import solve

from google.auth.transport.requests import Request      # type: ignore
from google.oauth2.credentials import Credentials       # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build             # type: ignore
from googleapiclient.errors import HttpError            # type: ignore

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



class CredentialsError(Exception):
    pass

def cell_name_fn(cell: Cell) -> str:
    (column, row) = cell
    return "R{}C{}".format(row + 1, column + 1)

def main() -> None:
    spreadsheet_id = open("spreadsheet.id", "rt").read().strip()

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        # Get a copy of the sheet
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                range="Input!{}:{}".format(
                        cell_name_fn((0, 0)),
                        cell_name_fn((MAX_NAMES + 1, MAX_NAMES)))).execute()
        values = Spreadsheet(result.get('values', []))
       
        problem = Problem.from_spreadsheet(values, cell_name_fn)
        assert problem.validate_problem()
        json.dump(problem.to_dict(), open("live_input.json", "wt"), indent=4)
        solve(problem)
        values = problem.to_spreadsheet()
        assert problem.validate_solution()

        sheet.values().update(spreadsheetId=spreadsheet_id,
                range="Output!{}:{}".format(
                        cell_name_fn((0, 0)),
                        cell_name_fn(values.get_bottom_right())),
                valueInputOption="RAW",
                body={"values": values.values}).execute()


        print(problem.to_text())
        json.dump(problem.to_dict(), open("solution.json", "wt"), indent=4)


    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main()
