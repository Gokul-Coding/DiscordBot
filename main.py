import os
import uuid
import asyncio
from discord import *
from dotenv import load_dotenv
from discord.ext import commands
import google.generativeai as ai
from datetime import datetime, timezone


#API Keys - to be safely stored
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ai_token = os.getenv('GEMINI_APIKEY')


ai.configure(api_key=ai_token)
model = ai.GenerativeModel("gemini-2.0-flash-lite")


intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

reminders = {}

async def send_reminder(reminder_id):
    global reminders
    try:
        if reminder_id in reminders:
            ctx, message, delay, _ = reminders[reminder_id]
            await asyncio.sleep(delay)

            if reminder_id in reminders:
                await ctx.send(f"⏰ Reminder for {ctx.author.mention}: {message}")
                del reminders[reminder_id]
    except asyncio.CancelledError:
        print(f"Reminder {reminder_id} was cancelled before execution")
    except KeyError:
        pass

@bot.command()
async def remind(ctx, date: str, time: str, *, message: str):
    global reminders
    try:
        date_time_str = f"{date} {time}"
        reminder_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

        reminder_time = reminder_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delay = (reminder_time - now).total_seconds()

        if delay <= 19800:
            await ctx.send("⏰ You can't set a reminder for the past! Please enter a future date and time.")
            return

        reminder_id = str(uuid.uuid4())[:8]
        task = bot.loop.create_task(send_reminder(reminder_id))

        reminders[reminder_id] = (ctx, message, delay-19800, task)

        await ctx.send(f"✅ Reminder set! ID: `{reminder_id}` (Triggers at {date_time_str})")

    except ValueError:
        await ctx.send("⚠️ Invalid date-time format! Use `YYYY-MM-DD HH:MM:SS` (e.g., `2025-03-06 15:30:00`).")

@bot.command()
async def remind_delete(ctx, reminder_id: str):
    global reminders
    if reminder_id in reminders:
        _, _, _, task = reminders[reminder_id]
        task.cancel()
        del reminders[reminder_id]
        await ctx.send(f"Reminder '{reminder_id}' deleted successfully!")
    else:
        await ctx.send(f"No reminder found with ID '{reminder_id}'")

@bot.command()
async def remind_modify(ctx, reminder_id: str, date: str, time : str, *,new_message: str):
    global reminders
    if reminder_id in reminders:
        _, _, _, task = reminders[reminder_id]
        task.cancel()
        new_task = bot.loop.create_task(send_reminder(reminder_id))

        date_time_str = f"{date} {time}"
        reminder_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

        reminder_time = reminder_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        new_time = (reminder_time - now).total_seconds() - 19800

        reminders[reminder_id] = (ctx, new_message, new_time, new_task)
        await ctx.send(f"Reminder '{reminder_id}' updated! New time: {new_time} seconds, New_message: {new_message}")
    else:
        await ctx.send(f"No reminder found with ID '{reminder_id}'")

#gemini apai info retrieving function
def get_gemini_response(user_input):
    try:
        response = model.generate_content(user_input)
        if response:
            return response.text
        else:
            return "I couldn't generate a response"
    except Exception as e:
        print(f"Gemini API Error : {e}")
        return "Sorry, I encountered an error"

#sends message to the group chat or else to the private chat
async  def send_message(message, user_msg) -> None:
    if not user_msg:
        print("Message was empty because intents were not enabled properly")
        return

    if is_private := user_msg[0] == '?':
        user_msg = user_msg[1:]

    try:
        #gets the response from gemini api
        response = get_gemini_response(user_msg)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)

@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("You must provide atleast 2 options!")
        return

    poll_msg = f"**{question}**\n\n"
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    if len(options) > len(reactions):
        await ctx.send("Polls can have maximum of 10 options!")
        return

    for i, option in enumerate(options):
        poll_msg += f"{reactions[i]} **{option}**\n"

    poll = await ctx.send(poll_msg)

    for i in range(len(options)):
        await poll.add_reaction(reactions[i])


#gets the msg and sends it in the terminal
@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    user_msg = message.content

    if user_msg.startswith("!"):
        await bot.process_commands(message)
        return

    print(f'[{str(message.channel)}] {str(message.author)}: "{message.content}"')
    await send_message(message, message.content)

#acknowledging the bot works
@bot.event
async def on_ready() -> None:
    await bot.tree.sync()
    print(f"{bot.user} is now running")

bot.run(TOKEN)

"""
Modes:

text normally - to use gemini api for reply
add '?' in front of your query - to use gemini api for reply but the reply falls to your DM instead of the group chat
command mode

Commands: <.....> - input

1)To CREATE a reminder
    syntax: !remind <date> <time> <message>
    example: in this format
    !remind 2025-03-05 12:01:10 Complete my project
    
2)To MODIFY a reminder
    syntax: !remind_modify <message_id> <new_date> <new_time> <new_message>
    example: in this format, message_id will be shown in chat as soon as a reminder is set
    !remind_modify 7cdfb296 2025-03-05 12:01:30 hi!
    
3)To DELETE a reminder
    syntax : !remind_delete <message_id>
    example: in this format
    !remind_delete d2519967
    
4)To CREATE a poll
    syntax: !poll "<message_to_be_appeared_for_poll>" <option_1> <option_2> ..... <option_10>
    the number of option has been capped to 10
    example: in this format
    !poll "Best number" 1 2 3 4 5 6 7 8 9 10
"""