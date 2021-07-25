import os
import discord
import requests
import json

client = discord.Client()

example_array = ['A', 'b', 'c']

def get_data():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith('!test'):
    await message.channel.send('Do not test me!')
  if message.content.startswith('!quote'):
    await message.channel.send(get_data())

my_secret = os.environ['token']

client.run(my_secret)