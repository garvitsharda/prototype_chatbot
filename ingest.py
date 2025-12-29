# ingest.py
from pymongo import MongoClient
from docx import Document

# Connect to MongoDB
client = MongoClient("MONGO_URI")
db = client["company_data"]
col = db["documents"]

# Read Word file
doc = Document("data/company.docx")
full_text = ""
for para in doc.paragraphs:
    if para.text.strip():
        full_text += para.text + " "

# Split into chunks (~400 words)
words = full_text.split()
chunk_size = 400
for i in range(0, len(words), chunk_size):
    chunk_text = " ".join(words[i:i+chunk_size])
    col.insert_one({
        "title": f"Chunk {i//chunk_size + 1}",
        "content": chunk_text
    })

print("Data ingested into MongoDB")
