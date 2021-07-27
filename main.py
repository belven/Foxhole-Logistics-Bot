import os
import discord
import requests
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from replit import db

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('foxhole-data-365f75e26908.json', scope)

# authorize the clientsheet 
client_gd = gspread.authorize(creds)

client = discord.Client()


example_array = ['A', 'b', 'c']

amount_id = 3
item_id = 2
location_id = 1

database_name = "requests"

def get_data():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


def add_request(request):
    split_request = slipt_request(request)
    requests = None

    if check_requests_database():
        requests = db[database_name]
        existing_request = check_existing_request(split_request)

        if existing_request is not None:
            split_existing = slipt_request(existing_request)
            val = get_request_amount(split_request) + get_request_amount(
                split_existing)
            split_existing[amount_id] = val
            requests.append(combine_request(split_request))

        else:
            requests.append(request)
    else:
        database_request = create_database_request(split_request)
        requests = database_request
        db[database_name] = create_database_request(split_request)


def create_database_request(split_request):
    combined_request = combine_request(split_request)
    return [
        get_request_location(split_request) + '_' +
        get_request_item(split_request), combined_request
    ]


def find_request(location, item):
    if check_requests_database():
        requests = db[database_name]

        for request in requests:
            data = requests[request]

            if location in data and item in data:
                print(request)
                return request
    return None


def check_requests_database():
    return database_name in db.keys() and db[database_name] is not None


def slipt_request(request):
    return re.findall(r'\S+', request)


#Takes in split request !request location item amount
def get_request_item(split_request):
    return split_request[item_id]


#Takes in split request !request location item amount
def get_request_amount(split_request):
    return split_request[amount_id]


#Takes in split request !request location item amount
def get_request_location(split_request):
    return split_request[location_id]


#Takes in split request !request location item amount
def combine_request(split_request):
    complete_request = get_request_location(
        split_request) + ' ' + get_request_item(
            split_request) + ' ' + get_request_amount(split_request)
    return complete_request


#Takes in split request !request location item amount
def check_existing_request(new_request):
    if database_name in db.keys():
        requests = db[database_name]
        location = get_request_location(new_request)
        item = get_request_item(new_request)

        id = find_request(location, item)

        if id is not None:
            return requests[id]
    return None


def delete_request(index):
    requests = db[database_name]
    if len(requests) > index:
        del requests[index]
        db[database_name] = requests


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    sheet = client_gd.open('Test Data')

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    val = sheet_instance.cell(col=3,row=2)

    print(val)

    #get_values(me, sheet_id, range_name)
    if check_requests_database():
        db[database_name].clear()


def get_values(self, spreadsheet_id, range_name):
    service = self
    
    # [START sheets_get_values]
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                 range=range_name).execute()
    rows = result.get('values', [])
    print('{0} rows retrieved.'.format(len(rows)))
    # [END sheets_get_values]
    return result

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!test'):
        await message.channel.send('Do not test me!')
    if message.content.startswith('!quote'):
        await message.channel.send(get_data())
    if message.content.startswith('!request'):
        add_request(message.content)


my_secret = os.environ['token']

client.run(my_secret)
