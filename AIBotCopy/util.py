import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, BotCommand, MenuButtonCommands, \
    BotCommandScopeChat, MenuButtonDefault
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


def format_user_info(user) -> str:

    fields = {
        "expertise": "Expertise Level",
        "interests": "AI & Data Science Interests",
        "goals": "Learning Goals",
        "preferred_topics": "Preferred Topics",
    }

    result = "\n".join(f"{name}: {user[key]}" for key, name in fields.items() if key in user)
    return result or "No information available."


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:

    if text.count('_') % 2 != 0:
        text = text.replace('_', '\\_')  # Escape Markdown issues
    text = text.encode('utf-16', errors='surrogatepass').decode('utf-16')
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:

    text = text.encode('utf-16', errors='surrogatepass').decode('utf-16')
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)


async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict) -> Message:

    keyboard = [[InlineKeyboardButton(value, callback_data=key)] for key, value in buttons.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> Message:

    file_path = os.path.join('resources', 'images', f'{name}.jpg')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image {name}.jpg not found in resources/images/")

    with open(file_path, 'rb') as photo:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):

    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)


async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(), chat_id=update.effective_chat.id)


def load_message(name):

    file_path = os.path.join("resources", "messages", f"{name}.txt")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"Message file '{name}.txt' not found."


def load_prompt(name):

    file_path = os.path.join("resources", "prompts", f"{name}.txt")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"Prompt file '{name}.txt' not found."


class Dialog:

    mode = None
