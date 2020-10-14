# bot.py
import os

import discord
import asyncio
import random
import dotenv
from discord.ext import commands
from enum import Enum
from dotenv import load_dotenv


class Player:
    def __init__(self, name):
        self.name = name
        self.notoriety = 0 
        self.supportLevel = 0
        self.made_action_this_turn = False
    
    def get_stats(self):
        return [self.notoriety, self.supportLevel]

    def ToString(self):
        return self.name + "\nNotoriety: " + str(self.notoriety) + "\nSupportLevel: " + str(self.supportLevel) + "\n\n" 

class RoundPhase(Enum):
    PRE_ROUND = 0
    ROUND = 1
    POST_ROUND = 2


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, 'token.env'))

names = ["p1","p2","p3","p4","p5","p6","p7"]

TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!')


client = discord.Client()


game_started = False
joining_phase = True
number_of_players = 0
current_players = []
current_round_phase = RoundPhase.PRE_ROUND
round_messgaes_sent = [False, False, False]
actionsMade = 0
winner = ""


@bot.command(name='Mob', help="Welcome to the Mob ladies and gents. The game is simple: ya gotta rise to the top ranks of the mob, but to do so, ya gotta choose how to help out and choose who to rat out. There's only room for one wiseguy at the top of this mob!\nCommands:\n !Mob Start: Starts the joining phase of the game.\n !Mob JoinGame: The sender joins the game.\n!Mob LockJoin: ends the joining phase and the game begins.")
async def run_duel(ctx, action, user = None):
    global game_started
    global current_players
    global joining_phase
    global current_round_phase
    global actionsMade
    global round_messgaes_sent
    command_list = ["snitch", "support", "pass"]

    if action.lower() == "reset":
        game_started = False
        current_players = 0
        joining_phase = True
        current_round_phase = RoundPhase.PRE_ROUND
        actionsMade = 0
        round_messgaes_sent = [False, False, False]
        return 
    if action.lower() == "help":
        await ctx.send("```Welcome to the Mob ladies and gents. The game is simple: ya gotta rise to the top ranks of the mob, but to do so, ya gotta choose who to help out and choose who to rat out. There's only room for one wiseguy at the top of this mob!\n\nCommands:\n!Mob Start: Starts the joining phase of the game.\n!Mob JoinGame: The sender joins the game.\n!Mob LockJoin: ends the joining phase and the game begins.\n!Mob Snitch [player]: Command to be used during daily activities round. Snitches on someone, increasing notoriety level by 1.\n!Mob Support [player]: Command to be used in activities round. Support another player in the mob, increasing your and the person you support supportLevel by 1.```")
        return
    def Add_Player(name):
        p = Player(name)
        current_players.append(p)

    def Get_Most_Notorious(players):
        max_notoriety = 3
        notorious_players = []
        for p in players:
            if p.notoriety >= 3:
                notorious_players.append(p)
        return notorious_players
                
    def Get_Most_Popular(players):
        max_popularity = 8
        popular_players = []

        for p in players:
            if p.supportLevel >= 8: 
                popular_players.append(p)
        return popular_players



    def Get_Players_String():
        playerStr = "```Current Players:\n"
        for p in current_players:
            playerStr += p.name + "\n"

        playerStr += "```"
        return playerStr

    def Get_Player_By_Name(name):
        for p in current_players:
            if(p.name == name):
                return p
    
    def Compile_Player_Stats():
        retStr = "```Stats:\n\n"
        for p in current_players:
            retStr += p.ToString()
        
        retStr += "```"
        return retStr
            

    def checkReady(reaction, user):
        return reaction.count == 2 ## change to this after testing -> (len(current_players) + 1)

    if joining_phase:
        if action.lower() == "cheataddp":
            await ctx.send("bot player added")
            Add_Player(names[random.randint(0,len(names))])
            await ctx.send(Get_Players_String())
            return
            
        if not game_started and action.lower() != "start":
            await ctx.send("Game not started, please start game before making another command")
            return
        if not game_started and action.lower() == "start":
            await ctx.send("Game Started. Players can now join.")
            game_started = True
            return
        
        if game_started and len(current_players) < 4 and action.lower() != "joingame":
            await ctx.send("Not enough players have joined, " + str(4 - len(current_players)) + " still needed")
            return
        elif game_started and action.lower() == "joingame":
            Add_Player(ctx.author.name)
            await ctx.send(ctx.author.name + " has joined the mob. Current players = " + str(len(current_players)) )
            await ctx.send(Get_Players_String())
            return
        elif game_started and len(current_players) >= 4 and action.lower() == "lockjoin":
            await ctx.send("Joining phase has ended. When everyone is ready, send '!Mob StartRound' to begin first round")
            joining_phase = False
            return
    if not joining_phase:
        while True:
            if current_round_phase == RoundPhase.PRE_ROUND: ## PRE ROUND
                if not round_messgaes_sent[0]:
                    s = await ctx.send("Alright wise guys, when you're ready to start today's round of activities, press the ✅ reaction")
                    await s.add_reaction('✅')
                    try: 
                        reaction, user = await bot.wait_for('reaction_add', check=checkReady)
                    except:
                        print("come on dawg")
                    else:
                        await ctx.send("Alright guys, now that everybody's ready, lets start the round. Let me know who ya either want to snitch on or support, or if ya gonna take the day off.")
                        current_round_phase = RoundPhase.ROUND
                print("preround")


            if current_round_phase == RoundPhase.ROUND: ## DURING ROUND
                if not round_messgaes_sent[1]:
                    await ctx.send("Once everybody finishes their daily activities, we'll proceed to dinner")
                    round_messgaes_sent[1] = True
                    return
                
                
                if isinstance(ctx.channel, discord.channel.DMChannel):
                    print("dm bot")
                    if action.lower() == "snitch" and not Get_Player_By_Name(ctx.author.name).made_action_this_turn:
                        playerHit = Get_Player_By_Name(user)
                        playerHit.notoriety += 1
                        actionsMade += 1
                        #await ctx.message.delete()
                    elif action.lower() == "support" and not Get_Player_By_Name(ctx.author.name).made_action_this_turn:
                        playerHit = Get_Player_By_Name(user)
                        user_player = Get_Player_By_Name(ctx.author.name)
                        user_player.supportLevel += 1
                        playerHit.supportLevel += 1
                        actionsMade += 1
                        #await ctx.message.delete()                
                    elif action.lower() == "pass" and not Get_Player_By_Name(ctx.author.name).made_action_this_turn:
                        actionsMade += 1
                        #await ctx.message.delete()

                if action.lower() == "cheatfinishround": ## devcheat
                    actionsMade = len(current_players)
                    print("using finish cheat")
                
                if action.lower() == "cheatkillplayer":
                    print("kill player")
                    current_players[0].supportLevel = 8     
                if action.lower() == "cheatpromoteplayer":
                    current_players[0].supportLevel = 4

                if actionsMade == len(current_players):
                    await ctx.send("Alright fellas, I've gotten everything I need to know from everybody, lets go to dinner, maybe someone needs to get something off their chest.")
                    current_round_phase = RoundPhase.POST_ROUND 
                    round_messgaes_sent[1] = False  
                    actionsMade = 0
                else:
                    return   


                    
                    

            if current_round_phase == RoundPhase.POST_ROUND: ## POST ROUND
                await ctx.send("So I've gotten interesting news from you lot today. Here's how I's seein ya...")
                await ctx.send(Compile_Player_Stats())
                

                players_getting_shot = Get_Most_Notorious(current_players)
                if len(players_getting_shot) > 0:
                    await ctx.send("Looks like we got some dirty rats in this organization. Mob bot won't allow it.")
                    mobBotShoots = "```Mob points his gun and shoots:\n"
                    for c in players_getting_shot:
                        mobBotShoots += c.name + "\n"
                    
                    mobBotShoots += "```"
                    await ctx.send(mobBotShoots)
                    for c in players_getting_shot:
                        current_players.remove(c)
                    await ctx.send("now that that's over let's continue, shall we.")

                winners = Get_Most_Popular(current_players)
                if len(winners) > 0:
                    await ctx.send("Welp, I gotta say, there are some great people in this family. Mob bot is happy.")
                    mobBotShakes = "```Mob bot stands up to shake the hands of:\n"
                    for c in winners:
                        mobBotShakes += c.name + "\n"
                    mobBotShakes += "```"
                    await ctx.send(mobBotShakes)
                    await ctx.send("Congratulations, you win the game.")
                    return 

                if len(players_getting_shot) > 0:
                    await ctx.send("")
                newS = await ctx.send("Once everybodies finished dinner, speaking ya mind and all that, we'll go on to the next day. [Click ✅ when you're ready to move on]")
                await newS.add_reaction('✅')
                try: 
                    reaction, user = await bot.wait_for('reaction_add', check=checkReady)
                except:
                    print("come on dawg")
                else:
                    await ctx.send("Seems like we're all done here. Have a goodnight everyone.")
                    current_round_phase = RoundPhase.PRE_ROUND
                

                
                print("postround")





bot.run(TOKEN)

