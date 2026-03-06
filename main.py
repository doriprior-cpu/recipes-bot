from fastapi import FastAPI, Request
from dotenv import load_dotenv
import anthropic
import requests
import os

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = "recipes123"

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

def get_recipe_response(user_message):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system="אתה בוט מתכונים בעברית. כשמשתמש שולח מרכיבים, תציע 3 מתכונים עם מה שיש ו-3 מתכונים עם תוספת קטנה. תשובות קצרות וברורות.",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

@app.get("/")
def root():
    return {"status": "הבוט פועל!"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge", 0))
    return {"error": "Invalid token"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        message = value["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]
        reply = get_recipe_response(text)
        send_whatsapp_message(from_number, reply)
    except Exception as e:
        pass
    return {"status": "ok"}
