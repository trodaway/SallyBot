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
import string

os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GIPHY_TOKEN = os.getenv("GIPHY_TOKEN")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


# USEFUL FUNCTIONS
def case(message, response):
    if message.isupper():
        return response.upper()
    elif message.islower():
        return response.lower()
    elif message.replace("'m", "").replace("'s", "").istitle():  # handles contractions
        return response.title().replace("'M", "'m").replace("'S", "'s")
    else:
        return string.capwords(response, sep=" ")


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
bot = commands.Bot(command_prefix=commands.when_mentioned_or(), case_insensitive=True)


@bot.event
async def on_ready():
    print("I'm connected and ready to go!")


@bot.command(name="hi", brief="I'll say hi", description="Say hi to me and I'll say hi back")
async def hi(ctx):
    print(f"*****\nCommand: hi\nCalled by: {ctx.author}")
    await ctx.send(f'Hi {ctx.author.mention}!')


@bot.command(name="leo", brief="I'll talk about Leo", description="Leo is my best friend, let's talk about him!")
async def leo(ctx):
    print(f"*****\nCommand: leo\nCalled by: {ctx.author}")
    await ctx.send("Leo is my Best Friend! We go on all our adventures together but he has to protect me, as other "
                   "SSAGO-ers like to steal me! :frowning:")


@bot.command(name="git", brief="Link to my Git repo", description="Get a link to the magic code behind me")
async def git(ctx):
    print(f"*****\nCommand: git\nCalled by: {ctx.author}")
    await ctx.send("Here's the git repo that contains all my inner code. I may look like the best teddy Seahorse you've"
                   " ever seen but there's a computer behind me!\nhttps://github.com/trodaway/SallyBot")


@bot.command(name="rally", brief="I'll talk about Viking Rally", description="Find out more about Viking Rally")
async def rally(ctx):
    print(f"*****\nCommand: rally\nCalled by: {ctx.author}")
    await ctx.send("My friends from NUSSAGG and DUSAGG are hosting Viking Rally in November 2021! Please come join us "
                   "for a weekend of great fun in the Toon and surrounding areas. Its a canny place to be!")


@bot.command(name="credits", brief="My credits", description="Find out who makes me work (or not work!)")
async def _credits(ctx):
    print(f"*****\nCommand: credits\nCalled by: {ctx.author}")
    try:
        with open("data/contributors.txt", "r") as file:
            contributors = "\n".join(file.readline().replace(", ", ",").split(","))
            await ctx.send(f"I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. I have the following "
                           f"people to thank for my creation:\n>>> {contributors}")
    except FileNotFoundError:
        await ctx.send("I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. Unfortunately my memory's "
                       "currently a little fuzzy as to who made me.")


@bot.command(name="fact", brief="Get a seahorse fact", description="I'll provide one of my many facts about seahorses")
async def fact(ctx):
    print(f"*****\nCommand: fact\nCalled by: {ctx.author}")
    try:
        with open("data/facts.json", "r") as file:
            facts = load(file)
            single_fact = facts[str(random.choice(range(len(facts))))]
            await ctx.send(single_fact)
    except FileNotFoundError:
        await ctx.send("I don't seem to know any facts at the minute :tired_face:. Please try again later!")


@bot.command(name="can I be your friend?", breif="Befriend me", description="Ask about being my friend")
async def friend(ctx):
    print(f"*****\nCommand: can I be your friend?\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as file:
            line = file.readline()
            friends = line.split(",")
            for single_friend in friends:
                friend_list.append(single_friend)
        print(friend_list)
        if ctx.author.id in friend_list:
            await ctx.send(f"{ctx.author.mention} you're already my friend!")
        else:
            with open("data/friends.txt", "a") as file:
                file.write(f",{ctx.author.id}")
            await ctx.send(f"{ctx.author.mention} you're now my friend!")
    except FileNotFoundError:
        await ctx.send(f"My memory's a little fuzzy right now. Please try asking me again later!")


@bot.command(name="steal", brief="Try and steal me", description="You can try and steal me, but will you succeed?")
async def steal(ctx):
    print(f"*****\nCommand: steal\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as f:
            line = f.readline()
            friends = line.split(",")
            for single_friend in friends:
                friend_list.append(single_friend)
        # if a NUSSAGG member tries to steal
        if ctx.author.roles.id == "692795798416523356":
            await ctx.send(f"{ctx.author.mention} you can't steal me, you're part of my club")
        # if a friend tries to steal, un-friend them
        elif ctx.author.id in friend_list:
            friend_list.remove(ctx.author.id)
            with open("data/friend.txt", "w") as f:
                f.write(",".join(friend_list))
            await ctx.send(f"{ctx.author.mention} you were meant to be my friend")
        # if someone else tries to steal, they fail
        else:
            await ctx.send("Better luck next time, I swam away")
    except FileNotFoundError:
        await ctx.send("Better luck next time, I swam away")


@bot.command(name="instagram", brief="Link to my Instagram", description="Get a link to mine and Leo's Instagram")
async def instagram(ctx):
    print(f"*****\nCommand: instagram\nCalled by: {ctx.author}")
    with ctx.channel.typing():
        # displays the latest instagram photo on Sally and Leo's profile
        insta = instaloader.Instaloader()
        insta.login("nussaggsallyandleo", INSTAGRAM_PASSWORD)
        profile = instaloader.Profile.from_username(insta.context, "nussaggsallyandleo")
        posts = profile.get_posts()
        post = next(posts)
        image_path = "nussaggsallyandleo_latest_insta.jpg"
        if os.path.exists(image_path):
            os.remove(image_path)
        with open(image_path, "wb") as f:
            f.write(requests.get(post.url).content)
        await ctx.send("<@689751502700675072> and I are on Instagram; you can find us at "
                       "https://www.instagram.com/nussaggsallyandleo/. As a taster, here's our latest pic...",
                       file=discord.File(image_path))
    os.remove(image_path)


@bot.event
async def on_message(message):
    channel = message.channel
    print(f"*****\nContent: {message.content}\nAuthor: {message.author}\nAuthor ID: {message.author.id}")

    # stops it replying to itself
    if (message.author == bot.user) or (message.content == ""):
        print("Trigger: It's me!")
        await bot.process_commands(message)
        
    else:
        # reacts to all of Leo's messages
        # if message.author.id == 689751502700675072:
        #     print("Trigger: It's Leo!")
        #     with channel.typing():
        #         try:
        #             await message.add_reaction("<:Sally:689616621576257557>")  # only works on SSAGO server
        #         except discord.errors.HTTPException:
        #             await message.add_reaction(":star_struck:")  # back-up, if not on the SSAGO server
    
        # responds to Leo's Roars
        if message.author.id == 689751502700675072 and match("^Ro+a+r$", message.content) is not None:
            print("Trigger: Leo Roared")
            with channel.typing():
                choice = random.choice(range(3))
                if choice == 0:
                    count = message.cotent.count("o")
                    await channel.send(f"{'a' * count + 'r' * int(count/2) + 'g' * int(count/2) + 'h' * int(count/2)}")
                elif choice == 1:
                    await channel.send(gif_response("scream"))
                else:
                    await channel.send(":shushing_face:")

        # Geordie Translations
        # special case for "no"
        elif message.content.lower() == "no":
            print("Trigger: Translation special case - no")
            with channel.typing():
                await channel.send(case(message, "nar"))
    
        # special case for "good"
        elif message.content.lower() == "good":
            print("Trigger: Translation special case - good")
            await channel.send(f"In the Toon we'd say that like:\n>>> {case(message.content, 'canny good like')}")
    
        # special case for "yes"
        elif message.content.lower() == "yes":
            print("Trigger: Translation special case - yes")
            await channel.send(f"In the Toon we'd say that like:\n>>> {case(message.content, 'whey aye man')}")
    
        # special case for "really good"
        elif message.content.lower() == "really good":
            print("Trigger: Translation special case - really good")
            await channel.send(f"In the Toon we'd say that like:\n>>> {case(message.content, 'purely belta')}")

        # normal translations
        else:
            with open("data/geordie.json", "r") as f:
                translations = load(f)
                msg = message.content.split(" ")
                """
                j = len(msg)
                while j > 0:
                    for i in range(len(msg)+1):
                        if i < j:
                            print(" ".join(msg[i:j]))
                    j += 1
                """
                keys = [key.lower() for key in translations.keys()]
                if any(x in keys for x in msg):
                    print(f"Trigger: We've a translation on our hands.. {msg}")
                    with channel.typing():
                        new_words = []
                        for word in msg:
                            print(f"Word: {word}")
                            if word in keys:
                                print("Found a translation")
                                new_word = translations[word]
                                new_words.append(case(word, new_word))
                            else:
                                print("Not found a translation")
                                new_words.append(word)
                            print(new_words)
                        new_msg = " ".join(new_words)
                        print(new_msg)
                        await channel.send(f"In the Toon we'd say that like:\n>>> {new_msg}")

        await bot.process_commands(message)
    
bot.run(TOKEN)
