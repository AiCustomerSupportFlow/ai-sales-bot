import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open("AI Leads CRM").sheet1


def save_to_sheet(user_id, product, city, phone):
    sheet.append_row([
        str(datetime.now()),
        str(user_id),
        product,
        city,
        phone
    ])