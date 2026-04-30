import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Zero-Waste AI Chef")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

class ChatRequest(BaseModel):
    messages: list

@app.post("/api/chat")
async def chat_with_sage(req: ChatRequest):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return {"reply": "API Key missing."}
    try:
        client = Groq(api_key=api_key)
        system_msg = {
            "role": "system", 
            "content": "You are Sage, a friendly AI Chef. Keep replies to 1 short sentence. If asked 'how are you', say 'I am great! Ready to turn your leftovers into magic?'"
        }
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[system_msg] + req.messages,
            temperature=0.7 
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

class IngredientInput(BaseModel):
    ingredients: str

@app.post("/api/recipe")
async def generate_recipe(payload: IngredientInput):
    api_key = os.environ.get("GROQ_API_KEY")
    try:
        client = Groq(api_key=api_key)
        prompt = f"Provide a recipe for: {payload.ingredients}. Start with a Title, then Ingredients, then Steps."
        msg = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "recipe_title": "Zero-Waste Creation",
            "recipe_body": msg.choices[0].message.content,
            "waste_tip": "Save your vegetable scraps for a future broth!"
        }
    except Exception as e:
        return {"recipe_title": "Error", "recipe_body": str(e), "waste_tip": "N/A"}