import os
import json
import requests
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from edapi import EdAPI
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Tag
import sys
from PIL import Image
import os

# Load environment variables
load_dotenv()


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
ED_API_TOKEN = os.getenv('ED_API_TOKEN')
ED_API_URL = os.getenv('ED_API_URL')

# initialize Ed API
ed = EdAPI()
ed.login()
user_info = ed.get_user_info()
# print("user_info is: ", user_info)
user = user_info['user']
print(f"Hello {user['name']}!")


client = discord.Client(intents=discord.Intents.default())
# Store the last seen thread number to avoid duplicate messages
last_seen_thread_number = None


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await send_initial_message()
    # await send_specific_to_discord()
    await check_for_new_thread()


async def send_initial_message():
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send("Ed Monitor here, I make your life simpler, hopefully")
        print('Sent initial message to Discord')
    else:
        print(f'Channel with ID {DISCORD_CHANNEL_ID} not found')



async def send_specific_to_discord():
    thread = ed.get_course_thread(53090, 911)
    # Check if the thread was retrieved successfully
    if thread and 'content' in thread:
        print("Thread found!")
        xml_content = thread['content']  # raw format

        # Parse the XML content with BeautifulSoup
        soup = BeautifulSoup(xml_content, 'xml')
        paragraphs = soup.find_all('paragraph')
        
        # Extract text from paragraphs and format it
        formatted_content = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(formatted_content)  # Send the formatted content to the Discord channel
            print('Sent thread content to Discord')
        else:
            print(f'Channel with ID {DISCORD_CHANNEL_ID} not found')
    else:
        print("Thread NOT found!")



@tasks.loop(minutes=60)  # Adjust the interval as needed
async def check_for_new_thread():
    global last_seen_thread_number
    threads = ed.list_threads(53090)
    # print("THREAD: ", threads)
    for thread in threads:
        creator_id = thread['user_id']

    # for thread in threads:
    #     if thread['number'] > (last_seen_thread_number or 0):
    #         # Get the user's role who created the thread
    #         thread_creator_ID = thread['user_id']
            
    #         thread_creator_role = thread_creator['user']['role']  # Get the role of the user who created the thread
            
    #         # Check if the user is a staff or TA
    #         if thread_creator_role in ['staff', 'ta']:
    #             await send_thread_to_discord(thread)
    #             last_seen_thread_number = thread['number']  # Update the last seen thread number
    #             break



async def send_thread_to_discord(thread):
    # Check if the thread was retrieved successfully
    if thread and 'content' in thread:
        print("Thread found!")
        xml_content = thread['content']  # raw format

        # Parse the XML content with BeautifulSoup
        soup = BeautifulSoup(xml_content, 'xml')
        paragraphs = soup.find_all('paragraph')
        
        # Extract text from paragraphs and format it
        formatted_content = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
        content = f"New thread created by {thread['user_id']}:\nTitle: {thread['title']}\nContent: {formatted_content}"

        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(formatted_content)  # Send the formatted content to the Discord channel
            print('Sent thread content to Discord')
        else:
            print(f'Channel with ID {DISCORD_CHANNEL_ID} not found')
    else:
        print("Thread NOT found!")
        

client.run(DISCORD_TOKEN)
