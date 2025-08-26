import discord
from discord.ext import commands
import os
import asyncio
import random
import easy_pil
from io import BytesIO


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Welcome cog is ready.')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_channel = member.guild.system_channel

        if not welcome_channel:
            return  # Exit if no system channel is found

        try:
            # Use asyncio.to_thread for the blocking os.listdir call
            def get_images():
                return os.listdir("./cogs/welcome_images")

            images = await asyncio.to_thread(get_images)
            randomized_image = random.choice(images)
            image_path = os.path.join("./cogs/welcome_images", randomized_image)

            # Create the welcome card
            bg = easy_pil.Editor(image_path).resize((1920, 1080))

            # Handle the avatar
            avatar_image = await easy_pil.load_image_async(str(member.avatar.url))
            avatar = easy_pil.Editor(avatar_image).resize((500, 500)).circle_image()

            font_big = easy_pil.Font.poppins(size=90, variant="bold")
            font_small = easy_pil.Font.poppins(size=60, variant="bold")

            bg.paste(avatar, (700, 180))
            bg.ellipse((700, 180), 500, 500, outline="white", stroke_width=5)

            bg.text((960, 730), f"{member.name} just joined the server!", color="white", font=font_big, align="center")
            bg.text((960, 820), f"Member #{member.guild.member_count}", color="white", font=font_small, align="center")

            # Send the message
            with BytesIO(bg.image_bytes) as image_buffer:
                img_file = discord.File(image_buffer, filename="welcome_card.png")
                await welcome_channel.send(f"Bossing {member.name}! Kamusta ang buhay buhay?!", file=img_file)

        except FileNotFoundError:
            print("Error: The 'welcome_images' directory or a file was not found.")
        except Exception as e:
            print(f"An unexpected error occurred in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        leave_channel = member.guild.system_channel

        if leave_channel is None:
            return  # Exit the function if no system channel is found

        try:
            # Use asyncio.to_thread for the blocking os.listdir call
            def get_images():
                return os.listdir("./cogs/welcome_images")

            images = await asyncio.to_thread(get_images)
            randomized_image = random.choice(images)
            image_path = os.path.join("./cogs/welcome_images", randomized_image)

            bg = easy_pil.Editor(image_path).resize((1980, 1080))

            if member.avatar:
                avatar_image = await easy_pil.load_image_async(str(member.avatar.url))
                avatar = easy_pil.Editor(avatar_image).resize((500, 500)).circle_image()
                bg.paste(avatar, (700, 180))
                bg.ellipse((700, 180), 500, 500, outline="white", stroke_width=5)

            font_big = easy_pil.Font.caveat(size=90, variant="bold")
            font_small = easy_pil.Font.caveat(size=60, variant="bold")

            bg.text((960, 730), f"Goodbye {member.name}!", color="white", font=font_big, align="center")
            bg.text((960, 820), f"We now have {member.guild.member_count} members.", color="white", font=font_small,
                    align="center")

            with BytesIO(bg.image_bytes) as image_buffer:
                img_file = discord.File(image_buffer, filename="farewell_card.png")
                await leave_channel.send(f"Aray kohh, bat ka naman umalis bossing {member.name}!", file=img_file)

        except FileNotFoundError:
            print("Error: The 'welcome_images' directory or a file was not found.")
        except Exception as e:
            print(f"An unexpected error occurred in on_member_remove: {e}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
