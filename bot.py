import os
import random
import json
import discord
from discord.ext import commands
import dotenv
import re
import giphy_client
from giphy_client.rest import ApiException
import requests
import instaloader
from bs4 import BeautifulSoup
import urllib.parse
import asyncio
import emoji
import datetime
import aiohttp
import io
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile("data/friends.txt"):
    with open("data/friends.txt", "w") as file:
        file.write("689579955012632586")  # adds Tim Rodaway, creator, as first friend

if not os.path.isdir("temp"):
    os.mkdir("temp")

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GIPHY_TOKEN = os.getenv("GIPHY_TOKEN")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

silence = False
on_ready_flag = False


# Sets how often the translator occurs, defaulting to 10
try:
    with open("data/translation_frequency.txt", "r") as freq_file:
        translator_frequency = int(freq_file.readline())
except FileNotFoundError:
    with open("data/translation_frequency.txt", "w") as freq_file:
        freq_file.write("15")
    translator_frequency = 15
print(f"Translation Frequency set to {translator_frequency}")


# USEFUL FUNCTIONS
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


def translator(text_to_translate, dialect="geordie"):
    demojized_text = emoji.demojize(text_to_translate)
    text_for_url = urllib.parse.quote(demojized_text)
    print(f"Text to translate: {text_to_translate}\nText for URL: {text_for_url}")
    url = f"http://www.whoohoo.co.uk/main.asp?string={text_for_url}&pageid={dialect}&topic=translator"
    x = requests.post(url, timeout=1)
    if x.status_code == 200:
        soup = BeautifulSoup(x.text, features="html.parser")
        translation = soup.find_all('form')[1].b.get_text(strip=True).encode("utf-8").\
            replace(b"\xc3\xa2\xc2\x80\xc2\x99", b"\x27").decode("ascii")
        if text_to_translate[0].isalpha() and text_to_translate[0].islower():
            translation = translation.replace(translation[0], translation[0].lower(), 1)  # corrects capital at start
        if not text_to_translate.endswith("."):
            translation = translation.rstrip(".")  # removes full stop if not in original text
        emojized_translation = emoji.emojize(translation)  # replaces emojis
        return emojized_translation
    else:
        print(f"POST Request returned a status code of {x.status_code} for {url}")
        return None


intents = discord.Intents.all()

# BASIC TEXT COMMANDS
bot = commands.Bot(command_prefix=commands.when_mentioned_or("?Sally"), case_insensitive=True, intents=intents)


async def status():
    while True:
        with open("data/activities.json", "r") as activities_file:
            activities = json.load(activities_file)
        single_activity = activities[str(random.choice(range(len(activities))))]
        if single_activity["type"] == "watching":
            activity = discord.Activity(name=single_activity["name"], type=discord.ActivityType.watching)
        elif single_activity["type"] == "listening":
            activity = discord.Activity(name=single_activity["name"], type=discord.ActivityType.listening)
        elif single_activity["type"] == "playing":
            activity = discord.Activity(name=single_activity["name"], type=discord.ActivityType.playing)
        else:
            activity = discord.Activity(name="The Sea", type=discord.ActivityType.watching)
        await bot.change_presence(activity=activity)
        # print(f"*****\nStatus Changed\nType: {single_activity['type']}\nName: {single_activity['name']}")
        await asyncio.sleep(10)


async def spotify():
    print("Started Spotify Task")
    with open("data/artists.json", "r") as artists_file:
        artists = json.load(artists_file)
    # which channel to send to, per guild
    # guild_channel = {689752642708308029: 689752642708308154}  # Test Server
    guild_channel = {689381329535762446: 690198193623007262}  # SSAGO Server
    while True:
        try:
            with open("temp/activities.json", "r") as temp_activities:
                activities = json.load(temp_activities)
        except FileNotFoundError:
            activities = {}
        guilds = bot.guilds
        for guild in guilds:
            if guild.id in guild_channel.keys():
                channel = bot.get_channel(guild_channel[guild.id])
                for member in guild.members:
                    for activity in member.activities:
                        if type(activity) is discord.Spotify:
                            # print(f"User: {member.display_name}\nArtist: {activity.artist}\nTitle: {activity.title}")
                            if any(i in artists.keys() for i in activity.artists) and \
                                    not any(i in activities.get(str(member.id)) for i in activity.artists):
                                for artist in activity.artists:
                                    if artist in artists.keys():
                                        print(f"{member.mention}\n{activity.title}\n{activity.artist}\n"
                                              f"{artists[artist]}")
                                        await channel.send(f"{member.mention}, I hope you're enjoying listening to "
                                                           f"{activity.title} by {activity.artist}!\n\n"
                                                           f"{artists[artist]}")
                                        print(f"{member.display_name} is listening to {artist}")
                                        activities[member.id] = artist
        with open("temp/activities.json", "w") as temp_activities:
            json.dump(activities, temp_activities)
        await asyncio.sleep(5)


async def catch_auto():
    await bot.get_user(689579955012632586).send("[INFO] catch_auto() triggered (pre while True)")
    while True:
        await bot.get_user(689579955012632586).send("[INFO] catch_auto at top of while True loop")
        # trigger once per day, at a random time
        time_of_day = random.random() * 86400
        now = datetime.datetime.now().timestamp() % 86400
        delay = time_of_day - now
        if delay < 0:
            delay += 86400

        await bot.get_user(689579955012632586).send(f"[INFO] catch_auto is delaying for {delay} seconds - next play is "
                                                    f"at {str(datetime.timedelta(seconds=time_of_day))}")
        print(f"Next random catch will be activated at {str(datetime.timedelta(seconds=time_of_day))}")
        await bot.get_user(689579955012632586).send("[INFO] catch_auto going to sleep")
        await asyncio.sleep(delay)
        await bot.get_user(689579955012632586).send("[INFO] catch_auto is awake")

        guild = [guild for guild in bot.guilds if guild.id == 689381329535762446][0]
        channel = [channel for channel in guild.channels if channel.id == 690198193623007262][0]

        with open("data/catch.json", "r") as catch_file:
            catchers = json.load(catch_file)
        catcher = catchers[str(random.choice(range(len(catchers))))]
        timeout = time.time() + 10
        while time.time() < timeout:
            if int(catcher["id"]) in [member.id for member in guild.members if member.status == discord.Status.online]:
                break
            catcher = catchers[str(random.choice(range(len(catchers))))]
        await channel.send(f"It's time for our daily game of catch! Since I don't have any arms I'm going to start by "
                           f"headbutting it over to <@{catcher['id']}> ...")
        if catcher.get("action") is not None:  # checks if bot requires an additional action to be able to catch
            await channel.send(f"{catcher['action']}")

        # sleeps until midnight
        now = datetime.datetime.now().timestamp() % 86400
        delay = 86400 - now
        await bot.get_user(689579955012632586).send(f"[INFO] catch_auto played, time to sleep until midnight for "
                                                    f"{delay} seconds")
        await asyncio.sleep(delay)
        await bot.get_user(689579955012632586).send("[INFO] catch_auto is at end of the loop")


async def avatar_auto():
    while True:
        try:
            now = datetime.datetime.now()
            if now.hour < 3:
                if not bot.user.avatar == "634c8e3fbdd6e6e831707a9b6767b00b":
                    with open("imgs/Sally_BadDrawing_UpsideDown.png", "rb") as pic:
                        await bot.user.edit(avatar=pic.read())
            elif now.hour >= 21:
                if not bot.user.avatar == "d97a7a9876d39a2761acd5b23213ca3f":
                    with open("imgs/Sally_BadDrawing.png", "rb") as pic:
                        await bot.user.edit(avatar=pic.read())
            else:
                if not bot.user.avatar == "47975935969cab20fd8e91d27be1b3ea":
                    with open("imgs/Sally_Normal.png", "rb") as pic:
                        await bot.user.edit(avatar=pic.read())
            await asyncio.sleep(60)
        except discord.errors.HTTPException:
            await asyncio.sleep(60)
            pass


@bot.command(name="hi", brief="I'll say hi", help="Say hi to me and I'll say hi back",
             aliases=["hello", "hey"])
async def hi(ctx):
    print(f"*****\nCommand: hi\nCalled by: {ctx.author}")
    await ctx.send(f'Hi {ctx.author.mention}!')


@bot.command(name="leo", brief="I'll talk about Leo", help="Leo is my best friend, let's talk about him!",
             aliases=["<@689751502700675072>", "<@!689751502700675072>", "<@&689751502700675072>"])  # Leo's user ID
async def leo(ctx):
    print(f"*****\nCommand: leo\nCalled by: {ctx.author}")
    await ctx.send("Leo is my Best Friend! We go on all our adventures together but he has to protect me, as other "
                   "SSAGO-ers like to steal me! :frowning:")


@bot.command(name="git", brief="Link to my Git repo", help="Get a link to the magic code behind me", aliases=["github"])
async def git(ctx):
    print(f"*****\nCommand: git\nCalled by: {ctx.author}")
    await ctx.send("Here's the git repo that contains all my inner code. I may look like the best teddy Seahorse you've"
                   " ever seen but there's a computer behind me!\nhttps://github.com/trodaway/SallyBot")


@bot.command(name="rally", brief="I'll talk about Viking Rally", help="Find out more about Viking Rally")
async def rally(ctx):
    print(f"*****\nCommand: rally\nCalled by: {ctx.author}")
    await ctx.send("My friends from NUSSAGG and DUSAGG are hosting Viking Rally in November 2021! Please come join us "
                   "for a weekend of great fun in the Toon and surrounding areas. Its a canny place to be! Find out "
                   "more about SSAGO's raid of the North East on the SSAGO Website -> https://viking-rally.ssago.org/")


@bot.command(name="credits", brief="My credits", help="Find out who makes me work (or not work!)")
async def _credits(ctx):
    print(f"*****\nCommand: credits\nCalled by: {ctx.author}")
    try:
        with open("data/contributors.txt", "r") as contributors_file:
            contributors = "\n".join(contributors_file.readline().replace(", ", ",").split(","))
        await ctx.send(f"I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. I have the following people"
                       f" to thank for my creation:\n>>> {contributors}")
    except FileNotFoundError:
        await ctx.send("I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. Unfortunately my memory's "
                       "currently a little fuzzy as to who made me.")


@bot.command(name="fact", brief="Get a seahorse fact", help="I'll provide one of my many facts about seahorses")
async def fact(ctx):
    print(f"*****\nCommand: fact\nCalled by: {ctx.author}")
    try:
        with open("data/facts.json", "r") as fact_file:
            facts = json.load(fact_file)
        single_fact = facts[str(random.choice(range(len(facts))))]
        await ctx.send(single_fact)
    except FileNotFoundError:
        await ctx.send("I don't seem to know any facts at the minute :tired_face:. Please try again later!")


@bot.command(name="joke", brief="Get a seahorse joke", help="I'll provide one of my many jokes about seahorses")
async def joke(ctx):
    print(f"*****\nCommand: joke\nCalled by: {ctx.author}")
    try:
        with open("data/jokes.json", "r") as joke_file:
            jokes = json.load(joke_file)
        single_joke = jokes[str(random.choice(range(len(jokes))))]
        await ctx.send(single_joke)
    except FileNotFoundError:
        await ctx.send("I don't seem to know any jokes at the minute :tired_face:. Please try again later!")


@bot.command(name="friend", brief="Befriend me", help="Ask about being my friend", aliases=["befriend"])
async def friend(ctx):
    print(f"*****\nCommand: friend\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as friends_file:
            line = friends_file.readline()
        multiple_friends = line.split(",")
        for single_friend in multiple_friends:
            friend_list.append(single_friend)
        print(friend_list)
        if str(ctx.author.id) in friend_list:
            await ctx.send(f"{ctx.author.mention} you're already my friend!")
        else:
            with open("data/friends.txt", "a") as friends_file:
                friends_file.write(f",{ctx.author.id}")
            await ctx.send(f"{ctx.author.mention} you're now my friend!")
    except FileNotFoundError:
        await ctx.send(f"My memory's a little fuzzy right now. Please try asking me again later!")


@bot.command(name="friends", brief="Friend list", help="Discover who I am friends with")
async def friends(ctx):
    print(f"*****\nCommand: friends\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as friends_file:
            line = friends_file.readline()
        multiple_friends = line.split(",")
        for single_friend in multiple_friends:
            if single_friend != '':
                friend_list.append(single_friend)
        print(friend_list)
        if len(friend_list) == 0:
            await ctx.send(f"Unfortunately I don't have any friends at the moment. {ctx.author.mention}, perhaps you "
                           f"could befriend me")
        else:
            friend_list_names = []
            for i in friend_list:
                if i != '':
                    name = bot.get_user(int(i)).name
                    friend_list_names.append(name)
            await ctx.send(f"My friends are:\n>>> {chr(10).join([i for i in friend_list_names])}")
    except FileNotFoundError:
        await ctx.send(f"My memory's a little fuzzy right now. Please try asking me again later!")


@bot.command(name="say", hidden=True, brief="Echoes what you say", help="Get Sally to say what you want her to say")
async def say(ctx, *, arg: str):
    print(f"*****\nCommand: say\nCalled by: {ctx.author}")
    await ctx.send(arg)


@bot.command(name="steal", brief="Try and steal me", help="You can try and steal me, but will you succeed?")
async def steal(ctx):
    print(f"*****\nCommand: steal\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as friends_file:
            line = friends_file.readline()
        multiple_friends = line.split(",")
        for single_friend in multiple_friends:
            if single_friend != '':
                friend_list.append(single_friend)
        # if a NUSSAGG member tries to steal
        if 692795798416523356 in [role.id for role in ctx.author.roles]:
            await ctx.send(f"{ctx.author.mention} you can't steal me, you're part of my club")
        # stops another mascot from stealing me
        elif 689416586515447885 in [role.id for role in ctx.author.roles] or 690193852061188141 in [role.id for role in
                                                                                                    ctx.author.roles]:
            await ctx.send(f"{ctx.author.mention} I think you've broken the laws of SSAGO physics.. how can one mascot "
                           f"steal another? Perhaps <@&689383534208614409> can weigh in on this one")
        # if a friend tries to steal, un-friend them
        elif str(ctx.author.id) in friend_list:
            friend_list.remove(str(ctx.author.id))
            with open("data/friends.txt", "w") as f:
                f.write(",".join(friend_list))
            await ctx.send(f"{ctx.author.mention} you were meant to be my friend")
        # if someone else tries to steal, they fail
        else:
            choice = random.choice(range(2))
            if choice == 0:
                await ctx.send("Better luck next time, I swam away")
            elif choice == 1:
                await ctx.send("Before you got to me, <@689751502700675072> pounced at you, saving me!")
    except FileNotFoundError:
        await ctx.send("Better luck next time, I swam away")


@bot.command(name="frequency", hidden=False, brief="Change how often I translate",
             help="Set the frequency of my translations. Set me to 0 to stop")
async def frequency(ctx, *arg):
    print(f"*****\nCommand: frequency\nCalled by: {ctx.author}")
    print(arg)
    global translator_frequency
    if len(arg) == 0:
        with open("data/translation_frequency.txt", "r") as freq:
            translator_frequency = int(freq.read())
        print(f"Translator frequency remains at: {translator_frequency}")
        if translator_frequency == 0:
            await ctx.send("I'm currently not translating")
        elif translator_frequency == 1:
            await ctx.send("I'm trying to translate every message!")
        else:
            await ctx.send(f"There's currently a 1 in {translator_frequency} chance of me translating a message")
    elif len(arg) == 1:
        try:
            translator_frequency = int(arg[0])
            with open("data/translation_frequency.txt", "w") as freq:
                freq.write(str(translator_frequency))
            print(f"Translator frequency set to: {translator_frequency}")
            if translator_frequency == 0:
                await ctx.send("I'll stop translating")
            elif translator_frequency == 1:
                await ctx.send("I'll try to translate every message!")
            else:
                await ctx.send(f"There's now a 1 in {translator_frequency} chance of me translating a message")
        except ValueError:
            await ctx.send("Sorry, I don't understand the number. Please try it like `@Sally the Seahorse frequency 10")
    else:
        await ctx.send("Sorry, I don't understand the number. Please try it like `@Sally the Seahorse frequency 10")


@bot.command(name="instagram", brief="Link to my Instagram", help="Get a link to mine and Leo's Instagram")
async def instagram(ctx):
    print(f"*****\nCommand: instagram\nCalled by: {ctx.author}")
    with ctx.channel.typing():
        # displays the latest instagram photo on Sally and Leo's profile
        insta = instaloader.Instaloader()
        insta.load_session_from_file("nussaggsallyandleo", ".insta_session")
        # insta.login("nussaggsallyandleo", INSTAGRAM_PASSWORD)  # curently using session file due to bug
        profile = instaloader.Profile.from_username(insta.context, "nussaggsallyandleo")
        posts = profile.get_posts()
        post = next(posts)
        print(post)
        image_path = "nussaggsallyandleo_latest_insta.jpg"
        if os.path.exists(image_path):
            os.remove(image_path)
        with open(image_path, "wb") as f:
            f.write(requests.get(post.url).content)
        await ctx.send(f"<@689751502700675072> and I are on Instagram; you can find us at "
                       f"https://www.instagram.com/nussaggsallyandleo/. As a taster, here's our latest pic...\n\n>>> "
                       f"{post.caption}",
                       file=discord.File(image_path))
    os.remove(image_path)


@bot.command(name="geordie", brief="Learn about some famous Geordies",
             help="I'll help teach you about some famous Geordies.")
async def geordie(ctx):
    print(f"*****\nCommand: geordie\nCalled by: {ctx.author}")
    try:
        with open("data/geordie.json", "r") as geordie_file:
            geordies = json.load(geordie_file)
        single_geordie = geordies[str(random.choice(range(len(geordies))))]
        embed = discord.Embed(title=single_geordie["name"], url=single_geordie["wiki"],
                              description=single_geordie["honours"], color=0x4fafe4)
        embed.set_thumbnail(url=single_geordie["image"])
        embed.add_field(name="Connection to Newcastle", value=single_geordie["connection"], inline=False)
        embed.add_field(name="Famous for?", value=single_geordie["fame"], inline=False)
        await ctx.send(embed=embed)
    except FileNotFoundError:
        await ctx.send("Ah divvint seem tuh knar any famous geordies at the minute :tired_face:. please try agyen "
                       "lator!\nOr, in plain English:\n>>> I don't seem to know any famous Geordies at the minute "
                       ":tired_face:. Please try again later!")


@bot.command(name="catch")
async def catch(ctx):
    with open("data/catch.json", "r") as catch_file:
        catchers = json.load(catch_file)
    if ctx.author.bot:
        print("Bot = True")
        await asyncio.sleep(random.randrange(2, 7))
    catcher = catchers[str(random.choice(range(len(catchers))))]
    timeout = time.time() + 10
    while time.time() < timeout:
        if int(catcher["id"]) in [member.id for member in ctx.guild.members if member.status == discord.Status.online]:
            break
        catcher = catchers[str(random.choice(range(len(catchers))))]
    await ctx.send(f"{ctx.author.mention}, I'm a seahorse, I don't have arms to catch a ball. I was however able to"
                   f" headbutt it over to <@{catcher['id']}> ...")
    if catcher.get("action") is not None:  # checks if bot requires an additional action to be able to catch
        await ctx.send(f"{catcher['action']}")


bot.remove_command("help")


@bot.command(name="help", invoke_without_command=True)
async def _help(ctx):
    print(f"*****\nCommand: help\nCalled by: {ctx.author}")
    embed = discord.Embed(title="Sally the Seahorse", url="https://github.com/trodaway/SallyBot",
                          description="Call me with `@Sally the Seahorse`", color=0x4fafe4)
    embed.set_thumbnail(url="https://ssago.org/img/clubs/logos/44.png")
    embed.add_field(name="Hi", value="Say hi to me and I'll say hi back", inline=False)
    embed.add_field(name="Leo", value="I'll talk about my best friend, Leo the Lion", inline=False)
    embed.add_field(name="Git", value="Get a link to the Github repository which contains all of my brains",
                    inline=False)
    embed.add_field(name="Rally", value="Yay, I get to talk about Viking Rally!", inline=False)
    embed.add_field(name="Credits", value="Find out who contributed to my creation", inline=False)
    embed.add_field(name="Fact", value="I've got lots of seahorse facts that I'd love to share", inline=False)
    embed.add_field(name="Joke", value="Get ready for a laugh as I tell you a seahorse joke", inline=False)
    embed.add_field(name="Friend", value="Ask about being my friend - I'm very friendly", inline=False)
    embed.add_field(name="Friends", value="Find out who I'm friends with", inline=False)
    embed.add_field(name="Steal", value="You could try to steal me, though it may not end well for you", inline=False)
    embed.add_field(name="Frequency <x>",
                    value="Set the frequency of my translator, so that I only have a 1 in x chance of translating. If I"
                          " really annoy you, feel free to stop me all together with 0.", inline=False)
    embed.add_field(name="Frequency", value="I'll tell you how often I'm translating messages currently", inline=False)
    embed.add_field(name="Instagram", value="Get a link to mine and Leo's insta - you'll even get a sneak peak out our "
                                            "latest adventures!", inline=False)
    embed.add_field(name="Geordie", value="Learn more about one of the many famous Geordies!", inline=False)
    embed.add_field(name="Catch", value="Throw a ball to me and I'll try to catch it", inline=False)
    embed.add_field(name="Say <x>", value="Get me to say <x>", inline=False)
    embed.add_field(name="Help", value="Access this help menu", inline=False)
    embed.add_field(name="Mute", value="Please only use if I'm broken and being a nuisance", inline=False)
    embed.set_footer(text="Any problems, please contact Tim Rodaway")
    await ctx.send(embed=embed)


@bot.command(name="mute")
async def mute(ctx):
    await ctx.send(f"<@689579955012632586>, I'm being silenced by {ctx.author.mention}")
    global silence
    silence = True


@bot.event
async def on_message(message):

    # reacts for the shrimp attack by Liam
    if message.guild and message.author.id == 150339580359475200 and \
            message.guild.get_role(692795753168634006) in message.author.roles:
        await message.add_reaction("🐬")
        await message.add_reaction("🪓")

    now = datetime.datetime.now().isoformat()

    ctx = await bot.get_context(message)

    # method of silencing if spamming
    global silence
    if silence:
        if message.author.id == 689579955012632586:  # only if creator messages
            if re.match(r"(?i)^<@[&!]?693216082567233667> (un-?(mute|silence)|resume|talk)$", message.content) is not \
                    None:
                silence = False
                await ctx.send("Yay - I can talk once more!")
            elif re.match(r"(?i)^<@[&!]?693216082567233667>", message.content) is not None:
                await ctx.send("I'm being quiet. You, and only you, can unmute me with the `unmute` command")
        elif re.match(r"(?i)^<@[&!]?693216082567233667>", message.content) is not None and not ctx.author.bot:
            await ctx.send("I'm being quiet. Please ask <@689579955012632586> to `unmute` me")
        return

    # print("*"*10, message.channel.id)

    if ctx.channel.type == discord.ChannelType.private:  # checks if message is a DM / Private Message
        guild = bot.get_guild(689381329535762446)  # gets SSAGO server
        role = guild.get_role(692795798416523356)  # gets NUSSAGG role
        if role in guild.get_member(ctx.author.id).roles:  # only allows NUSSAGG members / role holders past
            if message.author.bot:  # prevent a bot from triggering it, including self-triggering
                return
            elif len(message.attachments) > 0 and message.content == "Meme":
                for attachment in message.attachments:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status != 200:
                                return await message.channel.send("Could not download file...")
                            data = io.BytesIO(await resp.read())
                            channel = bot.get_channel(689401725005725709)  # SSAGO meme server
                            print(f"{now}: Sending Meme from {ctx.author.name}")
                            await channel.send(file=discord.File(data, os.path.basename(attachment.url)))
        return

    channel = message.channel

    # print(f"*****\nTimestamp: {now}\nContent: {message.content}\nAuthor: {message.author}\nAuthor ID: "
    #       f"{message.author.id}\nChannel: {channel.name}")

    # Added a NUSSAGG react and Meme Spork react to any memes a NUSSAGG member posts
    if (message.channel.id == 689401725005725709) and \
            (message.guild.get_role(699975448263786558) in message.author.roles) and (len(message.attachments) > 0):
        await message.add_reaction("<NUSSAGG:689608898239397888>")
        await message.add_reaction("<memespork:770733860308516924>")

    # stops it replying to itself
    if message.author == bot.user:
        # print(f"{now}: Trigger: It's me!")
        return

    elif message.content == "":
        # print(f"{now}: Trigger: No textual content in message")
        return

    # reacts to all of Leo's messages
    else:
        if message.author.id == 689751502700675072:
            print(f"{now}: Trigger: It's Leo!")

            if re.match("^Ro+a+r$", message.content) is not None:  # reacts to Leo's roars
                print("Trigger: Leo Roared")
                choice = random.choice(range(3))
                if choice == 0:
                    print("Response: argh")
                    count = message.content.count("o")
                    await channel.send(
                        f"{'a' * count + 'r' * int(count / 2) + 'g' * int(count / 2) + 'h' * int(count / 2)}")
                elif choice == 1:
                    with channel.typing():
                        print("Response: scream")
                        await channel.send(gif_response("scream"))
                        await channel.send(file=discord.File("imgs/GIPHY.gif"))
                else:
                    print("Response: shush")
                    await channel.send(":shushing_face:")

            # reacts to Leo protecting Sally
            elif re.match("(?i)^Glad I could help <@[!&]?693216082567233667>!$", message.content) is not None:
                await message.add_reaction(u"\U0001F618")

            elif re.match("(?i)^Sorry, I didn't quite understand that!", message.content) is not None:
                await message.add_reaction(u"\U0001F622")

            else:  # any of Leo's messages that aren't roars
                print("Trigger: add a reaction")
                try:
                    sally_emoji = "<:Sally:689616621576257557>"
                    await message.add_reaction(sally_emoji)  # only works on SSAGO server
                except discord.errors.HTTPException:
                    await message.add_reaction(u"\U0001F929")  # back-up, if not on the SSAGO server

        # translates every 'x' to geordie
        elif int(translator_frequency) != 0:  # set it to 0 to stop it from translating
            # print(f"Translator frequency: {translator_frequency}\tType: {type(translator_frequency)}")
            if random.randrange(int(translator_frequency)) == 0 and \
                    re.match("^<@[&!]?693216082567233667>.*$", message.content) is None and \
                    not (message.channel.category_id == 801588501841051689):
                print(f"{now}: Translating...")
                translated_text = translator(message.content)
                if translated_text is not None and not (translated_text.lower() == message.content.lower() or
                                                        translated_text.rstrip(".").lower() == message.content.lower()):
                    await channel.send(f"In the Toon we'd say that like:\n>>> {translated_text}")

    # print("Pre-regex")

    # Hi
    if re.match(r"(?i)^<@[&!]?693216082567233667> (hi|hello|hey|wye aye|aareet|alreet)[!.?]?$", message.content) is \
            not None:
        print(f"{now}: Regex- Hi")
        await hi(ctx)

    # Leo
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (<@[&!]?689751502700675072>|leo(( the)? lion)?)[!.?]?$",
                  message.content) is not None:
        print(f"{now}: Regex- Leo")
        await leo(ctx)

    # Git
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (git(hub)?|brains?)[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Git")
        await git(ctx)

    # Rally
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((viking|autumn( 2021)?|ssago) )?rally[!.?]?$", message.content) \
            is not None:
        print(f"{now}: Regex - Rally")
        await rally(ctx)

    # Credits
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (cred(it)?s?|contrib(utor)?s?)[!.?]?$", message.content) is not \
            None:
        print(f"{now}: Regex - Credits")
        await _credits(ctx)

    # Facts
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((sea[ -]?horse) )?facts?[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Facts")
        await fact(ctx)

    # Jokes
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((sea[ -]?horse) )?jokes?[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Jokes")
        await joke(ctx)

    # Friend
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (friend|befriend|(((let('s| us) be)|can we be|((do )?(yo)?u )?want "
                  "to be) friends?))[.!?]?$", message.content) is not None:
        print(f"{now}: Regex - Friend")
        await friend(ctx)

    # Friends
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((who are your )?friends|friends?[ -]?list|who are you friends "
                  r"with)[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Friends")
        await friends(ctx)

    # Steal
    elif re.match(r"(?i)^<@[&!]?693216082567233667> steal[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Steal")
        await steal(ctx)

    # Get Frequency
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (get )?(current )?((translat(e|or|ion)|geordie|geordie translat"
                  r"(e|or|ion)) )?freq(uency)?[!?.]?$",
                  message.content) is not None:
        print(f"{now}: Regex - Get Frequency")
        await frequency(ctx)

    # Set Frequency
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (set )?((translat(e|or|ion)|geordie|geordie translat(e|or|ion)) )?"
                  r"freq(uency)? \d+[!?.]?$",
                  message.content) is not None:
        print(f"{now}: Regex - Set Frequency")
        value = re.match(r"(?i)^<@[&!]?693216082567233667> (set )?((translat(e|or|ion)|geordie|geordie translat(e|or|"
                         r"ion)) )?freq(uency)? \d+[!?.]?",
                         message.content).string.split()[-1].rstrip("!?.")
        await frequency(ctx, value)

    # Instagram
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (instagram|insta|nussaggsallyandleo)[!.?]?$", message.content) is \
            not None:
        print(f"{now}: Regex - Insta")
        await instagram(ctx)

    # Geordie
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (famous )?geordie[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Geordie")
        await geordie(ctx)

    # Help
    elif re.match(r"(?i)^<@[&!]?693216082567233667> help[!.?]?$", message.content) is not None:
        print(f"{now}: Regex - Help")
        await _help(ctx)

    # Catch
    elif re.match(r"(?i)^(<@[&!]?693216082567233667> catch[!.?]?|I catch the ball in the air, and fly it straight back "
                  r"over to <@[&!]?693216082567233667>|(Rob|James) catches the ball, and throws it to "
                  r"<@[&!]?693216082567233667>|<@[&!]?\d+>, Freddo catches the ball, and throws it to "
                  r"<@[&!]?693216082567233667>, catch!|<@[&!]?\d+>, Morrissey's catches the ball, and throws it to "
                  r"<@[&!]?693216082567233667>, catch!)$", message.content) is not None:
        print(f"{now}: Regex - Catch")
        await catch(ctx)

    # Say
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (say|echo).*$", message.content) is not None:
        print(f"{now}: Regex - Say")
        words = re.match(r"(?i)^<@[&!]?693216082567233667> (say|echo) .*$", message.content).string.split(" ")[2:]
        value = " ".join(words)
        await say(ctx, arg=value)

    # Say
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (silence|mute|stop)$", message.content) is not None:
        print(f"{now}: Regex - Mute")
        await mute(ctx)

    # If tagged but no command
    elif re.match(r"(?i)^<@[&!]?693216082567233667>$", message.content) is not None:
        print(f"{now}: Tagged, but no command given")
        await ctx.send(f"Wye aye {ctx.author.mention}! Type `@Sally the Seahorse help` tuh learn warra gan dee.\nOr, in"
                       f" plain english:\n>>> Hi {ctx.author.mention}! Type `@Sally the Seahorse help` to learn what "
                       f"I can do.")

    # If being tagged in a catch, don't respond
    elif re.match(r"(?i)^<@[&!]?693216082567233667>, (Freddo|Morrissey's) catches the ball", message.content) \
            is not None:
        print(f"{now}: Tagged in a false positive catch")
        return

    # If an unknown command
    elif re.match(r"(?i)^<@[&!]?693216082567233667>.*$", message.content) is not None:
        await ctx.send(f"Soz {ctx.author.mention}, ah divvint understand that command. Type `@Sally the Seahorse help` "
                       f"tuh learn warra gan dee.\nOr, in plain english:\n>>> Sorry {ctx.author.mention}, I don't "
                       f"understand that command. Type `@Sally the Seahorse help` to learn what I can do.")
        print(f"{now}: Tagged in an unknown command\n{message.content}")

    else:
        return


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Soz {ctx.author.mention}, ah divvint understand that command. Type `@Sally the Seahorse help` "
                       f"tuh learn warra gan dee.\nOr, in plain english:\n>>> Sorry {ctx.author.mention}, I don't "
                       f"understand that command. Type `@Sally the Seahorse help` to learn what I can do.")
        return
    raise error


@bot.event
async def on_ready():
    print("I'm connected and ready to go!")
    await bot.get_user(689579955012632586).send("I'm up and running again! :wave:")
    global on_ready_flag
    if not on_ready_flag:
        bot.loop.create_task(status())  # sets custom statuses for the bot
        bot.loop.create_task(spotify())
        bot.loop.create_task(catch_auto())
        bot.loop.create_task(avatar_auto())
        on_ready_flag = True


bot.run(TOKEN)
