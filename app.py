import streamlit as st
import pandas as pd
import requests
import openai
import os
import time
from dotenv import load_dotenv
from improved_voice_input import voice_input


# Load environment variables and set OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Add this at the top of your app.py file
st.set_page_config(
    page_title="BeautyMate",
    page_icon="💄",
    layout="wide"
)

# --------------------------
# 1. HERO BANNER + ANIMATION
# --------------------------
hero_html = """
<div style="
    background: linear-gradient(to right, #ffe0f0, #fce4ec);
    border-radius: 20px;
    padding: 40px 30px;
    margin-bottom: 30px;
    text-align: center;
    animation: fadeInSlide 1s ease-out;
">
    <h1 style="font-size: 3rem; margin-bottom: 0; color: #d63384; font-family: 'Montserrat', sans-serif;">Welcome to BeautyMate 💄</h1>
    <p style="font-size: 1.2rem; margin-top: 10px; color: #555">Your Personalized Beauty Product Recommender</p>
</div>

<style>
@keyframes fadeInSlide {
  0% { opacity: 0; transform: translateY(-30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# --------------------------
# 2. USER PROFILE SYSTEM
# --------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-header'>👤 Your Profile</div>", unsafe_allow_html=True)
    if 'profile' not in st.session_state:
        st.session_state.profile = {}

    name = st.text_input("Your Name", value=st.session_state.profile.get("name", ""))
    age_group = st.selectbox("Age Range", ["Under 18", "18-24", "25-34", "35-44", "45+"])
    skin_type = st.radio("Skin Type", ["Dry", "Oily", "Combination", "Normal"])

    st.session_state.profile = {
        "name": name,
        "age_group": age_group,
        "skin_type": skin_type
    }

# --------------------------
# 3. LOADING SKELETON STYLE
# --------------------------
skeleton_html = """
<div style='border-radius: 10px; background: linear-gradient(-90deg, #eeeeee 0%, #dddddd 50%, #eeeeee 100%); 
            background-size: 200% 100%; 
            animation: shimmer 1.5s infinite; height: 250px; width: 100%; margin: 10px 0;'>
</div>

<style>
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
"""


def display_loading_skeletons():
    cols = st.columns(2)
    for col in cols:
        col.markdown(skeleton_html, unsafe_allow_html=True)



# Use profile info to personalize greeting
if 'profile' in st.session_state and st.session_state.profile.get("name"):
    st.markdown(f"### 👋 Hello, {st.session_state.profile['name']}! Let's find what works best for your {st.session_state.profile['skin_type']} skin.")



# Custom CSS styling for the app
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main header styles */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #d63384;
        text-align: center;
        margin: 20px 0;
        font-family: 'Montserrat', sans-serif;
    }
    /* Sidebar header styles */
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
   
    .product-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
        border-radius: 12px;
        padding: 0;
        margin: 15px 0;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        overflow: hidden;
        border: none;
        position: relative;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }
    .card-image-container {
        height: 200px;
        overflow: hidden;
        position: relative;
    }
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    .product-card:hover .card-img {
        transform: scale(1.05);
    }
    .card-content {
        padding: 16px;
    }
    .card-title {
        font-size: 1.3rem;
        margin: 0 0 8px 0;
        color: #333;
        font-weight: 700;
        line-height: 1.3;
    }
    .card-brand {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 8px;
        font-style: italic;
    }
    .card-description {
        font-size: 0.95rem;
        line-height: 1.5;
        color: #555;
        margin-bottom: 12px;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #eee;
    }
    .card-price {
        font-size: 1.2rem;
        font-weight: 700;
        color: #d63384;
    }
    .card-rating {
        display: flex;
        align-items: center;
        background: #f8f9fa;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.85rem;
    }
    .card-category {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(214, 51, 132, 0.9);
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Chat container styles */
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin-top: 30px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .chat-header {
        font-size: 1.2rem;
        color: #d63384;
        margin-bottom: 10px;
        text-align: left;
        font-weight: bold;
    }
    .user-message {
        background: #e9ecef;
        border-radius: 15px 15px 3px 15px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-end;
        margin-left: auto;
    }
    .assistant-message {
        background: #fae3eb;
        color: #333;
        border-radius: 15px 15px 15px 3px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
    }
    .chat-input {
        margin-top: 15px;
    }
    /* Beauty consultant avatar */
    .consultant-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
        background-color: #d63384;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
    }

    /* Chat button and controls */
    .chat-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #d63384;
        color: white;
        border-radius: 50px;
        padding: 10px 20px;
        font-weight: bold;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 12px rgba(214, 51, 132, 0.4);
        z-index: 1001;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .chat-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(214, 51, 132, 0.5);
    }

    .chat-close {
        background: none;
        border: none;
        color: #666;
        font-size: 1.2rem;
        cursor: pointer;
        transition: color 0.3s ease;
    }

    .chat-close:hover {
        color: #d63384;
    }
    </style>
    """, unsafe_allow_html=True)


# MODIFIED: Function to fetch products with improved error handling and using sample data by default
def fetch_makeup_products(category=None, brand=None):
    # Default to sample data - more stable than relying on the external API
    sample_data = get_sample_products(category)

    # If we have enough sample data for the current request, just use that
    if len(sample_data) >= 5 or (category is not None and brand is not None):
        return sample_data

    # Try the API only as a fallback for more variety
    base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
    params = {}
    if category:
        params['product_type'] = category.lower()
    if brand:
        params['brand'] = brand.lower()

    try:
        # Increase timeout to prevent hanging but don't wait too long
        response = requests.get(base_url, params=params, timeout=5)
        if response.status_code == 200:
            products = response.json()
            if products:  # If we got valid data
                df = pd.DataFrame(products)
                if not df.empty:
                    return df
        # For any issues, silently fall back to sample data
        return sample_data
    except Exception:
        # Don't show warning, just use sample data
        return sample_data


# IMPROVED: Enhanced sample data function with more products and categories
def get_sample_products(category=None):
    # Create comprehensive sample data with different categories
    sample_data = [
        {
            "name": "Natural Glow Bronzer",
            "brand": "EarthLab Cosmetics",
            "price": "28.99",
            "image_link": "https://images.unsplash.com/photo-1599733594230-6b823276abcc?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "bronzer",
            "rating": 4.8,
            "description": "A natural bronzer that gives a sun-kissed glow."
        },
        {
            "name": "Radiant Blush Duo",
            "brand": "Pure Beauty",
            "price": "24.50",
            "image_link": "https://images.unsplash.com/photo-1581514578022-3aafd55bbe4b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "blush",
            "rating": 4.5,
            "description": "A dual-color blush for the perfect cheek definition."
        },
        {
            "name": "Long-lasting Matte Lipstick",
            "brand": "ColorPop",
            "price": "19.99",
            "image_link": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "lipstick",
            "rating": 4.7,
            "description": "A creamy matte lipstick that lasts all day."
        },
        {
            "name": "Waterproof Mascara",
            "brand": "Lash Focus",
            "price": "22.00",
            "image_link": "https://images.unsplash.com/photo-1591360236480-4ed861025fa1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "mascara",
            "rating": 4.6,
            "description": "Volumizing and lengthening mascara that's truly waterproof."
        },
        {
            "name": "Shimmer Eyeshadow Palette",
            "brand": "Glimmer",
            "price": "32.00",
            "image_link": "https://images.unsplash.com/photo-1583241119308-050d4c933519?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "eyeshadow",
            "rating": 4.9,
            "description": "A palette of 12 shimmer eyeshadows for creating stunning looks."
        },
        # Adding more sample data for variety
        {
            "name": "Hydrating Foundation",
            "brand": "SkinGlow",
            "price": "35.99",
            "image_link": "https://images.unsplash.com/photo-1590156206058-ae06662e566b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "foundation",
            "rating": 4.7,
            "description": "A moisturizing foundation for dry skin types."
        },
        {
            "name": "Precision Eyeliner",
            "brand": "Line Perfect",
            "price": "18.50",
            "image_link": "https://images.unsplash.com/photo-1631214503374-35d266ee804e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "eyeliner",
            "rating": 4.8,
            "description": "A fine-tip eyeliner for precise application."
        },
        {
            "name": "Brow Definer Pencil",
            "brand": "BrowMaster",
            "price": "16.99",
            "image_link": "https://images.unsplash.com/photo-1597225244660-1cd128c64284?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "eyebrow",
            "rating": 4.6,
            "description": "Define and shape your brows with this precision pencil."
        },
        {
            "name": "Creamy Lip Liner",
            "brand": "LipDefine",
            "price": "15.00",
            "image_link": "https://images.unsplash.com/photo-1600612253971-422e7f7faeb6?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "lip liner",
            "rating": 4.4,
            "description": "A smooth, non-drying lip liner that prevents feathering."
        },
        {
            "name": "Quick-Dry Nail Polish",
            "brand": "NailPro",
            "price": "12.99",
            "image_link": "https://images.unsplash.com/photo-1603481588273-2f908a9a7a1b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": "nail polish",
            "rating": 4.3,
            "description": "Fast-drying, chip-resistant nail polish in vibrant colors."
        }
    ]

    # Filter by category if specified
    if category and category.lower() != "all":
        filtered_data = [p for p in sample_data if p["product_type"].lower() == category.lower()]
        # If we have matching products, return those
        if filtered_data:
            return pd.DataFrame(filtered_data)

    # Return all sample data if no category specified or no matches
    if category and category.lower() != "all" and not any(
            p["product_type"].lower() == category.lower() for p in sample_data):
        # Add one generic product for the requested category
        sample_data.append({
            "name": f"Premium {category.title() if category else 'Beauty Product'}",
            "brand": "BeautyMate",
            "price": "25.00",
            "image_link": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "product_type": category.lower() if category else "makeup",
            "rating": 4.5,
            "description": f"A high-quality {category.lower() if category else 'beauty product'}."
        })

    return pd.DataFrame(sample_data)


# Generate personalized description using OpenAI
def generate_personalized_description(product, gender):
    try:
        # Check if OpenAI client is available
        client = openai.OpenAI() if hasattr(openai, 'OpenAI') else None
        
        if not client:
            # Improved fallback descriptions based on gender
            if gender.lower() == "male":
                return f"This premium {product['product_type']} is specially formulated for men's skin. It offers a natural finish and long-lasting performance for a confident look all day."
            elif gender.lower() == "female":
                return f"This luxurious {product['product_type']} is perfect for enhancing your natural beauty. It provides exceptional coverage and staying power for a flawless finish."
            else:
                return f"This versatile {product['product_type']} works beautifully for all users. It's carefully formulated to complement any look while providing professional-quality results."

        product_name = product.get('name', 'Product')
        brand = product.get('brand', 'Brand')
        category = product.get('product_type', 'Beauty Product')
        price = product.get('price', '0.00')
        rating = product.get('rating', 0)

        prompt = f"""
        Create a compelling 3-sentence product description for a beauty recommendation system.
        Product: {product_name}
        Brand: {brand}
        Category: {category}
        Price: ${price}
        Rating: {rating}/5
        Gender: {gender}

        Focus on why this product is perfect for {gender} users.
        Highlight its key benefits. Keep it professional but engaging.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful beauty product recommendation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # More detailed fallback descriptions based on product type and gender
        product_type = product.get('product_type', '').lower()

        if product_type == "foundation":
            return f"This foundation provides flawless coverage while letting your skin breathe. Perfect for {gender.lower()} users looking for a natural finish that lasts all day."
        elif product_type == "lipstick":
            return f"This richly pigmented lipstick offers vibrant color and moisturizing comfort. Specially formulated to complement {gender.lower()} users with long-lasting, crease-resistant wear."
        elif product_type == "mascara":
            return f"Achieve dramatic lashes with this volumizing and lengthening mascara. Designed for {gender.lower()} users who want smudge-proof definition that lasts from day to night."
        else:
            return f"This premium {product_type} delivers professional-quality results with every use. Specially formulated for {gender.lower()} users with high-performance ingredients for outstanding results."


# Display recommendations using Streamlit components with a grid layout
def display_recommendations(recommendations_df, gender):
    if recommendations_df.empty:
        st.warning("No matching products found. Try adjusting your preferences.")
        return

    # Create a better grid layout with columns
    num_products = len(recommendations_df)

    # Use two columns for better layout
    for i in range(0, num_products, 2):
        cols = st.columns(2)

        # First column
        with cols[0]:
            if i < num_products:
                product = recommendations_df.iloc[i]
                display_product_card(product, gender)

        # Second column
        with cols[1]:
            if i + 1 < num_products:
                product = recommendations_df.iloc[i + 1]
                display_product_card(product, gender)


# Helper function to display a single product card
def display_product_card(product, gender):
    with st.container():
        # Create the product card container
        st.markdown("""
        <div class="product-card">
            <div class="card-image-container">
                <img class="card-img" src="{image_url}" alt="{product_name}">
                <div class="card-category">{category}</div>
            </div>
            <div class="card-content">
                <h3 class="card-title">{product_name}</h3>
                <p class="card-brand">by {brand}</p>
                <p class="card-description">{description}</p>
                <div class="card-footer">
                    <span class="card-price">${price}</span>
                    <span class="card-rating">⭐ {rating}/5</span>
                </div>
            </div>
        </div>
        """.format(
            image_url=product.get('image_link', 'https://via.placeholder.com/400x200?text=Product+Image'),
            product_name=product.get('name', 'Product'),
            category=product.get('product_type', 'Beauty').title(),
            brand=product.get('brand', 'Brand'),
            description=generate_personalized_description(product, gender),
            price=float(product.get('price', 0)),
            rating=product.get('rating', '4.5')
        ), unsafe_allow_html=True)


# Beauty consultant response using locally defined responses when OpenAI is unavailable
def get_beauty_consultant_response(user_question, gender):
    try:
        # Check if OpenAI client is available
        client = openai.OpenAI() if hasattr(openai, 'OpenAI') else None
        
        if not client:
            # Common beauty questions and predefined responses
            beauty_qa = {
                "foundation": f"For choosing the right foundation, match it to your jawline in natural light. If you're {gender.lower()}, look for formulas designed for your skin type - dry, oily, or combination. Test a few shades to find your perfect match.",
                "lipstick": f"When selecting lipstick, consider your skin undertone - cool tones look best with blue-reds, warm tones with orange-reds. For {gender.lower()} users, matte formulas last longer while creams are more hydrating.",
                "eyeshadow": f"The best eyeshadows for {gender.lower()} users depend on your eye color. Brown eyes pop with purples and blues, green eyes with rusty reds, and blue eyes with warm bronzes and coppers. Start with a neutral palette for versatility.",
                "mascara": "For the best mascara application, wiggle the wand at the base of your lashes then sweep upward. Curling your lashes first creates an eye-opening effect, and you can layer for more drama.",
                "bronzer": f"Apply bronzer where the sun naturally hits: forehead, cheekbones, bridge of nose, and jawline. For {gender.lower()} users, choose a shade just 1-2 tones deeper than your skin for the most natural result.",
                "blush": "For blush placement, smile and apply to the apples of your cheeks, then blend upward toward your temples. Cream blushes work well for dry skin, while powders are better for oily skin.",
                "skincare": f"A basic skincare routine should include cleanser, moisturizer, and sunscreen. For {gender.lower()} users, add a serum with ingredients targeting your specific concerns like vitamin C for brightness or hyaluronic acid for hydration."
            }

            # Check if any keywords from the question match our predefined answers
            question_lower = user_question.lower()
            for keyword, response in beauty_qa.items():
                if keyword in question_lower:
                    return response

            # Generic response if no keywords match
            return f"Thank you for your beauty question! For {gender.lower()} users, I generally recommend starting with quality products suited to your skin type and tone. Could you provide more details about what specific beauty advice you're looking for?"

        prompt = f"""
        You are a professional beauty consultant named Sofi. The user has asked the following question:
        "{user_question}"

        Provide a helpful, personalized response about beauty products or techniques.
        User's gender preference: {gender}

        Keep your response friendly, concise (max 3-4 sentences), and actionable.
        Include specific product types when relevant, but don't mention specific brands.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Sofi, a knowledgeable and friendly virtual beauty consultant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Fall back to the keyword-based system if API fails
        question_lower = user_question.lower()
        for keyword, response in {
            "foundation": f"For {gender.lower()} users, I recommend matching foundation to your jawline in natural light. Look for formulas that suit your skin type. Consider testing samples before purchasing a full-size product.",
            "lipstick": f"When choosing lipstick colors for {gender.lower()} users, consider your undertone. Warm skin looks great with orange-reds, while cool skin pairs well with blue-reds and berries.",
            "eyeshadow": f"For {gender.lower()} users, I suggest starting with a neutral palette that complements your eye color. Apply lighter shades on the lid and darker colors in the crease for dimension.",
            "skincare": f"A good skincare routine for {gender.lower()} users includes cleansing, moisturizing, and sun protection. Add targeted treatments based on your specific concerns like acne, aging, or hyperpigmentation."
        }.items():
            if keyword in question_lower:
                return response

        return "I'd be happy to help with your beauty questions! For personalized recommendations, I need to know more about your skin type, concerns, and preferences. Could you share a bit more about what you're looking for?"


# Display Beauty Consultant Chat Interface with pop-out box



def display_beauty_consultant(gender):
    if 'chat_visible' not in st.session_state:
        st.session_state.chat_visible = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    
    # Show voice usage instructions if first time
    if 'voice_instructions_shown' not in st.session_state:
        st.session_state.voice_instructions_shown = True
        
        # Add an info box with voice usage instructions
        with st.sidebar:
            with st.expander("🎙️ Voice Input Instructions", expanded=True):
                st.markdown("""
                **Using Voice Input:**
                1. Click the "Speak now" button
                2. Allow microphone access if prompted
                3. Speak clearly after the button changes to "Listening..."
                4. Your speech will be converted to text and sent automatically
                
                **Troubleshooting:**
                - Use Chrome, Edge or Safari for best results
                - Ensure your microphone is working
                - Make sure you've granted microphone permissions
                - Speak clearly and not too quickly
                """)

    def add_welcome_message():
        if not any(msg["role"] == "assistant" and "I'm Sofi" in msg["content"] for msg in st.session_state.chat_history):
            st.session_state.chat_history.insert(0, {
                "role": "assistant",
                "content": f"Hi there! I'm Sofi, your virtual beauty consultant 💋. Ask me anything beauty-related like 'What blush suits dry skin?' or 'How to pick foundation for oily skin?'"
            })

    if st.session_state.chat_visible:
        add_welcome_message()

        st.markdown("""
        <style>
        @keyframes slideUpFade {
            0% {opacity: 0; transform: translateY(30px);}
            100% {opacity: 1; transform: translateY(0);}
        }
        .chat-container {
            animation: slideUpFade 0.5s ease-out;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.markdown("<div class='consultant-avatar'>💋</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div class='chat-header'>Beauty Consultant: Sofi</div>", unsafe_allow_html=True)
            with col3:
                if st.button("✕", key="close_chat"):
                    st.session_state.chat_visible = False
                    st.rerun()

            # Display message history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("#### 🎙️ Speak or type your question below:")
                voice_input_html = voice_input(language="en", key="voice_input")
                st.markdown(voice_input_html, unsafe_allow_html=True)
                st.text_input("Or type here:", key="user_question")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Send"):
                    user_input = st.session_state.get("user_question", "")
                    if user_input:
                        st.session_state.chat_history.append({"role": "user", "content": user_input})
                        with st.spinner("Sofi is thinking..."):
                            response = get_beauty_consultant_response(user_input, gender)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})

                        # Speak the response
                        safe_response = response.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
                        st.markdown(f"""
                            <script>
                            try {{
                                if ('speechSynthesis' in window) {{
                                    var msg = new SpeechSynthesisUtterance("{safe_response}");
                                    msg.lang = "en-US";
                                    window.speechSynthesis.speak(msg);
                                }}
                            }} catch(e) {{
                                console.error("Speech synthesis error:", e);
                            }}
                            </script>
                        """, unsafe_allow_html=True)

                        # 🔁 Clear user input safely to avoid Streamlit error
                        if "user_question" in st.session_state:
                            del st.session_state["user_question"]
                        st.rerun()
                    else:
                        st.warning("Please enter a question first!")

            st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.chat_visible:
        with st.container():
            st.markdown("""
            <div style='position: fixed; bottom: 80px; left: 20px; background-color: #fff0f6; padding: 8px 12px;
                        border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); z-index: 1000;'>
                Need Help? Ask Sofi 💬
            </div>
            """, unsafe_allow_html=True)
            if st.button("💋 Chat with Sofi", key="open_chat"):
                st.session_state.chat_visible = True
                st.rerun()

# Main Streamlit App Function
def main():
    # Initialize OpenAI client if API key is available
    client = openai.OpenAI() if hasattr(openai, 'OpenAI') and os.getenv("OPENAI_API_KEY") else None
    
    apply_custom_css()
    st.markdown("<div class='main-header'>💄 BeautyMate: Your Personalized Beauty Guide</div>", unsafe_allow_html=True)

    # --- Sidebar: User Preferences ---
    with st.sidebar:
        st.markdown("<div class='sidebar-header'>🎯 Your Preferences</div>", unsafe_allow_html=True)

        # Use sample data to build consistent filter lists, avoiding API failures
        sample_df = get_sample_products()
        available_categories = sorted(sample_df['product_type'].dropna().unique())
        available_brands = sorted(sample_df['brand'].dropna().unique())

        category = st.selectbox("Product Category", ["All"] + list(available_categories))
        brand = st.selectbox("Brand", ["All"] + list(available_brands))
        gender = st.selectbox("Gender", ["All", "Female", "Male", "Unisex"])
        price_range = st.slider("Price Range (USD)", min_value=0, max_value=100, value=(20, 80), step=5)
        rating_filter = st.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.5)

        if st.button("💫 Get Recommendations"):
            with st.spinner("Finding your perfect beauty match..."):
                # Use None if "All" is selected
                selected_category = None if category == "All" else category
                selected_brand = None if brand == "All" else brand

                # Fetch products based on filters
                products_df = fetch_makeup_products(selected_category, selected_brand)

                # Apply price and rating filters
                if not products_df.empty:
                    # Convert price to numeric
                    products_df['price'] = pd.to_numeric(products_df['price'], errors='coerce')
                    # Drop rows where price is NaN
                    filtered_df = products_df.dropna(subset=['price'])

                    # Apply price filter
                    price_min, price_max = price_range
                    filtered_df = filtered_df[
                        (filtered_df['price'] >= price_min) & (filtered_df['price'] <= price_max)
                        ]

                    # Apply rating filter if available
                    if 'rating' in filtered_df.columns:
                        filtered_df['rating'] = pd.to_numeric(filtered_df['rating'], errors='coerce')
                        filtered_df = filtered_df[filtered_df['rating'] >= rating_filter]

                    # Sort by rating (if available) or price
                    if 'rating' in filtered_df.columns and not filtered_df['rating'].isnull().all():
                        filtered_df = filtered_df.sort_values(by='rating', ascending=False)
                    else:
                        filtered_df = filtered_df.sort_values(by='price', ascending=True)

                    # Get top recommendations
                    recommendations = filtered_df.head(5)
                    st.session_state['recommendations'] = recommendations

                    # Store the category selection for chat bot display logic
                    st.session_state['selected_category'] = category
                else:
                    st.error("No products found. Try different criteria.")

    # --- Main Area: Display Recommendations ---
    if 'recommendations' in st.session_state:
        st.subheader("✨ Top Product Recommendations Just for You:")
        display_recommendations(st.session_state['recommendations'], gender)
    else:
        st.info("Use the sidebar to set your preferences and get personalized beauty product recommendations.")

    # Always display beauty consultant regardless of whether recommendations exist
    display_beauty_consultant(gender)


if __name__ == "__main__":
    main()