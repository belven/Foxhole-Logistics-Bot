import os
import discord
import gspread
from discord.ext import tasks
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('foxhole-data-365f75e26908.json', scope)

# authorize the clientsheet 
client_gd = gspread.authorize(creds)

client = discord.Client()

servers = { { 'server' : "S.H.I.E.L.D.", 'channel' : "shield-clan-chat"} }

def report_data(channel):
    table_data = None
    sheet = client_gd.open('SHIELD STOCKPILES')
    sheet_instance = sheet.get_worksheet(2)
    records_data = sheet_instance.get_all_records()

    for data_row in records_data:
        name = data_row['Name']
        amount_needed = data_row['Amount Needed']

        if amount_needed > 0:
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


def get_server_channel_id(server_in, channel_in):
    for server in client.guilds:
      if server.name == server_in:
         for channel in server.channels:
            if channel.name == channel_in:
                return channel.id     
    return ''   
    

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    report_data_loop.start()


# Every 6 hours
@tasks.loop(seconds=21600.0)
async def report_data_loop():
  channel_id = get_server_channel_id("S.H.I.E.L.D.", "shield-clan-chat")
  channel = client.get_channel(channel_id)
  data = report_data(channel)
  message_data = '\n'

  for md in data:
    message_data = message_data + md + '\n'

  await channel.send(message_data)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!test'):
        await message.channel.send('Do not test me!')
    if message.content.startswith('!report_stock'):
        data = report_data(message.channel)
        message_data = '\n'

        for md in data:
          message_data = message_data + md + '\n'

        await message.channel.send(message_data)


my_secret = 'ODY4ODI0NjIzNDk0NTk0NTkw.YP1R_A.8wthZjnflM9Ch4rYCJDPKvJsGQA'

client.run(my_secret)