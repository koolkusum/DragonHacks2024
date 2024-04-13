import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime

from user import User, UserDatabase

pomodoro_running = True

async def hello(message : discord.message.Message):
    options = ["Hi ", "Hey ", "Hello ", "Howdy ", "Hi there ", "Greetings ", "Aloha ", "Bonjour ", "Ciao ", "Hola ", "How's it going? ", "Howdy-do ", "Good day ", "Wassup ", "What's popping? ", "What's up? ", "Hiya ", "What's new? ", "How are you? "]
    current_time = datetime.datetime.now().time().hour
    if current_time > 12:
        options.append("Good Afternoon! ")
    else:
        options.append("Good Morning! ")
    chosen_string = options[random.randint(0, len(options) - 1)]
    string = chosen_string + message.author.mention
    embed = discord.Embed(title = chosen_string, description=string, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.set_footer(text="!hello")
    await message.channel.send(file=file, embed=embed)

async def time(message : discord.message.Message):
    date = datetime.datetime.now()
    year = str(date.year).zfill(2)
    day = str(date.day).zfill(2)
    month = str(date.month).zfill(2)
    hour = str(date.hour).zfill(2)
    minute = str(date.minute).zfill(2)
    second = str(date.second).zfill(2)

    result_string = f'**Today is:** {year}-{day}-{month}\n**The time is:** {hour}:{minute}:{second}'
    embed = discord.Embed(title=result_string, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.set_footer(text="!time")
    await message.channel.send(file=file, embed=embed)

async def pomodoro(message : discord.message.Message, client: discord.Client):
    result_string = f'Enter Study Time'
    help_description = f'''Enter the minutes of how long you want to study for?'''
    embed = discord.Embed(title=result_string, description=help_description, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.set_footer(text="!pomodoro")
    await message.channel.send(file=file, embed=embed)
    def check(m):
        return m.author == message.author and m.channel == message.channel
    study_time = await client.wait_for('message', check=check, timeout=30)
    try:
        if not study_time.content.isdigit():
            result_title = f'Invalid Output'
            result_description = f'Pomodoro did not start for **{message.author.mention}**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="!pomodoro")
            await message.channel.send(file=file, embed=embed)
            return        
    except asyncio.TimeoutError:
        string = f'{message.author.mention} has taken too long to respond.'
        embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="!adduser")
        await message.channel.send(file=file, embed=embed)
    result_string = f'Enter Break Time'
    help_description = f'''Enter the minutes of how long you want to break to be for?'''
    embed = discord.Embed(title=result_string, description=help_description, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.set_footer(text="!pomodoro")
    await message.channel.send(file=file, embed=embed)
    def check(m):
        return m.author == message.author and m.channel == message.channel
    break_time = await client.wait_for('message', check=check, timeout=30)
    try:
        if not break_time.content.isdigit():
            result_title = f'Invalid Output'
            result_description = f'Pomodoro did not start for **{message.author.mention}**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="!pomodoro")
            await message.channel.send(file=file, embed=embed)
            return        
    except asyncio.TimeoutError:
        string = f'{message.author.mention} has taken too long to respond.'
        embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="!adduser")
        await message.channel.send(file=file, embed=embed)    
    study_time_content = int(study_time.content)
    break_time_content = int(break_time.content)
    study_seconds = study_time_content * 60
    break_seconds = break_time_content * 60
    pomodoro_running = True
    while pomodoro_running:
        result_title = f'Study Time Started'
        result_description = f'Pomodoro started for **{message.author.mention}**\nStart working for {study_time_content} minutes'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="!pomodoro")
        await message.channel.send(file=file, embed=embed)
        for i in range(study_seconds):
            try:
                end = await client.wait_for('message', check=check, timeout=1)
                if end.content == '!terminate':
                    pomodoro_running = False
                    print(False)
                    result_title = f'Pomodoro Terminated'
                    result_description = f'Pomodoro terminated for **{message.author.mention}**'
                    embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                    file = discord.File('images/icon.png', filename='icon.png')
                    embed.set_thumbnail(url='attachment://icon.png')
                    embed.set_author(name="Reminder-Bot says:")
                    embed.set_footer(text="!pomodoro")
                    await message.channel.send(file=file, embed=embed) 
                    return
            except asyncio.TimeoutError:
                continue

        result_title = f'Break Time Started'
        result_description = f'Pomodoro started for **{message.author.mention}**\nStart chilling for {break_time_content} minutes'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="!pomodoro")
        await message.channel.send(file=file, embed=embed)
        for i in range(break_seconds):
            try:
                end = await client.wait_for('message', check=check, timeout=1)
                if end.content == '!terminate':
                    print(False)
                    pomodoro_running = False
                    result_title = f'Pomodoro Terminated'
                    result_description = f'Pomodoro terminated for **{message.author.mention}**'
                    embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                    file = discord.File('images/icon.png', filename='icon.png')
                    embed.set_thumbnail(url='attachment://icon.png')
                    embed.set_author(name="Reminder-Bot says:")
                    embed.set_footer(text="!pomodoro")
                    await message.channel.send(file=file, embed=embed) 
                    return
            except asyncio.TimeoutError:
                continue
        
async def help(message : discord.message.Message, client : discord.Client):
    result_string = f'!Help'
    help_description = f'''How to use {client.user.mention}'''
    embed = discord.Embed(title=result_string, description=help_description, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.add_field(name="!hello", value="returns a friendly greeting!", inline=False)
    embed.add_field(name="!time", value="tells the current time.", inline=False)
    embed.add_field(name="!adduser", value="adds user to the database", inline=False)
    embed.add_field(name="!userinfo", value="returns user information from the database", inline=False)
    embed.add_field(name="!changereminder", value="changes the time that the user wants to be notified of the tasks", inline=False)
    embed.add_field(name="!deleteuser", value="deletes user from the database", inline=False)
    embed.add_field(name="!addtask", value="adds a task to the task list", inline=False)
    embed.add_field(name="!todaytask", value="displays the tasks that end on the current date", inline=False)
    embed.add_field(name="!alltasks", value="shows all uncompleted tasks", inline=False)
    embed.add_field(name="!removetask", value="removes tasks from tasks list", inline=False)
    embed.add_field(name="!completetask", value="updates an uncompleted task into completed", inline=False)
    embed.add_field(name="!pomodoro", value="initializes the pomodoro method", inline=False)
    embed.add_field(name="!help", value="shows the help menu", inline=False)
    embed.set_footer(text="!help")
    await message.channel.send(file=file, embed=embed)

async def invalidInput(message : discord.message.Message, client : discord.Client):
    result_string = f'[ERROR]: Invalid Input'
    help_description = f'''How to use {client.user.mention}'''
    embed = discord.Embed(title=result_string, description=help_description, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.add_field(name="!hello", value="returns a friendly greeting!", inline=False)
    embed.add_field(name="!time", value="tells the current time.", inline=False)
    embed.add_field(name="!adduser", value="adds user to the database", inline=False)
    embed.add_field(name="!userinfo", value="returns user information from the database", inline=False)
    embed.add_field(name="!changereminder", value="changes the time that the user wants to be notified of the tasks", inline=False)
    embed.add_field(name="!deleteuser", value="deletes user from the database", inline=False)
    embed.add_field(name="!addtask", value="adds a task to the task list", inline=False)
    embed.add_field(name="!todaytask", value="displays the tasks that end on the current date", inline=False)
    embed.add_field(name="!alltasks", value="shows all uncompleted tasks", inline=False)
    embed.add_field(name="!removetask", value="removes tasks from tasks list", inline=False)
    embed.add_field(name="!completetask", value="updates an uncompleted task into completed", inline=False)
    embed.add_field(name="!pomodoro", value="initializes the pomodoro method", inline=False)
    embed.add_field(name="!help", value="shows the help menu", inline=False)
    embed.set_footer(text="[ERROR]: Invalid Input")
    await message.channel.send(file=file, embed=embed)