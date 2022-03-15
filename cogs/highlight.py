import discord
from discord.ext import commands
import datetime
from typing import Optional, Union

def add_word(bot, text, author):
  data = bot.db.child("highlight").get().val()
  
  for element in data:
    if str(element) == str(text):
      users = data[element]
      newlist = users
      if author.id in users:
        break
      else:
        newlist.append(author.id) 
        data[element] = newlist
        break
  else:
    data[str(text)] = [author.id]
  
  bot.db.child("highlight").set(data)

def remove_word(bot, text, author):
  data = bot.db.child("highlight").get().val()
  
  for element in data:
    if str(element) == str(text):
      users = data[element]
      if author.id in users:
        users.remove(author.id)
        if users != None:
         data[element] = users
        else:
          data[element] = []
        break
  else:
    return "your not tracking this word!"
  
  
  bot.db.child("highlight").set(data)

def show_list(bot, author):
  data = bot.db.child("highlight").get().val()
  
  words = []
  for element in data:
    users = data[element]
    if author.id in users:
      words.append(str(element))
  
  return words

def channel_block(bot, author, channels):
  channels_id = [c.id for c in channels]
  data = bot.db.child("block").get().val()
  
  try:
      datachans = data[str(author.id)]["chans"]
  except:
      datachans = None
      #data[str(author.id)] = {}
      #data[str(author.id)]["chans"] = channels_id
      #joined = "\n".join([c.mention for c in channels])
      bot.db.child("block").child(str(author.id)).child("chans").set(channels_id)
      return channels_id
  if datachans:
      newlist = datachans
      for cid in channels_id:
          if not cid in datachans:
              newlist.append(cid)
          else:
            newlist.remove(cid)    
      #joined = ""
      #for chan in channels:
      #    if chan.id in newlist:
      #        joined += f"\n {chan.mention}"
      #data[str(author.id)]["chans"] = newlist
      #print(data)
      bot.db.child("block").child(str(author.id)).child("chans").set(newlist) 
      return newlist        
  
def user_block(bot, author, users):
  users_id = [u.id for u in users]
  data = bot.db.child("block").get().val()
  
  try:
      datausers = data[str(author.id)]["users"]
  except:
      datausers = None
      #data[str(author.id)] = {}
      #data[str(author.id)]["users"] = users_id
      #joined = "\n".join([u.mention for u in users])
      bot.db.child("block").child(str(author.id)).child("users").set(users_id)
      return users_id
  if datausers:
      newlist = datausers
      for cid in users_id:
          if not cid in datausers:
              newlist.append(cid)
          else:
            newlist.remove(cid)    
      #data[str(author.id)]["users"] = newlist
      bot.db.child("block").child(str(author.id)).child("users").set(newlist) 
      return newlist                 

def editroles(bot, roles):
  roles_id = [r.id for r in roles]
  data = bot.db.child("allowed").get().val()
  if data == None:
    bot.db.child("allowed").set(roles_id)
    return roles_id
  else:
    newlist = data
    for rid in roles_id:
      if not rid in data:
        newlist.append(rid)
      else:
        newlist.remove(rid)

    bot.db.child("allowed").set(newlist)
    return newlist       



def mycheck():
  def predicate(ctx):
    return ctx.guild.id == 941056850386890842 and [r for r in [r.id for r in ctx.author.roles] if r in ctx.bot.db.child("allowed").get().val()] != []
        
  return commands.check(predicate)

class highlight(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  
  @commands.group(case_insensitive = False, invoke_without_command = True, aliases = ["hl"])
  async def highlight(self, ctx):
   await ctx.send_help("hl")

  
  @highlight.command(name = "add", useage = "[exact = False] <word>", help = "add a word to track!", aliases = ["+"])
  @commands.guild_only()
  @mycheck()
  async def _add(self, ctx, exact : Optional[bool] = False, *, word):
    if len(word) > 20:
      return await ctx.send("your highlight has to be less than a length of 20 characters")
    if exact == True:
      word = f" {word} "
    try:
      add_word(self.bot, word, ctx.author)
      await ctx.reply(f"added {word} to your highlight list", allowed_mentions=discord.AllowedMentions(roles=False, everyone = False, users=False))
    except Exception as e:
     await ctx.reply(f"an error occurred:\n{e}")
  
  @highlight.command(name = "remove", useage = "[exact = False] <word>", help = "removes a word from your tracking list!", aliases = ["-"])
  @commands.guild_only()
  @mycheck()
  async def _remove(self, ctx,exact: Optional[bool] = False, *, word):
    if len(word) > 20:
      return await ctx.send("your highlight has to be less than a length of 20 characters")
    if exact == True:
      word = f" {word} "
    try:
      rt = remove_word(self.bot, word, ctx.author)
      if rt == "your not tracking this word!":
        return await ctx.reply("your not tracking this word!")
      await ctx.reply(f"removed {word} from your highlight list", allowed_mentions=discord.AllowedMentions(roles=False, everyone = False, users=False))
    except Exception as e:
      await ctx.reply(f"an error occured:\n{e}")
  
  @highlight.command(name = "show", help = "shows your currently tracking list", aliases = ["list"])
  @commands.guild_only()
  async def _show(self, ctx):
    try:
      words = show_list(self.bot, ctx.author)
      if words != []:
       string = "\n".join(words)
      else:
        return await ctx.reply("You're not tracking any words yet, use `r!highlight add <word>` to start tracking")
      embed = discord.Embed(title = "You're currently tracking the following words", description = string, colour = discord.Colour.random()).set_footer(text = "made by Ray786 (613752401878450176)")
      await ctx.send(embed = embed)
    except Exception as e:
      await ctx.reply(f"an error occured:\n{e}")
    
  @highlight.command(name = "block", help = "Messages sent in this channel/from this user won't notify you can select many channels and or members with the same command", aliases = ["ignore"])
  @commands.guild_only()
  @mycheck()
  async def _block(self, ctx, blocks: commands.Greedy[Union[discord.User, discord.TextChannel]]):
      #if blocks == []:
      #    return await ctx.send("list here")
      users = []
      channels = []
      for block in blocks:
          if isinstance(block, discord.User):
              users.append(block)
          if isinstance(block, discord.TextChannel):
              channels.append(block)     
      lst_of_chans = channel_block(self.bot, ctx.author, channels)      
      lst_of_users = user_block(self.bot, ctx.author, users)

      if lst_of_chans == [] and lst_of_users == []:
          return await ctx.send("You\'re not ignoring anything")
      #await ctx.send(f"{lst_of_chans}") #\n\n{lst_of_users}")
      else:
        lst_of_chans = [ctx.guild.get_channel(c) for c in lst_of_chans]
        lst_of_chans = "\n".join([c.mention for c in lst_of_chans])
        lst_of_users = [ctx.guild.get_member(u) for u in lst_of_users]
        lst_of_users = "\n".join([u.mention for u in lst_of_users])    
      em = discord.Embed().set_footer(text = "made by Ray786 (613752401878450176)")
      em.title = "**Your Current Ignores**"
      if lst_of_chans != "":
          em.add_field(name = "**channels**", value = lst_of_chans)
      if lst_of_users != "":
          em.add_field(name = "**Members**", value = lst_of_users)    
      await ctx.send(embed = em)  

  @highlight.command(name = "clear")
  @commands.guild_only()
  async def _clear(self, ctx):
    author = ctx.author
    data = self.bot.db.child("highlight").get().val()
    for element in data:
      users = data[element]
      if author.id in users:
        users.remove(author.id)
        self.bot.db.child("highlight").child(element).set(users)
    

    await ctx.send("removed all your highlights")

  @highlight.command(name = "roles", aliases = ["r"], help = "set the roles which can use this cog!")
  @commands.guild_only()
  @commands.is_owner()
  async def _roles(self, ctx, roles: commands.Greedy[discord.Role]):
    lst = editroles(self.bot, roles)
    if lst == []:
      return await ctx.send("no roles have been set!")
    else:
      lst = [ctx.guild.get_role(r).mention for r in lst]
      lst = "\n".join(lst)
      em = discord.Embed().set_footer(text = "made by Ray786 (613752401878450176)")
      em.title = "**your current roles**"
      em.add_field(name = "**roles**", value = lst)
      await ctx.send(embed = em)
  
  @highlight.command(name = "help", aliases = ["h"], help = "the help cmd for this cog")
  @commands.guild_only()
  async def _help(self, ctx, *, subcommand = None):
    if subcommand:
     await ctx.send_help(f"hl {subcommand}")
    else:
      await ctx.send("hl") 
  @commands.Cog.listener()
  async def on_message(self, message):
    if message.guild == None:
      return
    if message.guild.id != 941056850386890842:
      return
    if message.author.bot == True:
      return
    msg = message.content.lower()
    data = self.bot.db.child("highlight").get().val()
    

    for element in data:
      my_msg = element[1:-1]
      if str(element).lower() in msg:    
        users = data[element]
        if users == []:
          continue
        members = [message.guild.get_member(u) for u in users if u != None]
        message_lst = []

        async for messagevar in message.channel.history(limit=5):
          message_lst.append(messagevar)

        messages = [f"<t:{int(m.created_at.timestamp())}> **{m.author}**: {m.content}" for m in message_lst]
        end_result = "\n".join(reversed(messages))
        embed = discord.Embed(title = str(element), description = end_result, colour = discord.Colour.random())
        embed.add_field(name = "Source message", value = f"[jump to]({message.jump_url})")
        embed.set_footer(text = "made by Ray786 (613752401878450176) | Triggered")
        embed.timestamp = datetime.datetime.now()

        for mem in members:
          if mem == None:
              continue  
          #print([m.author for m in message_lst])
          if mem == message.author or mem.id in [m.author.id for m in message_lst]:
            pass
          else:
           if not message.channel.permissions_for(mem).view_channel:
             continue
           try:
            blocks = self.bot.db.child("block").get().val()[str(mem.id)]
            if message.channel.id in blocks['chans']:# or message.author.id in blocks['users']:
             continue
           except:
             pass
           try:
             if message.author.id in blocks['users']:
               continue
           except:
             pass    
           try:
            await mem.send(f"in **{message.guild}** {message.channel.mention}, you were mentioned with highlight word \"{element}\"",embed = embed)
           except:
             continue
      
      elif element.startswith(" ") and element.endswith(" ") and msg.startswith(f"{my_msg.lower()} "):
        users = data[element]
        if users == []:
          continue
        members = [message.guild.get_member(u) for u in users if u != None]
        message_lst = []

        async for messagevar in message.channel.history(limit=5):
          message_lst.append(messagevar)

        messages = [f"<t:{int(m.created_at.timestamp())}> **{m.author}**: {m.content}" for m in message_lst]
        end_result = "\n".join(reversed(messages))
        embed = discord.Embed(title = str(element), description = end_result, colour = discord.Colour.random())
        embed.add_field(name = "Source message", value = f"[jump to]({message.jump_url})")
        embed.set_footer(text = "made by Ray786 (613752401878450176) | Triggered")
        embed.timestamp = datetime.datetime.now()

        for mem in members:
          if mem == None:
              continue   
          if mem == message.author or mem.id in [m.author.id for m in message_lst]:
            pass
          else:
           if not message.channel.permissions_for(mem).view_channel:
             continue
           try:
            blocks = self.bot.db.child("block").get().val()[str(mem.id)]
            if message.channel.id in blocks['chans']:# or message.author.id in blocks['users']:
             continue
           except:
             pass
           try:
             if message.author.id in blocks['users']:
               continue
           except:
             pass
           try:
            await mem.send(f"in **{message.guild}** {message.channel.mention}, you were mentioned with highlight word \"{element}\"",embed = embed)
           except:
             continue
      elif msg.endswith(element[len(element)-2:-1]) and str(element).lower()[:-1] in msg and str(element).endswith(" "):
        users = data[element]
        if users == []:
          continue
        members = [message.guild.get_member(u) for u in users if u != None]
        message_lst = []

        async for messagevar in message.channel.history(limit=5):
          message_lst.append(messagevar)

        messages = [f"<t:{int(m.created_at.timestamp())}> **{m.author}**: {m.content}" for m in message_lst]
        end_result = "\n".join(reversed(messages))
        embed = discord.Embed(title = str(element), description = end_result, colour = discord.Colour.random())
        embed.add_field(name = "Source message", value = f"[jump to]({message.jump_url})")
        embed.set_footer(text = "made by Ray786 (613752401878450176) | Triggered")
        embed.timestamp = datetime.datetime.now()

        for mem in members:
          if mem == None:
              continue   
          if mem == message.author or mem.id in [m.author.id for m in message_lst]:
            pass
          else:
           if not message.channel.permissions_for(mem).view_channel:
             continue
           try:
            blocks = self.bot.db.child("block").get().val()[str(mem.id)]
            if message.channel.id in blocks['chans']:# or message.author.id in blocks['users']:
             continue
           except:
             pass
           try:
             if message.author.id in blocks['users']:
               continue
           except:
             pass    
           try:
            await mem.send(f"in **{message.guild}** {message.channel.mention}, you were mentioned with highlight word \"{element}\"",embed = embed)
           except:
             continue


      elif str(element).lower()[1:-1] == msg and str(element).endswith(" "):
        users = data[element]
        if users == []:
          continue
        members = [message.guild.get_member(u) for u in users if u != None]
        message_lst = []

        async for messagevar in message.channel.history(limit=5):
          message_lst.append(messagevar)

        messages = [f"<t:{int(m.created_at.timestamp())}> **{m.author}**: {m.content}" for m in message_lst]
        end_result = "\n".join(reversed(messages))
        embed = discord.Embed(title = str(element), description = end_result, colour = discord.Colour.random())
        embed.add_field(name = "Source message", value = f"[jump to]({message.jump_url})")
        embed.set_footer(text = "made by Ray786 (613752401878450176) | Triggered")
        embed.timestamp = datetime.datetime.now()
        for mem in members:
          if mem == None:
              continue 

          if mem == message.author or mem.id in [m.author.id for m in message_lst]:
            pass

          else:
           if not message.channel.permissions_for(mem).view_channel:
             continue
           try:
            blocks = self.bot.db.child("block").get().val()[str(mem.id)]
            if message.channel.id in blocks['chans']:# or message.author.id in blocks['users']:
             continue
           except:
             pass
           try:
             if message.author.id in blocks['users']:
               continue
           except:
             pass    
           try:
            await mem.send(f"in **{message.guild}** {message.channel.mention}, you were mentioned with highlight word \"{element}\"",embed = embed)
           except:
            continue
  


  


def setup(bot):
  bot.add_cog(highlight(bot))