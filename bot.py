import os
import random
from json import load
import discord
from discord.ext import commands
from dotenv import load_dotenv
from re import match
import giphy_client
from giphy_client.rest import ApiException
import requests
import instaloader

os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GIPHY_TOKEN = os.getenv("GIPHY_TOKEN")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


# USEFUL FUNCTIONS
def case_correction(message, response):
    if message.isupper():
        return response.upper()
    elif message.islower():
        return response.lower()
    else:
        return response.title()


def search_gifs(query):
    try:
        return giphy_client.DefaultApi().gifs_search_get(GIPHY_TOKEN, query, limit=10, rating='g')
    except ApiException as e:
        return f"Exception when calling DefaultApi->gifs_search_get: {e}\n"


def gif_response(emotion):
    gifs = search_gifs(emotion)
    lst = list(gifs.data)
    gif = random.choices(lst)
    return gif[0].url


# BASIC TEXT COMMANDS
bot = commands.Bot(command_prefix="?")  # All commands will start with ?


@bot.command(name="sally")
async def sally(ctx, arg: str):
    if arg == "help":
        with ctx.channel.typing():
            embed = discord.Embed(title="Sally the Seahorse Help", description="Available Commands:", colour=0x7413dc)
            embed.add_field(name="?sally hi", value="Sally will say hi to you!")
            embed.add_field(name="?sally leo", value="Sally will talk about Leo the Lion")
            embed.add_field(name="?sally git", value="A link to the SallyBot git will be sent")
            embed.add_field(name="?sally rally", value="Sally will talk about Viking Rally")
            embed.add_field(name="?sally steal", value="Try and steal me!")
            embed.add_field(name="?sally fact", value="Get a random fact about me and my fellow Seahorses")
            embed.add_field(name="?sally credits", value="Learn more about how created me")
            embed.add_field(name="?sally insta", value="Find out more about mine and Leo's Instagram")
            await ctx.send(embed=embed)

    elif arg == "hi":
        with ctx.channel.typing():
            await ctx.send(f'Hi {ctx.author.mention}!')

    elif arg == "leo":
        with ctx.channel.typing():
            await ctx.send("Leo is my Best Friend! We go on all our adventures together but he has to protect me, as "
                           "other SSAGO-ers like to steal me! :frowning:")

    elif arg == "git":
        with ctx.channel.typing():
            await ctx.send("Here's the git repo that contains all my inner code. I may look like the best teddy "
                           "Seahorse you've ever seen but there's a computer behind me!\n"
                           "https://github.com/TimRodaway/SallyBot")

    elif arg == "rally":
        with ctx.channel.typing():
            await ctx.send("Did you know my friends from NUSSAGG and DUSAGG are hosting Viking Rally in November 2021! "
                           "Please come join us for a weekend of great fun in the Toon and surrounding areas. Its a "
                           "canny place to be!")

    elif arg == "credits":
        with ctx.channel.typing():
            try:
                with open("data/contributors.txt", "r") as f:
                    contributors = f.readline()
                    credit = f"I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. I have the " \
                        f"following people to thank for my creation: {contributors}"
                    await ctx.send(credit)
            except FileNotFoundError:
                await ctx.send("I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. Unfortunately my "
                               "memory's currently a little fuzzy as to who made me.")

    # random seahorse fact
    elif arg == "fact":
        with ctx.channel.typing():
            try:
                with open("data/facts.json", "r") as f:
                    facts = load(f)
                    fact = facts[str(random.choice(range(len(facts))))]
                    await ctx.send(fact)
            except FileNotFoundError:
                await ctx.send("I don't seem to know any facts at the minute :tired_face:. Please try again later!")

    elif arg == "can I be your friend?":
        with ctx.channel.typing():
            try:
                friend_list = []
                with open("data/friends.txt", "r") as f:
                    line = f.readline()
                    friends = line.split(",")
                    for friend in friends:
                        friend_list.append(friend)
                if ctx.author.id in friend_list:
                    await ctx.send(f"{ctx.author.mention} you're already my friend!")
                else:
                    with open("data/friends.txt", "a") as f:
                        f.write(f",{ctx.author.id}")
                    await ctx.send(f"{ctx.author.mention} you're now my friend!")
            except FileNotFoundError:
                await ctx.send(f"My memory's a little fuzzy right now. Please try asking me again later!")

    elif arg == "steal":
        with ctx.channel.typing():
            try:
                friend_list = []
                with open("data/friends.txt", "r") as f:
                    line = f.readline()
                    friends = line.split(",")
                    for friend in friends:
                        friend_list.append(friend)
                if ctx.author.roles == "692795798416523356":
                    await ctx.send(f"{ctx.author.mention} you can't steal me, you're part of my club")
                # if a friend tries to steal, un-friend them
                if ctx.author.id in friend_list:
                    friend_list.remove(ctx.author.id)
                    with open("data/friend.txt", "w") as f:
                        f.write(",".join(friend_list))
                    await ctx.send(f"{ctx.author.mention} you were meant to be my friend")
                # if someone else tries to steal, they fail
                else:
                    await ctx.send("Better luck next time, I swam away")
            except FileNotFoundError:
                await ctx.send("Better luck next time, I swam away")

    elif arg == "insta":
        with ctx.channel.typing():
            await ctx.send("You can find mine and <!@689751502700675072>'s Instagram here -> "
                           "https://www.instagram.com/nussaggsallyandleo/")

            # displays the latest instagram photo on Sally and Leo's profile
            insta = instaloader.Instaloader()
            insta.login("nussaggsallyandleo", INSTAGRAM_PASSWORD)
            profile = instaloader.Profile.from_username(insta.context, "nussaggsallyandleo")
            posts = profile.get_posts()
            post = next(posts)
            if not os.path.isdir("temp"):
                os.mkdir("temp")
            with open("temp/latest_insta.jpg", "wb") as f:
                f.write(requests.get(post.url).content)
            await ctx.send(file=discord.File("temp/latest_insta.jpg"))
        os.remove("temp/latest_insta.jpg")

    # if command doesn't exist
    else:
        with ctx.channel.typing():
            await ctx.send("I don't understand you! Type '!sally help' to learn what I can do")


async def on_message(message):
    channel = message.channel

    # stops it replying to itself
    if message.author == discord.Client.user or message == "":
        return

    # reacts to all of Leo's messages
    elif message.author == "LeoBot":
        with channel.typing():
            await message.add_reaction(emoji="<:Sally:689616621576257557>")

    # responds to Leo's Roars
    elif message.author == "LeoBot" and match("^Ro+a+r$", message) is not None:
        with channel.typing():
            choice = random.choice(range(3))
            if choice == 0:
                count = message.count("o")
                await channel.send(f"{'a' * count + 'r' * int(count/2) + 'g' * int(count/2) + 'h' * int(count/2)}")
            elif choice == 1:
                await channel.send(gif_response("scream"))
            else:
                await channel.send(":shushing_face:")

    # Geordie Translations
    # special case for "no"
    elif (message.lower()) == "no":
        with channel.typing():
            await channel.send(case_correction(message, "nar"))

    # special case for "good"
    elif (message.lower()) == "good":
        with channel.typing():
            await channel.send(f"In the Newcastle we'd say that like: {case_correction(message, 'canny good like')}")

    # special case for "yes"
    elif (message.lower()) == "yes":
        with channel.typing():
            await channel.send(f"In the Newcastle we'd say that like: {case_correction(message, 'whey aye man')}")

    # special case for "really good"
    elif (message.lower()) == "really good":
        with channel.typing():
            await channel.send(f"In the Newcastle we'd say that like: {case_correction(message, 'purely belta')}")

    # normal translations
    else:
        with open("data/geordie.json", "r") as f:
            translations = load(f)
            msg = message.split(" ")
            if any(x in translations.keys() for x in msg):
                with channel.typing():
                    new_msg = []
                    for word in msg:
                        if word == translations.keys():
                            new_word = translations[word]
                            new_msg.append(new_word)
                        else:
                            new_msg.append(word)
                    await channel.send(f"In the Newcastle we'd say that like: {case_correction(message, new_msg)}")
            else:
                return


async def on_ready():
    print("I'm connected and ready to go!")
    
bot.run(TOKEN)
