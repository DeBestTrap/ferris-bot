'''
A discord bot created with the sole purpose of handling 
polls for my server (and now other servers).

~ Tyler Chan
'''
import discord, asyncio, time, os
import dining_hall_data, poll_data
from discord.ext import commands, tasks
from dotenv import load_dotenv
from itertools import cycle

'''
Bot initialization
'''
load_dotenv()
TOKEN = os.getenv('FERRIS_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents,
        owner_ids={226854455478452236, 136906809699991552} )
poll_dict = dict()
servers_with_polls = dict()
dining_poll = dining_hall_data.dining_hall_data()

'''
-----===  Events and Tasks  ===-----
'''
@bot.event
async def on_ready():
  '''
  --- More Variables! ---
  type = 1:Playing 2:Listening 3:Watching 4:Custom (doesn't work?) 5:Competing in
  '''
  global activities; activities = cycle([
    discord.Activity(name='I am the poll bot!', type=3),
    discord.Activity(name='$help for help!', type=2)])
  global rpi_role; rpi_role = discord.utils.get(bot.get_guild(333409598365106176).roles, id=757454843341176844)
  # Test channel
  # global res_channel; res_channel = bot.get_channel(352591626092412931)

  # The channel for where the reservation polls are sent.
  global res_channel; res_channel = bot.get_channel(808165459920289812)
  '''
  --- Start tasks ---
  '''
  change_presence.start()
  print('Ready')

@tasks.loop(seconds=15)
async def change_presence():
  '''
  Change the bot's presence every 15 seconds.
  '''
  await bot.change_presence(activity=next(activities))

@bot.event
async def on_reaction_add(reaction, user):
  '''
  On a reaction add, check to see if the msg is an active poll.
  If so, add the reaction to the reaction dict of that poll.
  '''
  if (user.id == 823309830722551819):
    # Disregard the bot's own reactions.
    return
  '''
  Check to see if the message is an active poll.
  If so, add the reaction to the reaction dict of that poll.
  '''
  msg_id = reaction.message.id
  if (msg_id in poll_dict.keys()):
    msg, reactions, items = poll_dict[msg_id].return_all_var()
    await add_or_delete_reactions(reaction, user, msg, reactions, True)
  '''
  Check to see if the message is a dining hall poll.
  If so, add the reaction to the reaction dict of that poll.
  '''
  if (dining_poll.is_active and msg_id == dining_poll.msg.id):
    await add_or_delete_reactions(reaction, user, dining_poll.msg, dining_poll.reactions, True)

@bot.event
async def on_reaction_remove(reaction, user):
  '''
  On a reaction remove, check to see if the msg is an active poll.
  If so, remove the reaction in the reaction dict of that poll.
  '''
  if (user.id == 823309830722551819):
    # Disregard the bot's own reactions.
    return
  '''
  Check to see if the message is an active poll.
  If so, remove the reaction in the reaction dict of that poll.
  '''
  msg_id = reaction.message.id
  if (msg_id in poll_dict.keys()):
    msg, reactions, items = poll_dict[msg_id].return_all_var()
    await add_or_delete_reactions(reaction, user, msg, reactions, False)
  '''
  Check to see if the message is a dining hall poll.
  If so, remove the reaction in the reaction dict of that poll.
  '''
  if (dining_poll.is_active and msg_id == dining_poll.msg.id):
    await add_or_delete_reactions(reaction, user, dining_poll.msg, dining_poll.reactions, False)

'''
-----=== Commands  ===-----
'''
@bot.command(name='poll')
async def poll(ctx, *, args):
  '''
  Creates a poll that users can vote on.
  Only can create a poll with 10 items or less (will disregard items following the 10th).
  Usage:
    $poll [title];[arg1];[arg2];[arg3];...
    [title] : the title or question of the poll
    [arg1]  : choice 1
    [arg2]  : choice 2
    [arg3]  : choice 3
    ...
  Example:
    $poll Should we go to the movies today?;Yes;No
  '''
  global poll_dict 
  args_as_one_str = ''.join(args)
  if (args_as_one_str.find(';') == -1):
    # Poll doesn't have enough items to react to.
    await ctx.send('Put some items on the poll dummy.')
    return
  '''
  Creates a new poll.
  Send a message with the poll title add 
  the approprate number of reactions to the message.
  '''
  reactions = dict()
  items = args_as_one_str.split(';')
  msg = await ctx.send(f'{items[0]}')
  for i in range(len(items)):
    if i == 0:
      # The first item is the title, skip it.
      continue
    elif i == 11:
      # There is no emoji for 10, break the loop.
      break
    await msg.add_reaction(f'{i-1}️⃣')
    reactions[f'{i-1}️⃣'] = []
  poll_dict[msg.id] = poll_data.poll_data(msg, reactions, items)
  await edit_poll(msg.id)

@bot.command(name='pollend')
async def pollend(ctx):
  '''
  Send a message to ask the author what polls they want to end.
  React to the message to select which poll to end and hit
  the thumbs up emoji to confirm.
  Can only show 10 polls at a time.
  Usage:
    $pollend
  Example:
    Which poll would you like to end?
    1 Which movie for today?
    2 Who here is going bowling?
  '''

  '''
  Fetch all polls in the guild and store the messages in all_poll_msgs.
  '''
  guild_id = ctx.guild.id
  all_poll_msgs = []
  for poll in poll_dict.values():
    if poll.msg.guild.id == guild_id:
      all_poll_msgs.append(poll.msg)
  if (not all_poll_msgs):
    # Error: no polls in the guild to delete.
    await ctx.send("There aren't polls in this server dummy.")
    return
  '''
  Send message with all poll titles listed on it
  and add the approprate number of reactions to the message.
  '''
  text = 'Which poll would you like to end?\n'
  end_msg = await ctx.send(text)
  for i, msg in enumerate(all_poll_msgs):
    if i == 10:
      # There is no emoji for 10, break the loop.
      break
    await end_msg.add_reaction(f'{i}️⃣')
    text += '{}️⃣ {}\n'.format(i, msg.content.split("\n")[0])
  await end_msg.add_reaction('👍')
  await end_msg.edit(content=text)
  '''
  Wait for message author to "confirm" which polls to delete.
  '''
  answered = False 
  def check(reaction, user):
    nonlocal answered; answered = str(reaction.emoji) == '👍'
    return reaction.message == end_msg and user == ctx.author and (answered)
  await bot.wait_for('reaction_add', check=check)
  '''
  Fetch updated message and check reactions to see which polls were selected by the user.
  '''
  end_msg = await ctx.fetch_message(end_msg.id)
  removed_list = [0 for msg in all_poll_msgs]
  for i, reaction in enumerate(end_msg.reactions):
    if i == 10:
      # There is no emoji for 10, break the loop.
      break
    if (i != len(all_poll_msgs) and reaction.count > 1):
      removed_list[i] = 1
  '''
  Remove user selected polls from poll_dict, edit the poll message to
  show that the poll has ended, and send a new msg showing the results of the polls that were ended.
  '''
  for i, bool in enumerate(removed_list):
    if (bool):
      msg = all_poll_msgs[i]
      poll_dict.pop(msg.id)
      await msg.edit(content=msg.content+'\n\n**Poll ended.**')
      await ctx.send(f'**-= Results =-**\n{msg.content}')
  '''
  Edit the msg with how many polls were removed.
  '''
  await end_msg.edit(content=f'Ended {sum(removed_list)} polls.')

@bot.command(name='respoll')
async def respoll(ctx, res_type_arg, duration):
  '''
  Create a reservation poll specifically for deciding 
  which rpi dining hall to eat at.
  Usage:
    $respoll [type] [duration]
    [type]     : Breakfast, Lunch, Dinner
    [duration] : duration in minutes
  Example:
    $respoll dinner 30
  '''
  duration = float(duration)
  if (dining_poll.is_active):
    # If a poll is already active then notify the author and
    # delete the command msg and the notification msg after 5 seconds.
    msg = await ctx.send('Reservation poll already running!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await msg.delete()
  else:
    if (dining_poll.activate(res_type_arg)):
      # If the res_type_arg is valid, then continue making the reservation poll.
      msg = await res_channel.send(f'**{dining_poll.type} Reservation** {rpi_role.mention}\n')
      creation_time = time.localtime(time.time() + duration*60)
      emoji_list = [ discord.utils.get(bot.get_guild(333409598365106176).emojis, name=f'{hall}') 
                     for hall in dining_poll.halls ]
      dining_poll.add_info(msg, creation_time, emoji_list)
      for emoji in emoji_list:
        # Add the reactions to the message.
        await msg.add_reaction(emoji)
      await edit_poll(msg.id)
      await asyncio.sleep(duration*60)
      await respollend(None)
    else:
      await ctx.send(f'Unknown argument: {res_type_arg}')

@bot.command(name='respollend')
async def respollend(ctx):
  '''
  End the current reservation poll.
  Can be used to end the reservation poll before the duration is up.
  Usage:
    $respollend
  '''
  global dining_poll
  if (dining_poll.is_active):
    await res_channel.send(f'**-= Results =-**\n{dining_poll.msg.content}')
    await dining_poll.msg.delete()
    if ctx != None:
      await ctx.message.delete()
    dining_poll = dining_hall_data.dining_hall_data()
  else:
    # The reservation poll was already ended.
    if ctx != None:
      await ctx.send('The reservation poll ended already.')

@bot.command(name='quit', aliases=['shutdown'])
@commands.is_owner()
async def quit(ctx):
  '''
  Shuts down the bot.
  Usage: (must be an owner)
    $quit
  '''
  await ctx.message.delete()
  await ctx.bot.close()

'''
-----===  Helper Functions  ===-----
'''
async def add_or_delete_reactions(reaction, user, msg, reactions, add_bool):
  '''
  Helper function to add or remove the users to the reaction dict.
  Calls edit_poll to update the poll message with the new data.
  '''
  if reaction.message.id == msg.id:
    if not(reaction.emoji in reactions.keys()):
      return
    if add_bool:
      reactions[reaction.emoji].append(user.mention)
    else:
      reactions[reaction.emoji].remove(user.mention)
    await edit_poll(msg.id)

async def edit_poll(msg_id):
  '''
  Helper function to edit the poll msg with the the emojis, count, and people who reacted.
  Add all of the items with emojis, count, and people who reacted in the format:
    [emoji no.] [item] : [count] ([p1], [p2],...)
  '''
  if (msg_id in poll_dict.keys()):
    # If the poll is in poll_dict, then edit the poll msg with the most recent data.
    msg, reactions, items = poll_dict[msg_id].return_all_var()
    text = f'**{items[0]}**\n'
    for i in range(len(items)):
      if i == 0:
        # First item is the title, skip it.
        continue
      elif i == 11:
        # There is no emoji for 10, break the loop.
        break
      text += f'{i-1}️⃣ {items[i]} : {len(reactions[f"{i-1}️⃣"])} ({" ".join(reactions[f"{i-1}️⃣"])})\n'
    await msg.edit(content=text)
  if (dining_poll.is_active):
    # If the reservation poll is active, then edit the reservation poll msg most recent data.
    text = f'**{dining_poll.type} Reservation** {rpi_role.mention}\n' + '-='*12 + '-\n'
    text = dining_poll.add_emojis_to_text(text)
    await dining_poll.msg.edit(content=text) 

bot.run(TOKEN)