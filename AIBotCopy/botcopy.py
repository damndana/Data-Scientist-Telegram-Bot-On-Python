import os
from dotenv import load_dotenv
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from gpt import ChatGptService  # Ensure your ChatGptService is also secured
from util import *


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("API keys are missing! Check your .env file.")


chatgpt = ChatGptService(token=OPENAI_API_KEY)
dialog = Dialog()
dialog.mode = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "main"
    text = (
        "Welcome to AnalyticBot – Your AI Learning Assistant!\n"
        "\n✅ Interactive topic-based daily quizzes"
        "\n📢 Daily AI & Data Science news digests"
        "\n🎯 Expert mode for detailed Q&A in data science"
    )
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "Run",
        "gpt": "Talk to AI (Data Science Expert)",
        "quiz": "Daily quizzes on AI & Data Science",
        "whatsup": "Latest IT & AI News",
    })

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "gpt"
    user_question = " ".join(context.args) if context.args else "Tell me something about data science."
    prompt = "You are a senior data engineer, data scientist, and analyst with deep expertise. Answer professionally:"
    answer = await chatgpt.add_message(user_question)
    await send_text(update, context, answer)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt_text = "You are a helpful AI that generates quiz questions about data analytics."
    message_text = "Generate a multiple-choice question with four answer options. " \
                   "Clearly indicate the correct answer using this format: \n" \
                   "Question: <text>\nA) <option 1>\nB) <option 2>\nC) <option 3>\nD) <option 4>\n" \
                   "Correct Answer: <A, B, C, or D>"

    quiz_text = await chatgpt.send_question(prompt_text, message_text)


    lines = quiz_text.split("\n")
    if len(lines) < 6:
        await update.message.reply_text("Error: Could not generate a valid quiz question.")
        return

    question = lines[0].replace("Question: ", "").strip()
    options = [line.split(") ")[1].strip() for line in lines[1:5]]
    correct_answer_letter = lines[5].replace("Correct Answer: ", "").strip()


    correct_option_id = {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_answer_letter, 0)

    # Send poll as a quiz
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False
    )

async def whatsup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "news"
    prompt = "Summarize the latest AI & Data Science news in a concise and informative way."
    news_summary = await chatgpt.send_question(prompt, "Fetch AI and IT news updates.")
    await send_text(update, context, news_summary)


app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(CommandHandler("whatsup", whatsup))

app.run_polling()
