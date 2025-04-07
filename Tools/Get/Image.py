import disnake
from PIL import Image, ImageDraw, ImageFont           
import io

from Tools.Get.Different import count_user_messages
from Tools.Get.UserAvatar import getUserAvatar
from config import DELETE_ERROR_SECONDS
from Tools.GeneralUI import ErrEmbed
   
async def getImage(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):

    user = await self.bot.db.get_user(member.id, inter.guild.id)
    if not user:
        return await inter.response.send_message(embed=await ErrEmbed(self, "Не удалось найти данные пользователя!"), delete_after=DELETE_ERROR_SECONDS, ephemeral=True)
    
    file = await getUserAvatar(member)
    image = Image.open(io.BytesIO(file))
    config = await self.bot.db.get_config(inter.guild.id)
    total_messages = await count_user_messages("01.01.2000", "01.01.2000", member.id, inter.guild.id, channel_id=config["countMessages"], flag=True)
    coins = user.coins
    voiceActivity = user.voiceActivity
    users_coins = await self.bot.db.get_users(inter.guild.id, sort=True)
    i = 0
    async for user in users_coins:
        if user["userId"] == member.id:
            top = i
        i += 1

    size = min(image.width, image.height)
    image = image.crop((
        (image.width - size) // 2,
        (image.height - size) // 2,
        (image.width + size) // 2,
        (image.height + size) // 2
    ))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    image = image.convert("RGBA")
    image.putalpha(mask)

    desired_size = 205

    image = image.resize((desired_size, desired_size))
    font = ImageFont.truetype("assets/MYRIADPRO-REGULAR.OTF", size=28)

    im = Image.open("assets/design.psd")
    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (955,320),
        f"{coins:.1f}",
        fill=("#f3f3f3"),
        font = font
        )

    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (955,380),
        f"{top+1}",
        fill=("#f3f3f3"),
        font = font
        )

    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (955,260),
        f"{total_messages}",
        fill=("#f3f3f3"),
        font = font
        )

    if voiceActivity !=None:

        time_string = f"{voiceActivity[0]}h:{voiceActivity[1]}m:{voiceActivity[2]}s"
    else:
        time_string = "-"

    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (955,200),
        f"{time_string}",
        fill=("#f3f3f3"),
        font = font
        )
    
    font = ImageFont.truetype("assets/MYRIADPRO-REGULAR.OTF", size=35)

    draw = ImageDraw.Draw(im)

    rect = [215, 405, 430, 445]
    text = f"{inter.author.display_name}"
    if len(text) > 12:
        font = ImageFont.truetype("assets/MYRIADPRO-REGULAR.OTF", size=25)

    text_x = (rect[0] + rect[2]) // 2
    text_y = (rect[1] + rect[3]) // 2

    bbox = draw.textbbox((text_x, text_y), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x -= text_width // 2
    text_y -= text_height // 2

    draw.text((text_x, text_y), text, fill="#f3f3f3", font=font)

    im.paste(image, (219,163), image)
    
    with io.BytesIO() as image_buffer:
        im.save(image_buffer, "png")
        image_buffer.seek(0)

        file=disnake.File(fp=image_buffer, filename="image.png")
    
    return file