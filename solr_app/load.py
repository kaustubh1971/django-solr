import django
import re
import os

os.sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_solr.settings')
django.setup()

from django_solr.settings import SAMPLE_SPREADSHEET_ID
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.utils import timezone as django_timezone
from datetime import datetime, timezone
from solr_app.models import JobApplication



# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]


# The ID and range of a sample spreadsheet.
SAMPLE_RANGE_NAME = "Form Responses 1!A1:O4330"

def is_string_float_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def string_starts_with_a_number(str_val):
    pattern = re.compile(r'\d+(\.\d+)?')
    return bool(pattern.match(str_val))

def string_starts_with_integer(str_val):
    pattern = re.compile(r'\d+')
    return bool(pattern.match(str_val))

def get_numbers_list_from_string(val):
    return [int(match.group()) for match in re.finditer(r'\d+', val)]

def is_range_provided(val):
    pattern = re.compile(r'(\d+)+\s*[-,to]+\s*(\d)+\s*(days?|weeks?|months?)')
    return bool(pattern.match(val))

def get_proper_ctc(val):
    value = 0
    if not val:
        return 0
    if val.isdigit():
        value = int(val)
        if value >= 1 and value < 100:
            value = value * 100000
    elif is_string_float_number(val):
        if float(val) >= 1.0 and float(val) < 100.0:
            value = float(val) * 100000
    elif string_starts_with_a_number(val):
        pattern = re.compile(r'^\d+(\.\d+)?[kK]$')
        lakh_pattern = re.compile(r'^\d+(\.\d+)?\s*(lacs?|lakhs?|lpa|ctc)?$')
        if bool(lakh_pattern.match(val.lower())):
            split_val = 'lpa' if 'lpa' in val.lower() else 'ctc' if 'ctc' in val.lower() \
                else 'lakhs' if 'lakhs' in val.lower() else 'lacs' in 'lacs' in val.lower()
            # value = float(val.lower().split('lpa')[0].strip())
            value = float(val.lower().split(split_val)[0].strip())
            if value < 100.0:
                value = value * 100000
        if ',' in val:
            try:
                normal_number_str = val.replace(',', "")
                value = int(normal_number_str)
            except Exception as ValueError:
                if 'year' in val.lower():
                    value = float(normal_number_str.lower().split('year')[0].strip())
        if bool(pattern.match(val.lower())):
            value = float(val.lower().split('k')[0].strip())
            value = value * 12
    return value

def refine_and_fetch_experience(val):
    experience = 0
    if not string_starts_with_integer(val) or val == 'fresher':
        return experience
    elif '-' in val:
        experience = int(val.split('-')[0])
    elif '+' in val:
        experience = int(val.split('+')[0])
    return experience

def get_proper_notice_period(val):
    value = 0
    if not val or val.lower().strip() in ['na', 'n/a']:
        return value
    elif val.isdigit():
        return int(val)
    elif string_starts_with_integer(val):
        # for range 15-30 days, 1-2 week, 1 to 2 months
        if is_range_provided(val.lower()):
            number_list = get_numbers_list_from_string(val)
            max_number = max(number_list)
            if 'week' in val.lower():
                value = max_number * 7
            elif 'month' in val.lower():
                value = max_number * 30
            else:
                value = max_number

        elif 'day' in val.lower():
            split_val = 'days' if 'days' in val.lower() else 'day'
            value = int(val.lower().split(split_val)[0].strip())
        elif 'dys' in val.lower():
            value = int(val.lower().split('dys')[0].strip())
        elif 'month' in val.lower():
            split_val = 'months' if 'months' in val.lower() else 'month'
            value = int(val.lower().split(split_val)[0].strip())
            value = value * 30
        elif 'week' in val.lower():
            value = int(val.lower().split("week")[0].strip())
            value = value * 7

    return value

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("solr_app/token.json"):
        creds = Credentials.from_authorized_user_file("solr_app/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "solr_app/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("solr_app/token.json", "w") as token:
            token.write(creds.to_json())

    # error_count = 0
    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        count = 0
        job_application_list = []
        for row in values:
            row_dict = {}
            count += 1
            if count == 1:
                continue

            datetime_object = datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S') if row[0] else None
            datetime_object = django_timezone.make_aware(datetime_object, timezone.utc)
            row_len = len(row)
            data_dict = {
                0: "timestamp",
                1: "email",
                2: "role",
                3: "why_us",
                4: "why_you",
                5: "social_profile_link",
                6: "resume_link",
                7: "mobile_number",
                8: "experience",
                9: "preferred_location",
                10: "name",
                11: "preferred_time_for_call",
                12: "other_role",
                13: "current_ctc",
                14: "notice_period"
            }
            for key, val in data_dict.items():
                if row_len > key:
                    row_dict[val] = row[key]
                else:
                    break

            if 'timestamp' in row_dict:
                row_dict['timestamp'] = datetime_object

            for key, value in row_dict.items():
                if key == 'current_ctc':
                    val = get_proper_ctc(value)
                    row_dict[key] = val
                if key == 'notice_period':
                    val = get_proper_notice_period(value)
                    row_dict[key] = val
                elif key == 'experience':
                    experience_val = refine_and_fetch_experience(value.lower())
                    row_dict['experience'] = experience_val

            job_application_list.append(JobApplication(**row_dict))

        JobApplication.objects.bulk_create(job_application_list)

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
