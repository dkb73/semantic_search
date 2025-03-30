import google.generativeai as genai
import faiss
import numpy as np

# Configure Gemini API
genai.configure(api_key="AIzaSyDYfBtQvnWCj4mNLAHOfjONB411j0ygWzg")  # Use environment variables instead of hardcoding

# Function to generate embeddings
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",  
        content=text,
        task_type="retrieval_document"  
    )
    return np.array(response["embedding"], dtype="float32")

# Sample hostel data
hostel_data = [
    "Affordable boys PG in Gandhinagar with AC",
    "Luxury hostel for students in Ahmedabad",
    "Budget-friendly accommodation in Gandhinagar",
    "Girls PG in Delhi with high-speed WiFi",
    "Cheap student hostel near metro station"
]

# Convert hostel descriptions into embeddings
hostel_embeddings = np.array([get_embedding(desc) for desc in hostel_data])

# Create FAISS index for similarity search
index = faiss.IndexFlatL2(hostel_embeddings.shape[1])  
index.add(hostel_embeddings)

# User query
query = "Cheap hostel in Gandhinagar"
query_embedding = get_embedding(query).reshape(1, -1)  

# Search in FAISS index (find top 2 matches)
D, I = index.search(query_embedding, k=5)  
matching_hostels = [hostel_data[i] for i in I[0]]

# Show results
print("🔹 User Query:", query)
print("🔹 Top Matches:", matching_hostels)
