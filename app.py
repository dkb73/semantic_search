from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import config  

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=config.GEMINI_API_KEY)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hostelDB"]
hostel_collection = db["hostels"]

# Load FAISS index and hostel IDs
index = faiss.read_index("hostel_index.faiss")
hostel_ids = np.load("hostel_ids.npy")

# Function to generate embeddings
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return np.array(response["embedding"], dtype="float32")

@app.route("/")
def home():
    return render_template("index.html")  # Serve the frontend page

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    # Get embedding for query
    query_embedding = get_embedding(query).reshape(1, -1)

    # Search using FAISS
    D, I = index.search(query_embedding, k=5)

    # Retrieve hostel details from MongoDB
    results = []
    for i in I[0]:
        if i < len(hostel_ids):
            hostel_id = hostel_ids[i]
            hostel = hostel_collection.find_one({"_id": ObjectId(hostel_id)})
            if hostel:
                results.append({
                    "name": hostel["name"],
                    "location": hostel["location"],
                    "description": hostel["description"],
                    "facilities": hostel["facilities"],
                    "room_types": hostel["room_types"],
                    "monthly_rent": hostel["monthly_rent"],
                    "ratings": hostel["ratings"],
                    "contact": hostel["contact"]["phone"]
                })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
