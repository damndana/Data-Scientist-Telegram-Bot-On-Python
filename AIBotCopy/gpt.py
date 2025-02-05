import openai
import httpx
import os

class ChatGptService:
    def __init__(self):
        token = os.getenv("OPENAI_API_KEY")
        if not token:
            raise ValueError("API key not found. Set the OPENAI_API_KEY environment variable.")
        self.client = openai.Client(api_key=token, http_client=httpx.Client(verify=True))
        self.message_list = []

    async def send_message_list(self) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Choose GPT model
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def generate_quiz_question(self) -> tuple:
        prompt_text = "You are a helpful AI that generates quiz questions about data analytics."
        message_text = "Generate a multiple-choice question with four answer options. Format: \n" \
                       "Question: <text>\nA) <option 1>\nB) <option 2>\nC) <option 3>\nD) <option 4>"

        quiz_text = await self.send_question(prompt_text, message_text)
        lines = quiz_text.split("\n")
        if len(lines) < 5:
            return None, None  # Handle error case

        question = lines[0].replace("Question: ", "").strip()
        options = [line.split(") ")[1].strip() for line in lines[1:5]]
        return question, options
