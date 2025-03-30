import streamlit as st
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import config
from datetime import datetime

# Set page configuration with new theme
st.set_page_config(
    page_title="Hostel Haven",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with modern styling
st.markdown("""
    <style>
    :root {
        --primary: #6C63FF;
        --secondary: #4D44DB;
        --accent: #FF6584;
        --light: #F8F9FF;
        --dark: #2E2E48;
        --gray: #A3A3C2;
    }
    
    .stApp {
        background-color: var(--light);
        color: var(--dark);
    }
    
    /* Main container styling */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 3rem 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(108, 99, 255, 0.2);
        text-align: center;
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }
    
    /* Search section */
    .search-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    
    .search-title {
        color: var(--dark);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #E0E0F5;
        padding: 14px 18px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.2);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(to right, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(108, 99, 255, 0.15);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(108, 99, 255, 0.25);
        background: linear-gradient(to right, var(--secondary), var(--primary));
    }
    
    /* Results section */
    .results-section {
        margin-top: 2rem;
    }
    
    .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .results-title {
        color: var(--dark);
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .results-count {
        color: var(--gray);
        font-size: 1rem;
    }
    
    /* Hostel card */
    .hostel-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        border-left: 4px solid var(--primary);
    }
    
    .hostel-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .hostel-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .hostel-name {
        color: var(--dark);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .hostel-location {
        color: var(--gray);
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .hostel-price {
        background: linear-gradient(to right, var(--primary), var(--secondary));
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .hostel-rating {
        display: flex;
        align-items: center;
        gap: 5px;
        color: var(--dark);
        font-weight: 600;
    }
    
    .star-filled {
        color: #FFC107;
    }
    
    .star-empty {
        color: #E0E0E0;
    }
    
    .hostel-description {
        color: var(--dark);
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    /* Section styling */
    .section-title {
        color: var(--dark);
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #F0F0FA;
    }
    
    /* Tags styling */
    .tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .tag {
        background: #F0F0FA;
        color: var(--dark);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .facility-tag {
        background: #E6F7FF;
        color: #1890FF;
    }
    
    .room-tag {
        background: #F6FFED;
        color: #52C41A;
    }
    
    .contact-tag {
        background: #FFF2E8;
        color: #FA8C16;
    }
    
    /* Contact section */
    .contact-section {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--dark);
    }
    
    /* No results styling */
    .no-results {
        text-align: center;
        padding: 3rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    }
    
    .no-results-icon {
        font-size: 4rem;
        color: var(--gray);
        margin-bottom: 1rem;
    }
    
    /* Filter sidebar */
    .sidebar-section {
        margin-bottom: 2rem;
    }
    
    .sidebar-title {
        color: var(--dark);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .hostel-header {
            flex-direction: column;
            gap: 1rem;
        }
        
        .hostel-price {
            align-self: flex-start;
        }
    }
    
    /* Animation for loading */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .hostel-card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Map container */
    .map-container {
        height: 300px;
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
        margin-top: 1rem;
        border: 1px solid #F0F0FA;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--gray);
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    /* Badge for new hostels */
    .new-badge {
        background-color: var(--accent);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
        display: inline-block;
    }
    
    /* Amenities grid */
    .amenities-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .amenity-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

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

# Function to render star ratings
def render_stars(rating):
    try:
        rating = float(rating)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = ""
        stars += "★" * full_stars
        if half_star:
            stars += "½"
        stars += "☆" * empty_stars
        
        return stars
    except:
        return "Not rated"

# Helper function to escape HTML special characters
def escape_html(text):
    if text is None:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

# Helper function to check if hostel is new (added in last 30 days)
def is_new_hostel(hostel):
    if 'added_date' in hostel:
        added_date = hostel['added_date']
        if isinstance(added_date, str):
            try:
                added_date = datetime.strptime(added_date, "%Y-%m-%d")
            except:
                return False
        return (datetime.now() - added_date).days <= 30
    return False

# Sidebar filters
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: var(--primary);">🔍 Filters</h2>
            <p style="color: var(--gray);">Refine your search results</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Price Range</div>', unsafe_allow_html=True)
    price_range = st.slider(
        "Monthly rent range (₹)",
        min_value=0, max_value=20000, value=(2000, 10000),
        step=500,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Minimum Rating</div>', unsafe_allow_html=True)
    min_rating = st.select_slider(
        "Minimum rating",
        options=["1", "2", "3", "4", "5"],
        value="3",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Room Type</div>', unsafe_allow_html=True)
    room_types = st.multiselect(
        "Select room types",
        ["Single", "Double", "Dormitory", "Shared", "Private"],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Facilities</div>', unsafe_allow_html=True)
    facilities = st.multiselect(
        "Select facilities",
        ["WiFi", "AC", "Laundry", "Kitchen", "Parking", "Gym", "Study Room"],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Main content
st.markdown("""
    <div class="header">
        <h1 class="header-title">🏡 Hostel Haven</h1>
        <p class="header-subtitle">Discover your perfect student accommodation with AI-powered search</p>
    </div>
""", unsafe_allow_html=True)

# Search section
st.markdown('<div class="search-section">', unsafe_allow_html=True)
st.markdown('<h2 class="search-title">What are you looking for in a hostel?</h2>', unsafe_allow_html=True)

# Two-column layout for search
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input(
        "", 
        placeholder="Example: 'Affordable hostel near campus with AC rooms and good WiFi'",
        key="search_query",
        label_visibility="collapsed"
    )
with col2:
    search_pressed = st.button("Search Hostels", type="primary")

st.markdown('</div>', unsafe_allow_html=True)

# Results section
if search_pressed:
    if not query:
        st.warning("Please enter a search query to find hostels matching your preferences.")
    else:
        if not index or hostel_ids is None:
            st.error("Search index not available. Please try again later or contact support.")
        elif hostel_collection is None:
            st.error("Database connection not available. Please try again later or contact support.")
        else:
            with st.spinner("Finding the best hostels for you..."):
                query_embedding = get_embedding(query)
                if query_embedding is not None:
                    query_embedding = query_embedding.reshape(1, -1)
                    D, I = index.search(query_embedding, k=10)  # Get more results for filtering
                    
                    # Display results
                    st.markdown('<div class="results-section">', unsafe_allow_html=True)
                    
                    # Results header
                    st.markdown("""
                        <div class="results-header">
                            <h2 class="results-title">Search Results</h2>
                            <div class="results-count">Showing {count} hostels</div>
                        </div>
                    """.format(count=len(I[0]) if I[0][0] != -1 else 0), unsafe_allow_html=True)
                    
                    if I[0][0] == -1 or all(i == -1 for i in I[0]):
                        st.markdown("""
                            <div class="no-results">
                                <div class="no-results-icon">🏠</div>
                                <h3>No matching hostels found</h3>
                                <p>Try adjusting your search criteria or filters</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        found_results = 0
                        
                        for i in I[0]:
                            if i != -1 and 0 <= i < len(hostel_ids):
                                hostel_id = hostel_ids[i]
                                hostel = hostel_collection.find_one({"_id": ObjectId(hostel_id)})
                                
                                if hostel:
                                    # Apply filters
                                    hostel_rent = hostel.get('monthly_rent', 0)
                                    if not (price_range[0] <= hostel_rent <= price_range[1]):
                                        continue
                                    
                                    hostel_rating = float(hostel.get('ratings', 0))
                                    if hostel_rating < float(min_rating):
                                        continue
                                    
                                    if room_types:
                                        hostel_rooms = hostel.get('room_types', [])
                                        if not any(room.lower() in [r.lower() for r in hostel_rooms] for room in room_types):
                                            continue
                                    
                                    if facilities:
                                        hostel_facilities = hostel.get('facilities', [])
                                        if not any(facility.lower() in [f.lower() for f in hostel_facilities] for facility in facilities):
                                            continue
                                    
                                    found_results += 1
                                    
                                    # Prepare hostel data
                                    hostel_name = escape_html(hostel.get('name', 'Unknown Hostel'))
                                    hostel_location = escape_html(hostel.get('location', 'Location not specified'))
                                    hostel_rent = escape_html(hostel.get('monthly_rent', 'N/A'))
                                    hostel_description = escape_html(hostel.get('description', 'No description available'))
                                    rating_display = render_stars(hostel.get('ratings', '0'))
                                    is_new = is_new_hostel(hostel)
                                    
                                    # Display hostel card
                                    st.markdown(f"""
                                        <div class='hostel-card'>
                                            <div class='hostel-header'>
                                                <div>
                                                    <h3 class='hostel-name'>
                                                        {hostel_name}
                                                        {f'<span class="new-badge">NEW</span>' if is_new else ''}
                                                    </h3>
                                                    <div class='hostel-location'>
                                                        📍 {hostel_location}
                                                    </div>
                                                </div>
                                                <div class='hostel-price'>
                                                    ₹{hostel_rent}/mo
                                                </div>
                                            </div>
                                            
                                            <div class='hostel-rating'>
                                                <span class="star-filled">★</span>
                                                {rating_display} ({hostel.get('ratings', '0')})
                                            </div>
                                            
                                            <div class='hostel-description'>
                                                {hostel_description}
                                            </div>
                                            
                                            <div class='section-title'>Room Types</div>
                                            <div class='tags-container'>
                                    """, unsafe_allow_html=True)
                                    
                                    # Display room types
                                    if hostel.get('room_types'):
                                        for room in hostel['room_types']:
                                            st.markdown(f"""
                                                <div class='tag room-tag'>
                                                    🛏️ {escape_html(room)}
                                                </div>
                                            """, unsafe_allow_html=True)
                                    
                                    st.markdown("""
                                            </div>
                                            
                                            <div class='section-title'>Amenities</div>
                                            <div class='amenities-grid'>
                                    """, unsafe_allow_html=True)
                                    
                                    # Display amenities in a grid
                                    if hostel.get('facilities'):
                                        for facility in hostel['facilities'][:8]:  # Limit to 8 amenities
                                            st.markdown(f"""
                                                <div class='amenity-item'>
                                                    ✅ {escape_html(facility)}
                                                </div>
                                            """, unsafe_allow_html=True)
                                    
                                    st.markdown("""
                                            </div>
                                            
                                            <div class='section-title'>Contact Information</div>
                                            <div class='contact-section'>
                                    """, unsafe_allow_html=True)
                                    
                                    # Contact information
                                    contact_phone = escape_html(hostel.get('contact', {}).get('phone', 'Not provided'))
                                    contact_email = escape_html(hostel.get('contact', {}).get('email', 'Not provided'))
                                    
                                    st.markdown(f"""
                                                <div class='contact-item'>
                                                    📞 {contact_phone}
                                                </div>
                                                <div class='contact-item'>
                                                    ✉️ {contact_email}
                                                </div>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                        
                        if found_results == 0:
                            st.markdown("""
                                <div class="no-results">
                                    <div class="no-results-icon">🔍</div>
                                    <h3>No hostels match your filters</h3>
                                    <p>Try adjusting your filter criteria</p>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

# Featured hostels section when no search is performed
# Featured hostels section when no search is performed
if not search_pressed:
    st.markdown("""
        <style>
            .featured-title {
                color: #2E2E48;
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 1.5rem;
            }
            .hostel-card {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
                border-left: 4px solid #6C63FF;
            }
            .hostel-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 1rem;
            }
            .hostel-name {
                color: #2E2E48;
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }
            .hostel-location {
                color: #A3A3C2;
                font-size: 1rem;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .hostel-price {
                background: linear-gradient(to right, #6C63FF, #4D44DB);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-weight: 600;
                font-size: 1rem;
            }
            .hostel-rating {
                display: flex;
                align-items: center;
                gap: 5px;
                color: #2E2E48;
                font-weight: 600;
            }
            .star-filled {
                color: #FFC107;
            }
            .hostel-description {
                color: #2E2E48;
                line-height: 1.6;
                margin: 1rem 0;
            }
            .section-title {
                color: #2E2E48;
                font-weight: 600;
                font-size: 1.1rem;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #F0F0FA;
            }
            .tags-container {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin: 0.5rem 0;
            }
            .tag {
                background: #F0F0FA;
                color: #2E2E48;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
            }
            .facility-tag {
                background: #E6F7FF;
                color: #1890FF;
            }
            .new-badge {
                background-color: #FF6584;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="featured-title">Featured Hostels</div>', unsafe_allow_html=True)
    
    # Display 3 featured hostels from the database
    try:
        featured_hostels = hostel_collection.find().sort("ratings", -1).limit(3)
        
        for hostel in featured_hostels:
            with st.container():
                st.markdown('<div class="hostel-card">', unsafe_allow_html=True)
                
                # Header with name and price
                col1, col2 = st.columns([3, 1])
                with col1:
                    hostel_name = hostel.get('name', 'Unknown Hostel')
                    if is_new_hostel(hostel):
                        st.markdown(f'<div class="hostel-name">{escape_html(hostel_name)} <span class="new-badge">NEW</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="hostel-name">{escape_html(hostel_name)}</div>', unsafe_allow_html=True)
                    
                    hostel_location = hostel.get('location', 'Location not specified')
                    st.markdown(f'<div class="hostel-location">📍 {escape_html(hostel_location)}</div>', unsafe_allow_html=True)
                
                with col2:
                    hostel_rent = hostel.get('monthly_rent', 'N/A')
                    st.markdown(f'<div class="hostel-price">₹{escape_html(str(hostel_rent))}/mo</div>', unsafe_allow_html=True)
                
                # Rating
                rating_display = render_stars(hostel.get('ratings', '0'))
                st.markdown(f"""
                    <div class='hostel-rating'>
                        <span class="star-filled">★</span>
                        {rating_display} ({hostel.get('ratings', '0')})
                    </div>
                """, unsafe_allow_html=True)
                
                # Description
                hostel_description = hostel.get('description', 'No description available')
                st.markdown(f'<div class="hostel-description">{escape_html(hostel_description)}</div>', unsafe_allow_html=True)
                
                # Amenities
                st.markdown('<div class="section-title">Top Amenities</div>', unsafe_allow_html=True)
                
                if hostel.get('facilities'):
                    cols = st.columns(5)
                    for i, facility in enumerate(hostel['facilities'][:5]):
                        with cols[i % 5]:
                            st.markdown(f'<div class="tag facility-tag">✅ {escape_html(facility)}</div>', unsafe_allow_html=True)
                
                # View Details button
                st.markdown("""
                    <div style="text-align: center; margin-top: 1.5rem;">
                        <button style="background: #6C63FF; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 12px; font-weight: 600; cursor: pointer;">
                            View Details
                        </button>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Could not load featured hostels: {e}")
# Footer
st.markdown("""
    <div class="footer">
        <p>© 2025 Hostel Haven | Find your perfect student accommodation</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem; color: var(--gray);">
            Powered by AI & MongoDB Atlas
        </p>
    </div>
""", unsafe_allow_html=True)