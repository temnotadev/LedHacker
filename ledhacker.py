from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from PIL import Image
import requests
import io

TOKEN = "8315327828:AAG8lSt8eULmyyBQircmduENh_Cyk8HHhlA"

user_ips = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send /setip <your LED IP> then send an image.")

async def set_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_ips[update.effective_user.id] = context.args[0]
        await update.message.reply_text(f"IP set to {context.args[0]}. Now send an image.")
    else:
        await update.message.reply_text("Usage: /setip 192.168.0.100")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_ips:
        await update.message.reply_text("Please set IP first using /setip.")
        return

    photo = await update.message.photo[-1].get_file()
    image_data = await photo.download_as_bytearray()
    img = Image.open(io.BytesIO(image_data))
    img = img.resize((64, 32)).convert('RGB')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    ip = user_ips[user_id]
    try:
        # Example endpoint — replace with your LED's real upload method
        response = requests.post(f"http://{ip}/upload", files={"image": buffer})
        if response.ok:
            await update.message.reply_text("Image sent to LED!")
        else:
            await update.message.reply_text(f"Failed: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setip", set_ip))
app.add_handler(MessageHandler(filters.PHOTO, handle_image))

app.run_polling()
