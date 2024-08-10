import discord
import os
import logging
import random
from discord.ext import commands
from discord import FFmpegPCMAudio, ConnectionClosed, ClientException
import asyncio
from dotenv import load_dotenv
from pydub import AudioSegment
from song_titles import song_titles
from discord.ext import tasks
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.typing = False
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class NextCog(commands.Cog):
    def __init__(self, bot, voice_client):
        self.bot = bot
        self.voice_client = voice_client

    @commands.command()
    async def next(self, ctx):
        print("Next command triggered")
        voice_client = None
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.guild:
                voice_client = vc
                break

        if voice_client is None:
            print("Bot is not connected to a voice channel.")
            return

        try:
            voice_client.stop()
            print("Next song will play")
            await play_random_song()
            
        except Exception as e:
            print(f"Error occurred: {e}")

async def setup(bot, voice_client):
    cog = NextCog(bot, voice_client)
    bot.add_cog(cog)
    return cog

async def change_status():
    await bot.wait_until_ready()
    while not bot.is_closed():
        statuses = [
            discord.Game(name="TG!"),
            discord.Game(name="SUCE!"),
            discord.Game(name="MA BEUTEU???"),
            discord.Game(name="NON!"),
        ]
        for status in statuses:
            await bot.change_presence(activity=status)
            await asyncio.sleep(10)

audio_files = [file for file in os.listdir("songs") if file.endswith(".mp3")]
random.shuffle(audio_files)  
voice_client = None

playlist = []

song_titles = song_titles

@bot.event
async def on_ready():
    print(f"""
=============================================================
{bot.user.name} is damn connected !!
=============================================================          
""")
    change_bot_identity.start()
    send_private_message.start()
    global voice_client
    target_voice_channel_id = 1018098145420390410  
    target_voice_channel = bot.get_channel(target_voice_channel_id)
    bot.loop.create_task(change_status())
    if target_voice_channel:
        if voice_client is None or not hasattr(voice_client, 'is_connected') or not voice_client.is_connected():
            voice_client = await target_voice_channel.connect()
        print("Bot is connected to the voice channel and starting to play music.")
        await play_random_song()
    

bot_names = ["LE SOFTEUR", "LE PAGO", "LA BÊTE", "LA MOUCHE", "LE SUPPOSITOIRE", "LE COUPE-JARRET", 
             "LE NABUCHODONOSOR", "LA BULLE", "LA NOUILLE",  "LE PIED-BOUCHE", "LE CORBEAU", 
             "LE STRING", "L'EGIRL", "LE GOAT", "LE FRÈRE", 
             "LE NABOT", "LE MALOTRU", "L'ÉBOUEUR", "LA POUTRE", "LA FLAQUE"]
profile_pictures = ["./pics/09softeur.jpeg", "./pics/02pago.png", "./pics/05bete.png", "./pics/03mouche.jpeg",
                    "./pics/04suppositoire.jpeg", "./pics/06coupe-jarret.jpeg",
                    "./pics/nabu.png", 
                    "./pics/bulle.png", "./pics/nouille.png", "./pics/08pied-bouche.png", "./pics/corbeau.png", 
                    "./pics/00string.png", "./pics/egirl.jpeg",
                    "./pics/goat.jpeg", "./pics/frere.png", "./pics/07nabot.jpeg", 
                    "./pics/malotru.png", "./pics/eboueur.png", "./pics/poutre.jpeg", "./pics/flaque.png"]

current_index = 0

@tasks.loop(hours=6)
async def change_bot_identity():
    global current_index
    print("Starting the process to change bot's identity")
    new_name = bot_names[current_index]
    new_picture_path = profile_pictures[current_index]
    print(f"""
=============================================================
Selected new name: {new_name}
Selected new profile picture: {new_picture_path}
=============================================================
""")
    try:
        await bot.user.edit(username=new_name)
        print(f"""
=============================================================              
Bot name changed to {new_name}
=============================================================
""")
        with open(new_picture_path, 'rb') as img:
            image_data = img.read()
            await bot.user.edit(avatar=image_data)
            print("""
=============================================================                  
Bot profile picture changed successfully
=============================================================
""")
        current_index = (current_index + 1) % len(bot_names)
    except Exception as e:
        print(f"Error changing bot identity: {e}")


async def play_random_song():
    global voice_client
    ignored_user_id = 1161683957440589976
    channel_ids = [534010128773414926, 811683007290146858, 1018098145420390410, 880881683749015622,
                   530012749066010657, 534010172587114508, 1017001428524486686, 1150149299028635731, 1216106779138850976]
    text_channel_id = 1199479426497380423
    text_channel = bot.get_channel(text_channel_id)
    wait_channel_id = 1200530884831477841
    empty_channel_count = 0
    while True:
        try:
            if empty_channel_count >= 20:
                print("""
=============================================================
20 empty channels encountered. Disconnecting and waiting for 30 minutes.  
=============================================================
""")
                if voice_client:
                    await voice_client.disconnect()
                await asyncio.sleep(1800)
                empty_channel_count = 0
                continue
            target_voice_channel_id = random.choice(channel_ids)
            target_voice_channel = bot.get_channel(target_voice_channel_id)
            if voice_client:
                await voice_client.disconnect()
            voice_client = await target_voice_channel.connect()
            channel_members = [member for member in target_voice_channel.members if member.id != ignored_user_id and member != bot.user]
            if len(channel_members) == 0:
                print(f"""
=============================================================
Voice channel {target_voice_channel.name} is empty. Moving to the next channel.
=============================================================
""")
                empty_channel_count += 1
                continue
            else:
                empty_channel_count = 0
            print(f"""
=============================================================
Currently in voice channel: {target_voice_channel.name}
Members in voice channel: {[member.name for member in channel_members]}
=============================================================
""")
            audio_files = [file for file in os.listdir("songs") if file.endswith((".mp3", ".wav"))]
            if not audio_files:
                print("No more songs in the 'songs' directory.")
                break
            random.shuffle(audio_files)
            random_audio_file = audio_files.pop(0)
            print(f"""
=============================================================
Playing song: {random_audio_file}
=============================================================
""")
            audio_file_path = os.path.join("songs", random_audio_file)
            audio = AudioSegment.from_mp3(audio_file_path)
            audio_duration = len(audio) / 1000
            audio_source = FFmpegPCMAudio(executable="ffmpeg", source=audio_file_path)
            try:
                if not voice_client.is_playing():
                    voice_client.play(audio_source)
                    song_title = song_titles.get(random_audio_file, 'Unknown')
                    await text_channel.send(f'Vous écoutez désormais: {song_title}')
                else:
                    print("Bot is already playing.")
            except (ConnectionClosed, ClientException) as e:
                print(f"Error occurred: {e}")
                break
            await asyncio.sleep(audio_duration)
            print("""
=============================================================
Waiting for 10 minutes in the channel after playing the song.
=============================================================
""")
            await asyncio.sleep(600)
            wait_channel = bot.get_channel(wait_channel_id)
            if wait_channel:
                if voice_client:
                    await voice_client.disconnect()
                voice_client = await wait_channel.connect()
                print(f"""
=============================================================
Bot is in {wait_channel.name}. Waiting for 10 minutes.  
=============================================================
""")
                await asyncio.sleep(600)
        except discord.errors.ConnectionClosed as e:
            print(f"Disconnected from voice with error: {e}")
            print("Attempting to reconnect...")
            target_voice_channel_id = random.choice(channel_ids)
            target_voice_channel = bot.get_channel(target_voice_channel_id)
            voice_client = await target_voice_channel.connect()
            continue



user_ids = [530012026114670593, 1163037440852893756, 447164227321331715, 502900113040212019, 694257248532299881, 435469813951889408, 
            750289831719862334, 428264487754268672,
            211868111844933633, 332522721269383169, 256128167041957888, 720003437861011578, 404065631386992660, 539142544098066446,
            257458706738839553, 531874992141500416, 248855519035523085, 300368857346998287, 259364875770265600, ] 
messages = ["https://tenor.com/view/geneva-kitsui-koni-kitsui-koni-mountain-gif-98006767313222820",
            "👀",
            "https://drive.google.com/uc?id=1rmy6SojTegp5NkYMX_pohtwzZQm4zpHi&export=download",
            "Ouais de ouf",
            "https://tenor.com/view/pago-kitsui-koni-kitsui-koni-vcg-gif-5542109184676738895",
            "https://www.youtube.com/watch?v=r3edq2MiH3o&list=PLke_eeiQwDHNNPW2QwBKf8J4-rO59m6ha&index=8",
            "https://drive.google.com/uc?id=1K9XQK8fmIW1sKOwFWKzrln1QfgznnpxU&export=download",
            "https://drive.google.com/uc?id=1CJZj45lzULSR4qXq4Ls3uJANPMHro9_Q&export=download",
            ]
message_index = 0

@tasks.loop(seconds=40000) 
async def send_private_message():
    global message_index
    user_id = user_ids[message_index % len(user_ids)]
    user = await bot.fetch_user(user_id)
    if user:
        try:
            await user.send(messages[message_index])
            print(f"""
=============================================================
Sent '{messages[message_index]}' to {user_id}
=============================================================
""")
        except Exception as e:
            print(f"""
=============================================================
Failed to send message to {user_id}: {e}
=============================================================
""")
    message_index = 1 - message_index

@send_private_message.before_loop
async def before_send_private_message():
    print("Waiting for bot to be ready...")
    await bot.wait_until_ready()
    print("Starting to send private messages.")



bot_token = os.getenv("DISCORD_BOT_TOKEN")

async def run_bot():
    try:
        print("oui")
        
    except Exception as e:
        print(f"Error loading extension: {e}")

if __name__ == "__main__":
    try:
        bot.loop.run_until_complete(setup(bot, voice_client))
        bot.run(bot_token)
    except KeyboardInterrupt:
        if voice_client:
            voice_client.stop()
            voice_client.disconnect()
