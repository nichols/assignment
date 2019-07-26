from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import pickle
import re
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

CREDENTIALS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

_getter = None

def process_cell(cell):
  cell = cell.strip()
  m = re.match(r"(\d*)(\.\d*)?$", cell)
  if not m or not cell:
    return cell
  elif m.group(2):
    return float(cell)
  else:
    return int(m.group(1))


class SheetsDataGetter:
  def __init__(self):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    self.api = build('sheets', 'v4', credentials=creds).spreadsheets()

  def get_data_for_range(self, spreadsheet_id, sheet_range):
    raw_data = self.api.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute().get("values", [])
    return [list(map(process_cell, row)) for row in raw_data]


def get_data_for_range(spreadsheet_id, sheet_range):
  global _getter
  if not _getter:
    _getter = SheetsDataGetter()
  return _getter.get_data_for_range(spreadsheet_id, sheet_range)


def get_data_for_params(spreadsheet_id, upper_left, lower_right, sheet_name=None):
  sheet_range = "{}:{}".format(sheet_name, upper_left, lower_right)
  if sheet_name:
    sheet_range = "{}!{}".format(sheet_name, sheet_range)
  return get_data_for_range(spreadsheet_id, sheet_range)


def _test_data():
  sheet_id = '1WydOez3OoBKLvxsdUaZQ8s9d5xBK7BY9dzBIyxJXzgk'
  sheet_range = "A1:H10"
  values = get_data_for_range(sheet_id, sheet_range)

  return values


def main():
  print(_test_data())


if __name__ == '__main__':
    main()
