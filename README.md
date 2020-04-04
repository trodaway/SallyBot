# SallyBot
A discord bot for Sally the Seahorse - One of NUSSAGG's Mascots

## To setup
### Files that need adding
* `data/translation_frequency.txt`. This should simply contain a number, to keep the value consistent when reloading the bot
* `data/friends.txt`. This should contain a list of friends ID's, seperated by commas (no spaces). It will automatically populate, so you can just create a blank file, or pre-populate it with specific friends if you wish
* `.env`. This contains:
    * `DISCORD_TOKEN` available from [Discord's Developer Portal](https://discordapp.com/developers)
    * `GIPHY_TOKEN` available from [Giphy's Developer Portal](https://developers.giphy.com/)
    * `INSTAGRAM_PASSWORD` which is your standard Instagram Account's password
    
### Required libraries
`requirements.txt` contains the required libraries. All of these are available from pip.