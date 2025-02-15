from discord.ext import commands
from discord import Embed

import random
import requests

COLOR = [0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F, 0x800000, 0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585, 0xFFB6C1, 0x00CED1]

class MyCommands(commands.Cog):
    """A couple of commands."""

    def __init__(self, bot: commands.Bot, wolframclient):
        self.bot = bot
        self.wolframclient = wolframclient
        self.config = {
            "timeout_random": 60
        }


    @commands.command(name='random')
    async def random(self, ctx: commands.Context, number_of_dice: int, number_of_sides: int):
        """Simulates rolling dice."""
        print("random event!")

        embed = Embed(title="Zufallszahlen",color=random.choice(COLOR), description=f"{number_of_dice} Würfel mit {number_of_sides} Seiten:")

        for _ in range(number_of_dice):
            w =  str(random.choice(range(1, number_of_sides + 1)))
            embed.add_field(name=w, value = "_"*len(w)+"/"+str(number_of_sides), inline=True)

        timeout = self.config["timeout_random"]        
        embed.set_footer(text=f"Selbstlöschend nach {timeout} Sekunden.")

        await ctx.message.delete()
        await ctx.send(embed=embed, delete_after=timeout)


    @commands.command(name='hi')
    async def hi(self, ctx: commands.Context, number_of_hi: int = 1):
        """Say \"Hi!\" multiple times."""
        print("hi!")

        for _ in range(number_of_hi):
            await ctx.send('Hi!')


    @commands.command(name='echo', help='Echo string.')
    async def echo(self, ctx: commands.Context, *, txt:str):
        """Echos input string."""
        print("echo!")

        await ctx.send(txt)


    @commands.command(name='emoji')
    async def emoji(self, ctx: commands.Context, emoji_name: str, image_url:str):
        """Creates custom server emoji. 
        Supports .jpg .gif .png."""
        print("emoji!")

        response = requests.get(image_url)
        img = response.content   
        img = await ctx.guild.create_custom_emoji(name=emoji_name, image=img)
        await ctx.send(">> Emoji created: "+str(img))


    @commands.command(name='molec')
    async def molec(self, ctx: commands.Context, smile_string: str):
        """'Visualize a given molecule string. Supports MIME and other structural identifier. 
        Note: Triple bonds in SMILES strings represented by \'\#\' have to be URL-escaped as \'%23\' and \'?\' as \'%3F\'."""
        print('molec!')

        url1 = 'http://cactus.nci.nih.gov/chemical/structure/' + smile_string+ '/image'
        await ctx.send(">> Molecule: "+ str(url1))
        

    @commands.command(name='wolfram')
    async def wolfram(self, ctx: commands.Context, *, question_string: str):
        """Use Wolfram Alpha (API) to solve Math or ask random stuff It can do ...
        everything WolframAlpha can do: Equations, Weather  (Overview: https://www.wolframalpha.com/)"""
        print('wolfram! ' + question_string)

        res = self.wolframclient .query(question_string)
        if not res.success:
            await ctx.send(">> Wolfram Weisnisch Weiter... ")
            return
        try:
            message = next(res.results).text
        except StopIteration:
            message = "No short result found. Try \"!wolfram-l\"."
        await ctx.send(">> Wolfram: "+ message)


    @commands.command(name='wolfall')
    async def wolfall(self, ctx: commands.Context, *, question_string: str):
        """See !wolfram. Returns long informative answer"""
        print('wolfram! ' + question_string)

        res = self.wolframclient .query(question_string)
        if not res.success:
            await ctx.send(">> Wolfram Weisnisch Weiter... ")
            return

        message = ""    
        for pod in res.pods:
            if pod.title == res.datatypes:
                message += str(pod.subpod.img.src) + "\n"
            for sub in pod.subpods:
                if sub.plaintext:
                    message += str(sub.plaintext) + "\n"
        await ctx.send(">> Wolfram: "+ message)


    @commands.command(name='wolfget')
    async def wolfget(self, ctx: commands.Context, image_title: str, question_string: str):
        """See !wolfram. Returns image with given title"""
        print('wolfram! ' + question_string)

        res = self.wolframclient .query(question_string)
        if not res.success:
            await ctx.send(">> Wolfram Weisnisch Weiter... ")
            return

        message = ""    
        try:
            message = next(res.results).text+"\n"
        except StopIteration:
            pass
        for pod in res.pods:
            if pod.title == image_title:
                message += str(pod.subpod.img.src) + "\n"
        await ctx.send(">> Wolfram: "+ message)

