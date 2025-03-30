import streamlit as st
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import config

# Configure Gemini API
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")

# Connect to MongoDB Atlas
try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    hostel_collection = db[config.COLLECTION_NAME]
    # st.success("Successfully connected to MongoDB Atlas!")
except Exception as e:
    st.error(f"Error connecting to MongoDB Atlas: {e}")
    hostel_collection = None

# Load FAISS index and hostel IDs
try:
    index = faiss.read_index("hostel_index.faiss")
    hostel_ids = np.load("hostel_ids.npy")
except Exception as e:
    st.error(f"Error loading FAISS index or hostel IDs: {e}")
    index = None
    hostel_ids = None

# Function to generate embeddings
def get_embedding(text):
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return np.array(response["embedding"], dtype="float32")
    except Exception as e:
        st.error(f"Error generating embedding: {e}")
        return None

# Streamlit UI
st.title("Hostel Search Application")
st.write("Search for hostels using natural language queries")

# Search input
query = st.text_input("Enter your search query:", "")

if st.button("Search"):
    if not query:
        st.warning("Please enter a search query")
    else:
        if not index or hostel_ids is None:
            st.error("FAISS index not available")
        elif hostel_collection is None:
            st.error("MongoDB connection not available")
        else:
            with st.spinner("Searching..."):
                # Get embedding for query
                query_embedding = get_embedding(query)
                if query_embedding is not None:
                    query_embedding = query_embedding.reshape(1, -1)

                    # Search using FAISS
                    D, I = index.search(query_embedding, k=5)

                    # Handle case where no results are found
                    if I[0][0] == -1:
                        st.info("No matching hostels found")
                    else:
                        # Display results
                        for i in I[0]:
                            if 0 <= i < len(hostel_ids):
                                hostel_id = hostel_ids[i]
                                hostel = hostel_collection.find_one({"_id": ObjectId(hostel_id)})

                                if hostel:
                                    with st.expander(f"🏠 {hostel.get('name', 'Unknown')}"):
                                        st.write(f"**Location:** {hostel.get('location', 'Not specified')}")
                                        st.write(f"**Description:** {hostel.get('description', 'No description available')}")
                                        
                                        if hostel.get('facilities'):
                                            st.write("**Facilities:**")
                                            for facility in hostel['facilities']:
                                                st.write(f"- {facility}")
                                        
                                        if hostel.get('room_types'):
                                            st.write("**Room Types:**")
                                            for room in hostel['room_types']:
                                                st.write(f"- {room}")
                                        
                                        st.write(f"**Monthly Rent:** {hostel.get('monthly_rent', 'Not available')}")
                                        st.write(f"**Ratings:** {hostel.get('ratings', 'Not rated')}")
                                        st.write(f"**Contact:** {hostel.get('contact', {}).get('phone', 'Not provided')}")