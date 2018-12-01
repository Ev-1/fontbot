import discord
import os
import asyncio
import codecs
import json

from discord.ext import commands


class EmojiText:
    DATA_PATH = 'data/emojitext/'
    FONTS = DATA_PATH + 'fonts.json'

    def __init__(self, bot):
        if not os.path.exists(self.DATA_PATH):
            os.makedirs(self.DATA_PATH)

        if not os.path.isfile(self.FONTS):
            with codecs.open(self.FONTS, "w+", encoding='utf8') as f:
                json.dump({}, f, indent=4)

        with codecs.open(self.FONTS, "r", encoding='utf8') as f:
            self.fonts = json.load(f)

        self.bot = bot
        self.map_types = {'AZ':'abcdefghijklmnopqrstuvwxyz', '09':'0123456789', 'punc':'.,-:!?'}


    @commands.command()
    async def listemoji(self, ctx):
        msg = ""
        for emoji in ctx.guild.emojis:
            if emoji.animated:
                msg += f'<a:{emoji.name}:{emoji.id}> '
            else:
                msg += f'<:{emoji.name}:{emoji.id}> '
        if len(msg) > 2000:
            await ctx.send(msg[0:1999])
            await ctx.send(msg[2000:-1])
        else:
            await ctx.send(msg)

    @commands.is_owner()
    @commands.command()
    async def makefont(self, ctx, font, mapping, *, emojis):
        """
            Make a new or update an existing font
            This command is for quickly making most of the characters
            <font> is the font name.
            <mapping> is AZ, 09 or punc and changes which characters you define
            <emojis> the emojis you want to map the characters to.

            AZ    maps to abcdefghijklmnopqrstuvwxyz
            09    maps to 0123456789
            punc  maps to .,-:!?

            custom maps characters not covered above
            !makefont <font> custom ø :emoji_ø: æ :emoji_æ:

            make sure to have the emojis in the right order
        """
        new_map = {}

        if mapping in self.map_types.keys():
            to_map = self.map_types[mapping]
            emoji_list = emojis.split()
            if len(emoji_list) != len(to_map):
                await ctx.send(f'Wrong number of emojis, you need {len(to_map)}')
                return
            for i in range(0,len(to_map)):
                new_map[to_map[i]] = emoji_list[i]

        elif mapping == "custom":
            custom_map = emojis.split()
            if len(custom_map)%2 != 0:
                await ctx.send("Your need the same amount of emojis and characters")
                return
            new_map = dict(zip(custom_map[::2], custom_map[1::2]))

        else:
            await ctx.send("You must choose a mapping, (AZ, 09, punc or custom)")
            return

        if font in self.fonts.keys():
            old_map = self.fonts[font]
        else:
            old_map = {}

        self.fonts[font] = {**old_map, **new_map}

        with codecs.open(self.FONTS, "w", encoding='utf8') as write_file:
            json.dump(self.fonts, write_file, indent=4)

        await ctx.send(f"Font {font} updated")

    @commands.is_owner()
    @commands.command()
    async def removefont(self, ctx, font):
        if font in self.fonts.keys():
            del self.fonts[font]
            with codecs.open(self.FONTS, "w", encoding='utf8') as write_file:
                json.dump(self.fonts, write_file, indent=4)
            await ctx.send(f'Font {font} deleted')
        else:
            await ctx.send('No font with that name')

    @commands.command()
    async def font(self, ctx, font: str=None):
        if font is None:
            msg = "List of available fonts:\n"
            for font in self.fonts.keys():
                msg += f"{font}\n"
            await ctx.send(msg)
            return

        if font in self.fonts.keys():
            msg = ""
            for character in self.fonts[font].keys():
                msg += f"{character} = {self.fonts[font][character]}\n"
            await ctx.send(msg)
            return
        await ctx.send("No font of that name")

    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if not isinstance(message.channel, discord.TextChannel):
            return

        content = message.content
        if content is '' or not content.startswith('f!'):  # hardcoded atm
            return

        font, msg = content[2:].split(None, 1)
        if font in self.fonts.keys():
            emojimsg = ""
            for character in msg.lower():
                if character == ' ':
                    emojimsg += '     '
                    pass
                try:
                    emojimsg += f'{self.fonts[font][character]}'
                except KeyError:
                    emojimsg += f'{character}'

            await message.channel.send(emojimsg)


def setup(bot):
    bot.add_cog(EmojiText(bot))
