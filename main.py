import os
import ffmpeg
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InputFile
import logging

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token (hardcoded for simplicity as per user request)
BOT_TOKEN = "7631955443:AAHymZAyiprbPP31BKs9vPmBmUqbFug2W_I"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text("Hi! Send me an m3u8 video URL, and I'll share the video for you.")

async def handle_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles m3u8 video URLs, streams them, and sends the video to Telegram."""
    message = update.message
    url = message.text.strip()

    # Validate the URL
    if "m3u8" not in url:
        await message.reply_text("Please send a valid m3u8 video URL.")
        return

    await message.reply_text("Processing the video... please wait.")

    try:
        # Use ffmpeg to stream the m3u8 URL directly to a pipe
        process = (
            ffmpeg
            .input(url)
            .output('pipe:', format='mp4', vcodec='copy', acodec='copy')  # Stream directly to mp4 format
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        # Read the streamed video data
        video_data = process.stdout.read()

        # Send the video directly to Telegram using InputFile
        await message.reply_video(
            video=InputFile(video_data, filename="video.mp4"),
            supports_streaming=True
        )

    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        await message.reply_text(f"Failed to process the video: {error_message}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
    finally:
        # Ensure the ffmpeg process is terminated
        if 'process' in locals():
            process.terminate()

# Set up the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_url))

# Start the bot
logger.info("Starting the bot...")
app.run_polling()
