import streamlit as st
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import config
import html

# Load environment variables
load_dotenv()

# Get environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in environment variables")
    st.stop()

if not MONGO_URI:
    st.error("MONGO_URI not found in environment variables")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="Hostel Search",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS with improved styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main {
        padding: 2rem;
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 12px 16px;
        font-size: 16px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 0 2px rgba(255,75,75,0.2);
    }
    .stExpander {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .stMarkdown {
        color: #333;
    }
    .header-container {
        text-align: center;
        padding: 2rem;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    .header-title {
        color: #FF4B4B;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #666;
        font-size: 1.2rem;
    }
    .search-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .search-title {
        color: #333;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    .results-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .results-title {
        color: #333;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .hostel-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 5px solid #FF4B4B;
        transition: transform 0.3s ease;
        font-size: 1.75rem;
        font-weight: 700;
    }
    .hostel-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .hostel-name {
        color: #FF4B4B;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .hostel-detail {
        color: #555;
        margin-left: 5rem;
        font-size: 1rem;
        line-height: 1.5;

    }
    .hostel-section {
        margin-top: 1rem;
    }
    .section-title {
        color: #333;
        font-weight: 600;
        font-size: 1.25rem;
        margin-left: 5rem;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 0.5rem;
    }
    .facility-tag {
        display: inline-block;
        background-color: #f0f0f0;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        color: #555;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    .facility-tag:hover {
        background-color: #e0e0e0;
        transform: translateY(-2px);
    }
    .room-type-tag {
        display: inline-block;
        background-color: #FFE5E5;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        color: #FF4B4B;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    .room-type-tag:hover {
        background-color: #FFD5D5;
        transform: translateY(-2px);
    }
    .rating-stars {
        color: #FFD700;
        margin-top: 0.5rem;
        margin-left: 5rem;
        font-size: 1.2rem;
    }
    .no-results {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
    .divider {
        height: 1px;
        background-color: #f0f0f0;
        margin: 1.5rem 0;
    }
    .spinner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    .error-message {
        background-color: #FFF5F5;
        color: #FF4B4B;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF4B4B;
        margin: 1rem 0;
    }
    .info-message {
        background-color: #F0F7FF;
        color: #3182CE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3182CE;
        margin: 1rem 0;
    }
    .contact-badge {
        background-color: #E9FFF9;
        margin-left: 5rem;
        color: #38B2AC;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
    }
    .price-badge {
        background-color: #EBF8FF;
        color: #3182CE;
        border-radius: 20px;
        display: inline-block;
        margin-left: 5rem;
        font-weight: 600;
    }
    .stTextInput {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }
    .stTextInput > div > div > input {
        width: 100%;
        padding: 15px 20px;
        font-size: 16px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.1);
    }
    .stButton {
        width: 100%;
        max-width: 300px;
        margin: 20px auto;
    }
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        padding: 15px 30px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def escape_html(text):
    if isinstance(text, (int, float)):
        text = str(text)
    return html.escape(str(text)) if text else ""

def render_stars(rating):
    try:
        rating = float(rating)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = "★" * full_stars
        stars += "½" if half_star else ""
        stars += "☆" * empty_stars
        
        return f"{rating} {stars}"
    except (ValueError, TypeError):
        return "Not rated"

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")

# Connect to MongoDB Atlas
try:
    client = MongoClient(MONGO_URI)
    db = client["hostelDB"]
    hostel_collection = db["hostels"]
    # Connection successful, but no need to show success message to keep UI clean
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

# Header Section
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏠 Semantic Search</h1>
        <p class="header-subtitle">Find your perfect accommodation with AI-powered natural language search</p>
    </div>
""", unsafe_allow_html=True)

# Search Section
st.markdown('<h2 class="search-title">What kind of hostel are you looking for?</h2>', unsafe_allow_html=True)

# Search input with placeholder
query = st.text_input("", 
                     placeholder="Example: Looking for a hostel near university with AC rooms and laundry facility",
                     key="search_query")

# Search button
search_pressed = st.button("🔍 Find My Perfect Hostel")

st.markdown('</div>', unsafe_allow_html=True)

# Results Section
if search_pressed:
    if not query:
        st.markdown("""
            <div class="info-message">
                Please enter a search query to find hostels matching your preferences.
            </div>
        """, unsafe_allow_html=True)
    else:
        if not index or hostel_ids is None:
            st.markdown("""
                <div class="error-message">
                    <strong>Error:</strong> Search index not available. Please try again later or contact support.
                </div>
            """, unsafe_allow_html=True)
        elif hostel_collection is None:
            st.markdown("""
                <div class="error-message">
                    <strong>Error:</strong> Database connection not available. Please try again later or contact support.
                </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Searching for your perfect hostel match..."):
                query_embedding = get_embedding(query)
                if query_embedding is not None:
                    query_embedding = query_embedding.reshape(1, -1)
                    D, I = index.search(query_embedding, k=5)

                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.markdown(f'<h2 class="results-title">Top Matches for "{escape_html(query)}"</h2>', unsafe_allow_html=True)

                    if I[0][0] == -1 or all(i == -1 for i in I[0]):
                        st.markdown("""
                            <div class="no-results">
                                <img src="https://cdn-icons-png.flaticon.com/512/6134/6134065.png" width="100">
                                <h3>No matching hostels found</h3>
                                <p>Try different keywords or broaden your requirements</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        found_results = False
                        
                        for i in I[0]:
                            if i != -1 and 0 <= i < len(hostel_ids):
                                found_results = True
                                hostel_id = hostel_ids[i]
                                hostel = hostel_collection.find_one({"_id": ObjectId(hostel_id)})

                                if hostel:
                                    # Prepare rating display
                                    rating_display = render_stars(hostel.get('ratings', 'Not rated'))
                                    
                                    # Get and escape hostel data
                                    hostel_name = escape_html(hostel.get('name', 'Unknown Hostel'))
                                    hostel_location = escape_html(hostel.get('location', 'Location not specified'))
                                    hostel_rent = escape_html(hostel.get('monthly_rent', 'N/A'))
                                    hostel_description = escape_html(hostel.get('description', 'No description available'))                                  

                                    # Hostel name
                                    st.markdown(f"""<div class='hostel-card'>{hostel_name}</div>""", unsafe_allow_html=True)

                                    # Location
                                    st.markdown(f"""<div class='hostel-detail'><strong>📍 Location:</strong> {hostel_location}</div>""", unsafe_allow_html=True)

                                    # Price and rating container
                                    st.markdown("""<div style="display: flex; flex-wrap: wrap; align-items: center; margin-top: 0.5rem;">""", unsafe_allow_html=True)
                                    st.markdown(f"""<div class='price-badge'>💰 ₹{hostel_rent} / month</div>""", unsafe_allow_html=True)
                                    st.markdown(f"""<div class='rating-stars'>⭐ {rating_display}</div>""", unsafe_allow_html=True)
                                    st.markdown("""</div>""", unsafe_allow_html=True)  # Close flex container

                                    # About section
                                    st.markdown("""<div class='hostel-section'><div class='section-title'>About this Hostel</div></div>""", unsafe_allow_html=True)
                                    st.markdown(f"""<div class='hostel-detail'>{hostel_description}</div>""", unsafe_allow_html=True)

                                    # Facilities
                                    if hostel.get('facilities'):
                                        st.markdown("<div class='section-title'>Facilities & Amenities</div>", unsafe_allow_html=True)
                                        facility_html = ""
                                        for idx, facility in enumerate(hostel['facilities']):
                                            margin_style = 'margin-left: 5rem;' if idx == 0 else ''
                                            facility_html += f"<div class='facility-tag' style='{margin_style}'>🏷️ {escape_html(facility)}</div>"
                                        st.markdown(f"<div style='display: flex; flex-wrap: wrap;'>{facility_html}</div>", unsafe_allow_html=True)

                                    # Room types
                                    if hostel.get('room_types'):
                                        st.markdown("<div class='section-title'>Available Room Types</div>", unsafe_allow_html=True)
                                        room_html = ""
                                        for idx, room in enumerate(hostel['room_types']):
                                            margin_style = 'margin-left: 5rem;' if idx == 0 else ''
                                            room_html += f"<div class='room-type-tag' style='{margin_style}'>🛏️ {escape_html(room)}</div>"
                                        st.markdown(f"<div style='display: flex; flex-wrap: wrap;'>{room_html}</div>", unsafe_allow_html=True)

                                    # Contact information
                                    contact_phone = escape_html(hostel.get('contact', {}).get('phone', 'Not provided'))
                                    contact_email = escape_html(hostel.get('contact', {}).get('email', 'Not provided'))

                                    st.markdown("""<div class='section-title'>Contact Information</div>""", unsafe_allow_html=True)
                                    st.markdown("""<div style="display: flex; flex-wrap: wrap;">""", unsafe_allow_html=True)
                                    st.markdown(f"""<div class='contact-badge'>📞 {contact_phone}</div>""", unsafe_allow_html=True)
                                    if contact_email != 'Not provided':
                                        st.markdown(f"""<div class='contact-badge' style="margin-left: 0.5rem;">✉️ {contact_email}</div>""", unsafe_allow_html=True)
                                    st.markdown("""</div>""", unsafe_allow_html=True)  # Close flex container

                                    # Close hostel-card div (ONLY ONCE at the very end)
                                    st.markdown("""</div>""", unsafe_allow_html=True)

                                    # Add divider outside the card
                                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                        
                        if not found_results:
                            st.markdown("""
                                <div class="no-results">
                                    <h3>No valid hostel information found</h3>
                                    <p>Please try a different search query</p>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

