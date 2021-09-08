import os
import discord
import gspread
import re
from replit import db
from discord.ext import tasks
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('foxhole-data-365f75e26908.json', scope)

# authorize the clientsheet 
client_gd = gspread.authorize(creds)

client = discord.Client()

shield = { 'server' : 'S.H.I.E.L.D.', 'channel' : 'shield-clan-chat'}

sheet_names = {}
sheet_names[0] = {'Name' : 'W_Frontlines', 'Sheet' : 0 }
sheet_names[1] = {'Name' : 'W_Valuables', 'Sheet' : 1 }
sheet_names[2] = {'Name' : 'SF_Frontlines', 'Sheet' : 2}
sheet_names[3] = {'Name' : 'SF_Valuables', 'Sheet' : 3}

def report_data(channel, sheet_index):
    table_data = None
    sheet = client_gd.open('SHIELD STOCKPILES')
    index = get_sheet_index(sheet_index)
    sheet_instance = sheet.get_worksheet(index)
    records_data = sheet_instance.get_all_records()

    for data_row in records_data:
        name = data_row['Name']
        amount_needed = data_row['Amount Needed']
        stock_type = data_row['Type']
        is_vehicle = stock_type == 'Vehicle' or stock_type == 'Vehicles Crated'

        if amount_needed > 0 and not is_vehicle:
            if name is None:
                name = ''

            if amount_needed is None:
                amount_needed = ''

            data_row = name + ' ' + str(amount_needed)

            if table_data is None:
                table_data = [data_row]
            else:
                table_data.append(data_row)
    
    return table_data

def get_sheet_index(location):

    for data_row in sheet_names:
        name = sheet_names[data_row]['Name']

        if name.lower() == location.lower():
            return int(sheet_names[data_row]['Sheet'])


def slipt_by_sapce(text):
    return re.findall(r'\S+', text)

def get_server_channel_id(server_in, channel_in):
    for server in client.guilds:
      if server.name == server_in:
         for channel in server.channels:
            if channel.name == channel_in:
                return channel.id     
    return ''   
    

def report_sheets():
    text = ''

    for data_row in sheet_names:
        name = sheet_names[data_row]['Name']
        sheet = sheet_names[data_row]['Sheet']
        text = text + '\n'
        text = text + name + ' ' + str(sheet)
    
    return text

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!test'):
        await message.channel.send('Do not test me!')
    if (message.content.startswith('!report_stock_test')):
        location = slipt_by_sapce(message.content)[1]
        data = report_data(message.channel, location)
        message_data = '\n'

        for md in data:
          message_data = message_data + md + '\n'

        await message.author.send(message_data)
    elif(message.content.startswith('!report_stock')):
        location = slipt_by_sapce(message.content)[1]
        data = report_data(message.channel, location)
        message_data = '\n'

        for md in data:
            message_data = message_data + md + '\n'

        await message.channel.send(message_data)
    elif(message.content.startswith('!report_sheets')):
        text = report_sheets()
        await message.channel.send(text)

client.run(my_secret)
