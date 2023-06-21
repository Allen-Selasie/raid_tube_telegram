import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube, Playlist

# Telegram bot token
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Command to handle /start
def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the YouTube downloader bot!")

# Command to handle /download
def download(update: Update, context):
    user_input = update.message.text.split(" ")
    url = user_input[1]
    media_type = user_input[2]

    # Ask the user for quality preference
    context.bot.send_message(chat_id=update.effective_chat.id, text="What quality would you like?")

    # Define a custom handler for quality response
    context.user_data['url'] = url
    context.user_data['media_type'] = media_type
    context.user_data['user_id'] = update.effective_chat.id
    return ask_quality

# Custom handler for quality preference
def ask_quality(update: Update, context):
    quality = update.message.text

    # Get the URL, media type, and user ID from context.user_data
    url = context.user_data['url']
    media_type = context.user_data['media_type']
    user_id = context.user_data['user_id']

    # Download YouTube video
    if media_type == "video":
        try:
            youtube = YouTube(url)
            if quality.lower() == 'audio':
                video = youtube.streams.filter(only_audio=True).first()
                video.download()
                context.bot.send_message(chat_id=user_id, text="Video downloaded as audio successfully!")
            else:
                video = youtube.streams.get_by_resolution(quality)
                video.download()
                context.bot.send_message(chat_id=user_id, text="Video downloaded successfully!")
        except Exception as e:
            context.bot.send_message(chat_id=user_id, text="An error occurred while downloading the video.")

    # Download YouTube playlist
    elif media_type == "playlist":
        try:
            playlist = Playlist(url)
            for video in playlist.videos:
                if quality.lower() == 'audio':
                    audio = video.streams.filter(only_audio=True).first()
                    audio.download()
                else:
                    video.streams.get_by_resolution(quality).download()
            if quality.lower() == 'audio':
                context.bot.send_message(chat_id=user_id, text="Playlist downloaded as audio successfully!")
            else:
                context.bot.send_message(chat_id=user_id, text="Playlist downloaded successfully!")
        except Exception as e:
            context.bot.send_message(chat_id=user_id, text="An error occurred while downloading the playlist.")

# Command to handle any other text message
def echo(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid command. Please use /download <url> <video/playlist>")

# Main function
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    start_handler = CommandHandler('start', start)
    download_handler = CommandHandler('download', download)

    # Message handler
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

    # Add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(download_handler)
    dispatcher.add_handler(echo_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
