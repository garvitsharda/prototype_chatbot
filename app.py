from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os
from huggingface_hub import InferenceClient

app = Flask(__name__)

# -------------------------
# MongoDB Setup
# -------------------------
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["company_data"]
col = db["documents"]

# -------------------------
# Hugging Face Setup
# -------------------------
HF_TOKEN = os.environ.get("HF_TOKEN")
hf_client = InferenceClient(token=HF_TOKEN)

MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324:fastest"  # free chat‑ready model

def call_hf_chat(prompt_text):
    try:
        # Send chat request via Inference API
        response = hf_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error from HuggingFace API: {str(e)}"

# -------------------------
# Flask Routes
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_question = request.json.get("question", "").strip()
    if not user_question:
        return jsonify({"answer": "Please ask a valid question."})

    # Retrieve relevant documents
    results = list(col.find({"$text": {"$search": user_question}}).limit(3))
    if not results:
        results = list(col.find({"content": {"$regex": user_question, "$options": "i"}}).limit(3))

    context = " ".join([r.get("content", "") for r in results])
    if not context.strip():
        context = "No relevant information found in the database."

    prompt_text = f"""
Answer the following question using ONLY the context below.
Context:
{context}

Question: {user_question}
"""

    answer = call_hf_chat(prompt_text)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
