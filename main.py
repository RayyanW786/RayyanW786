import discord
from discord.ext import commands
import pyrebase
import os 

intents  = discord.Intents.default()
intents.messages = True
intents.members = True

class DankTradesBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('r!','r!'),intents = intents, case_insensitive=True)
        self.has_started = False
        self.db = False
        
    async def on_ready(self):
        if not self.db: #this firebase account was specifically made for dank trades highlight only
            firebaseConfig = {
  'apiKey': "AIzaSyC5qcWcNvU0n_QVfQ_TgUmVJAYKZIXMoto",
  'authDomain': "fir-db-fe8ff.firebaseapp.com",
  'databaseURL': "https://fir-db-fe8ff-default-rtdb.firebaseio.com",
  'projectId': "fir-db-fe8ff",
  'storageBucket': "fir-db-fe8ff.appspot.com",
  'messagingSenderId': "1029362686584",
  'appId': "1:1029362686584:web:e35177d819a44ffd0e6b8d",
  'measurementId': "G-QQY8VNH1RT"
}

            firebase = pyrebase.initialize_app(firebaseConfig)
            self.db = firebase.database()

            
        if not self.has_started:
            print(f'Logged in as {self.user} (ID: {self.user.id})')
            print('------')
            await load_all_cogs()
            self.has_added = True

      
    
bot = DankTradesBot()
bot.owner_ids = [613752401878450176, 422967413295022080] #ray, abc (doesnt really matter as we only have one owner command)

@bot.event
async def on_command_error(ctx, error):
    pass #basically ignoring all command errors   

async def load_all_cogs():
    await bot.wait_until_ready()
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
            except commands.errors.NoEntryPointError as e:
                print(e)

class MyNewHelp(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		for page in self.paginator.pages:
			emby = discord.Embed(description=page, colour = 0x2f3136).set_footer(text = "made by Ray786 (613752401878450176)")
			await destination.send(embed=emby)

	async def send_error_message(self, error):
		embed = discord.Embed(title="Error", description=error, colour= 0x2f3136)
		channel = self.get_destination()
		await channel.send(embed=embed)


bot.help_command = MyNewHelp()
bot.remove_command("help")
bot.run("") #enter the bots token here 