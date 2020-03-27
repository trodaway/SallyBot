import os
import random
import requests
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BASE_URL = os.getenv('BASE_URL') #Base URL for API Calls

## USEFUL FUNCTIONS ##
def dataRequest(path): #Returns JSON from Database API Calls
    url = BASE_URL + path
    r = requests.get(url = url)
    return r.json()

## BASIC TEXT COMMANDS ##
bot = commands.Bot(command_prefix='!') #All commands will start with !

@bot.command(name='leo')
async def leo(ctx, arg: str):
    if arg == "help":
        embed = discord.Embed(title="Leo the Lion Help", description="Available Commands:", colour=0x7413dc)
        
        embed.add_field(name="!leo hi", value="Leo will say hi to you!")
        embed.add_field(name="!leo sally", value="Leo will talk about Sally the Seahorse")
        embed.add_field(name="!leo git", value="A link to the LeoBot git will be sent")
        embed.add_field(name="!leo rally", value="Leo will talk about Viking Rally")
        embed.add_field(name="!leo steal", value="Try and steal leo, but it won't end well!")
        embed.add_field(name="!leo adventure", value="Leo will say what adventure he wants to go on next!")
        embed.add_field(name="!leo memory", value="Leo will tell you one of his favourite memories with NUSSAGG")
        embed.add_field(name="!roar <length>", value="Leo will roar for the length specified (up to a value of 999)")

        await ctx.send(embed = embed)

    elif arg == "hi":
        await ctx.send(
            f'Hi {ctx.author.mention}!'
        )

    elif arg == "sally":
        await ctx.send(
            f'Sally (:sally:) is my Best Friend! We go on all our adventures together but we have to protect her, as other SSAGOers like to steal her! :frowning:'
        )

    elif arg == "git":
        await ctx.send(
            f'Here\'s the git repo that contains all my inner code. I may look like the best teddy lion you\'ve ever seen but theres a computer behind me!' +
            '\n' +
            'https://github.com/JWB-Git/LeoBot'
        )

    elif arg == "rally":
        await ctx.send(
            f'Did you know my friends from NUSSAGG and DUSSAG are hosting Viking Rally in November 2021! Please come join us for a weekend of great fun in the Toon '+
            'and surrounding areas. Its a canny place to be!'
        )

    elif arg == "steal":
        await ctx.send(
            f'You can\'t steal me! Sally (:sally:) is NUSSAGG\'s stealable mascot!'
        )

    elif arg == "drink":
        await ctx.send(
            f'Cheers! :beers:'
        )

    elif arg == "adventure":
        mascotData = dataRequest('read/mascots.php')
        locationData = dataRequest('read/locations.php')

        if mascotData['success'] == 1 and locationData['success'] == 1:
            mascots = mascotData['mascots']
            locations = locationData['locations']

            mascot = random.choice(mascots)
            location = random.choice(locations)

            await ctx.send(
                f'I want to go to {location} with {mascot} on my next adventure! :airplane:'
            )
        else:
            await ctx.send(f'I don\'t know where I would like to visit next right now, but ask me again later!')

    elif arg == "memory":
        data = dataRequest('read/memories.php')

        if data['success'] == 1:
            memories = data['memories']
            memory = random.choice(memories)
            await ctx.send(memory)
        else:
            await ctx.send(f'I can\'t seem to remember anything at the minute :tired_face:. Please try again later!')

    else:
        await ctx.send(f'I don\'t understand you! Type \'!leo help\' to learn what I can do')

@bot.command(name='roar', help='Make Leo Roar!')
async def roar(ctx, length: int):
    if length == 69:
        await ctx.send(f':rolling_eyes:')
    elif length == 666:
        await ctx.send(f':japanese_ogre:')
    elif length <= 0:
        await ctx.send(f'How would I roar for zero or negative length!?')
    elif length > 999:
        await ctx.send(f'I can\'t roar for that long!')
    else:
        roar_str = 'R'
        for i in range(length):
            roar_str += 'o'
        for i in range(length):
            roar_str += 'a'
        roar_str += 'r'

        await ctx.send(roar_str)
    
bot.run(TOKEN)