import streamlit as st
import os
import hashlib
from dotenv import load_dotenv
from openai import OpenAI
import base64
from pathlib import Path
import time
import uuid  # For unique identifiers


# Function to validate access codes
def is_valid_access_code(code):
    """Validate access code against list of valid hashed codes"""
    # You can generate these hashes by running:
    # hashlib.sha256("your-access-code".encode()).hexdigest()
    valid_hashes = [
        # Sample access codes - replace with your actual codes when setting up Gumroad
        "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
        "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f",  # "12345678"
        "d7e9d1492da79adcaf78e4794cc8c757a2f880c6df1957cc46dcc1d8392f9386",  # "alphabetapp"
        "82b2f8aad241550bca3801a65693cb54c59962db48b2f55d8ee553a820cb6736",  # "alphabet123"
        # Add more hashed access codes as needed
    ]
    
    # For freemium model, allow demo access
    if code.lower() == "demo":
        return True, "demo"
    
    # Hash the input code
    hashed_code = hashlib.sha256(code.encode()).hexdigest()
    
    # Check if hash matches any valid hash
    if hashed_code in valid_hashes:
        return True, "premium"
    
    return False, None


# Load environment variables from .env file with override=True
load_dotenv(override=True)

# Get API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Alphabet Learning Adventure",
    page_icon="📚",
    layout="wide"
)

# CSS for enhanced styling with animations and fun colors
custom_css = """
<style>
    /* General page style */
    .main {
        background-color: #f9f9f9;
        padding: 1rem 2rem;
    }

    /* Button Styling - More Playful with Bigger Font */
    .stButton > button {
        font-weight: bold !important;
        font-size: 48px !important;  /* Increased from 48px to 60px */
        line-height: 1 !important; /* Better vertical alignment */
        height: 60px !important;  /* Increased height to properly fit larger text */
        width: 100% !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
        padding: 0 !important; /* Removed padding to help centering */
        display: flex !important; /* Use flexbox for better centering */
        justify-content: center !important; /* Center horizontally */
        align-items: center !important; /* Center vertically */
        background-color: #87CEFA !important; /* Light sky blue background */
    }

    /* Make sure the button height works on mobile too */
    @media (max-width: 768px) {
        .stButton > button {
            height: 80px !important;
            font-size: 50px !important;  /* Slightly smaller on mobile */
        }
    }

    /* Button hover state - make it slightly lighter */
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.25) !important;
        background-color: #ADD8E6 !important; /* Lighter blue on hover */
    }

    /* Button active state */
    .stButton > button:active {
        transform: translateY(1px) scale(0.98) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        background-color: #1E90FF !important; /* Slightly darker when clicked */
    }

    /* Content Area Styling - More Fun */
    .content-box {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        margin-top: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: none;
        transition: all 0.3s ease;
    }
    
    .content-box:hover {
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
    }

    /* Example Word Styling - Colorful and Playful */
    .example-word {
        display: inline-block;
        background-color: #f0f0f0;
        color: #333;
        border-radius: 20px;
        padding: 10px 20px;
        margin: 8px;
        font-weight: 600;
        font-size: 18px;
        text-align: center;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    .example-word:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 10px rgba(0,0,0,0.15);
    }

    /* Letter Display Styling - More Vibrant */
    .letter-display {
        font-size: 150px;
        font-weight: bold;
        text-align: center;
        line-height: 1;
        transition: all 0.3s ease;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.15);
    }
    
    .letter-display:hover {
        transform: scale(1.05);
    }
    
    @media (min-width: 768px) {
      .letter-display {
          font-size: 180px;
          margin-right: 40px;
      }
    }

    /* Letter Info Text Styling - More Engaging */
    .letter-info {
        font-size: 20px;
        line-height: 1.7;
        color: #333;
    }
    
    .phonetic {
        font-style: italic;
        color: #555;
        margin-top: 5px;
        font-size: 18px;
        border-left: 3px solid #4CAF50;
        padding-left: 10px;
    }

    /* Section Headers - Colorful */
    .section-header {
        font-size: 24px;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 10px;
        display: inline-block;
        margin-bottom: 15px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }

    /* Example Words Container - More Engaging */
    .example-words-container {
        margin: 20px 0;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 15px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* Practice Time Section - Fun Design */
    .practice-section {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #FF9800;
    }
    
    .practice-title {
        color: #FF9800;
        font-size: 24px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    
    .practice-title::before {
        content: "🚀";
        margin-right: 10px;
    }

    /* Parents Tips Section - Distinct and Helpful */
    .parents-tips {
        margin-top: 25px;
        padding: 20px;
        background-color: #E3F2FD;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #2196F3;
    }
    
    .tips-title {
        color: #2196F3;
        font-size: 20px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    
    .tips-title::before {
        content: "💡";
        margin-right: 10px;
    }

    /* Gumroad styled button */
    .gumroad-button {
        display: inline-block;
        background-color: #FF90E8;
        color: #111;
        font-weight: bold;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 5px;
        transition: all 0.2s ease;
    }
    
    .gumroad-button:hover {
        background-color: #FF61C7;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
"""

# Inject the CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Add this new CSS right after your existing CSS code

compact_css = """
<style>
    /* More compact layout */
    .main {
        padding: 0.5rem 1rem !important;
    }
    
    /* More compact letter display */
    .letter-display {
        font-size: 100px !important; /* Slightly larger */
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        display: inline-block !important;
    }
    
    /* Content container for better spacing */
    .content-container {
        margin-top: 10px !important;
        padding: 15px !important;
        border-radius: 10px !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Letter heading for better proportion */
    .letter-heading {
        font-size: 36px !important; /* Increased from 28px */
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
        font-weight: bold !important;
    }
    
    /* Phonetic info larger */
    .phonetic-info {
        font-size: 20px !important; /* Increased from 14px */
        margin: 8px 0 !important;
        line-height: 1.3 !important;
    }
    
    /* Letter description larger */
    .letter-description {
        font-size: 24px !important; /* Increased from 16px */
        line-height: 1.4 !important;
        margin: 12px 0 !important;
    }
    
    /* Example word heading */
    .example-heading {
        font-size: 28px !important; /* Increased from 18px */
        margin: 15px 0 10px 0 !important;
        padding: 8px 15px !important;
        display: inline-block !important;
        font-weight: bold !important;
    }
    
    /* Example words larger */
    .example-word {
        font-size: 22px !important; /* Increased from 14px */
        padding: 8px 15px !important;
        margin: 5px !important;
        font-weight: bold !important;
    }
    
    /* Practice section larger */
    .practice-title {
        font-size: 28px !important; /* Increased from 18px */
        margin: 15px 0 10px 0 !important;
        font-weight: bold !important;
    }
    
    /* Practice list items */
    .practice-list {
        font-size: 22px !important; /* Increased from 14px */
        line-height: 1.5 !important;
        padding-left: 25px !important;
        margin: 10px 0 !important;
    }
    
    /* Tips section more compact but larger text */
    .tips-section {
        margin-top: 15px !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    
    /* Tips title larger */
    .tips-title {
        font-size: 24px !important; /* Increased from 16px */
        margin: 0 0 8px 0 !important;
        font-weight: bold !important;
    }
    
    /* Tips content */
    .tips-content {
        font-size: 22px !important; /* Increased from 14px */
        margin: 0 !important;
        line-height: 1.4 !important;
    }
    
    /* Footer slightly larger */
    footer {
        margin-top: 20px !important;
        font-size: 20px !important; /* Increased from 10px */
        padding: 8px !important;
    }
    
    /* Better responsive layout */
    @media (max-width: 768px) {
        .letter-row {
            flex-direction: row !important;
            align-items: center !important;
        }
        
        .letter-display {
            font-size: 80px !important;
            margin-right: 15px !important;
        }
    }
    
    /* Disabled letter buttons for demo mode */
    .disabled-letter {
        width: 100%;
        height: 60px;
        background-color: #e0e0e0;
        color: #999;
        border-radius: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 48px;
        font-weight: bold;
        box-shadow: none;
        cursor: not-allowed;
    }
</style>
"""

# Apply the compact CSS
st.markdown(compact_css, unsafe_allow_html=True)

# ---------------------------------------------
# Access Code Verification
# ---------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.access_level = None

# Check if this is a demo access request from URL

try:
    params = st.query_params
    if 'demo' in params and params['demo'] == 'true' and not st.session_state.authenticated:
        st.session_state.authenticated = True
        st.session_state.access_level = "demo"
except Exception as e:
    # Just log the error, don't show it to users
    print(f"Error checking query parameters: {e}")
    pass

if not st.session_state.authenticated:
    st.title("🔤 Alphabet Learning Adventure 🔤")
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #4285F4;">Welcome to Alphabet Learning Adventure!</h2>
        <p style="font-size: 1.2rem;">An interactive tool to help children learn the alphabet with audio pronunciations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Features
        * 🔤 Learn letters A-Z with fun, interactive cards
        * 🔊 Audio pronunciations with 6 different voice options 
        * 📝 Example words and practice exercises
        * 👨‍👩‍👧‍👦 Tips for parents and teachers
        """)
        
        st.markdown("### Try It Free!")
        if st.button("Start Free Demo", type="primary"):
            st.session_state.authenticated = True
            st.session_state.access_level = "demo"
            st.rerun()
        
        st.markdown("""
        <div style="font-size: 0.8rem; margin-top: 0.5rem;">
        Free demo includes access to letters A-F
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        ### Get Full Access
        Enter your access code to unlock all 26 letters and premium features
        """)
        
        access_code = st.text_input("Access Code", type="password")
        
        if st.button("Unlock Full Access"):
            is_valid, level = is_valid_access_code(access_code)
            if is_valid:
                st.session_state.authenticated = True
                st.session_state.access_level = level
                st.rerun()
            else:
                st.error("Invalid access code")
        
        st.markdown("""
        <div style="margin-top: 2rem;">
            <p>Don't have an access code?</p>
            <a href="https://lindsayhiebert.gumroad.com/l/alphabet-adventure" target="_blank" class="gumroad-button">Purchase on Gumroad</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0; padding: 1rem; background-color: #f8f9fa; border-radius: 10px;">
        <h3>Perfect for:</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="padding: 1rem;">👶 Preschoolers</div>
            <div style="padding: 1rem;">🏫 Classrooms</div>
            <div style="padding: 1rem;">🏠 Homeschooling</div>
            <div style="padding: 1rem;">👨‍👩‍👧‍👦 Families</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo footer
    st.markdown("""
    <footer style="margin-top: 20px; text-align: center; font-size: 18px; color: #555;">
        © 2025 Alphabet Learning Adventure. All rights reserved.<br>
        <strong>Developed and Designed by <a href="https://www.linkedin.com/in/lindsayhiebert/" target="_blank" style="text-decoration: none; color: #4285F4; font-weight: bold;">Lindsay Hiebert</a></strong>
    </footer>
    """, unsafe_allow_html=True)
    
    st.stop()

# Check if API key is available and valid
if not API_KEY or not API_KEY.startswith("sk-"):
    # Try to get from Streamlit secrets as fallback
    try:
        API_KEY = st.secrets["OPENAI_API_KEY"]
    except:
        pass
        
    # If still not available, show error
    if not API_KEY or not API_KEY.startswith("sk-"):
        st.error("⚠️ OpenAI API Key is missing or invalid. Please add it to your .env file or Streamlit secrets.")
        st.info("Create a .env file in your project directory with: OPENAI_API_KEY=your-api-key")
        st.stop()

try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {e}")
    st.stop()

# --- Data Definitions ---

# Letter phonetics information
phonetics = {
    'A': {'phonetic': '/eɪ/', 'type': 'vowel', 'sounds': 'long "a" as in "ace" or short "a" as in "apple"'},
    'B': {'phonetic': '/biː/', 'type': 'consonant', 'sounds': '"buh" sound'},
    'C': {'phonetic': '/siː/', 'type': 'consonant', 'sounds': 'hard "k" sound as in "cat" or soft "s" sound as in "city"'},
    'D': {'phonetic': '/diː/', 'type': 'consonant', 'sounds': '"duh" sound'},
    'E': {'phonetic': '/iː/', 'type': 'vowel', 'sounds': 'long "e" as in "eve" or short "e" as in "end"'},
    'F': {'phonetic': '/ɛf/', 'type': 'consonant', 'sounds': '"fff" sound'},
    'G': {'phonetic': '/dʒiː/', 'type': 'consonant', 'sounds': 'hard "g" as in "go" or soft "j" as in "gem"'},
    'H': {'phonetic': '/eɪtʃ/', 'type': 'consonant', 'sounds': '"huh" sound'},
    'I': {'phonetic': '/aɪ/', 'type': 'vowel', 'sounds': 'long "i" as in "ice" or short "i" as in "in"'},
    'J': {'phonetic': '/dʒeɪ/', 'type': 'consonant', 'sounds': '"juh" sound'},
    'K': {'phonetic': '/keɪ/', 'type': 'consonant', 'sounds': '"kuh" sound'},
    'L': {'phonetic': '/ɛl/', 'type': 'consonant', 'sounds': '"lll" sound'},
    'M': {'phonetic': '/ɛm/', 'type': 'consonant', 'sounds': '"mmm" sound'},
    'N': {'phonetic': '/ɛn/', 'type': 'consonant', 'sounds': '"nnn" sound'},
    'O': {'phonetic': '/oʊ/', 'type': 'vowel', 'sounds': 'long "o" as in "oak" or short "o" as in "ox"'},
    'P': {'phonetic': '/piː/', 'type': 'consonant', 'sounds': '"puh" sound'},
    'Q': {'phonetic': '/kjuː/', 'type': 'consonant', 'sounds': '"kwuh" sound (almost always followed by U)'},
    'R': {'phonetic': '/ɑr/', 'type': 'consonant', 'sounds': '"rrr" sound'},
    'S': {'phonetic': '/ɛs/', 'type': 'consonant', 'sounds': '"sss" sound'},
    'T': {'phonetic': '/tiː/', 'type': 'consonant', 'sounds': '"tuh" sound'},
    'U': {'phonetic': '/juː/', 'type': 'vowel', 'sounds': 'long "u" as in "use" or short "u" as in "up"'},
    'V': {'phonetic': '/viː/', 'type': 'consonant', 'sounds': '"vvv" sound'},
    'W': {'phonetic': '/ˈdʌbəl.juː/', 'type': 'consonant', 'sounds': '"wuh" sound'},
    'X': {'phonetic': '/ɛks/', 'type': 'consonant', 'sounds': '"ks" sound as in "box" or "z" sound at the beginning of words'},
    'Y': {'phonetic': '/waɪ/', 'type': 'both', 'sounds': 'consonant sound "yuh" or vowel sounds "ee" as in "happy" or "eye" as in "my"'},
    'Z': {'phonetic': '/ziː/', 'type': 'consonant', 'sounds': '"zzz" sound'}
}

# Define a vibrant, child-friendly color palette for buttons# Updated button colors - Google-inspired vibrant palette
button_colors = {
    'A': '#EA4335',  # Google Red
    'B': '#FBBC05',  # Google Yellow
    'C': '#34A853',  # Google Green
    'D': '#4285F4',  # Google Blue
    'E': '#FF5252',  # Bright Red
    'F': '#FF9800',  # Bright Orange
    'G': '#FFCA28',  # Amber
    'H': '#66BB6A',  # Strong Green
    'I': '#26C6DA',  # Cyan
    'J': '#42A5F5',  # Bright Blue
    'K': '#7E57C2',  # Deep Purple
    'L': '#EC407A',  # Pink
    'M': '#AB47BC',  # Purple
    'N': '#EF5350',  # Light Red
    'O': '#FFA726',  # Orange
    'P': '#FFEE58',  # Yellow
    'Q': '#9CCC65',  # Light Green
    'R': '#26A69A',  # Teal
    'S': '#29B6F6',  # Light Blue
    'T': '#5C6BC0',  # Indigo
    'U': '#EC407A',  # Pink
    'V': '#66BB6A',  # Green
    'W': '#FFA000',  # Amber
    'X': '#EF5350',  # Light Red
    'Y': '#AB47BC',  # Purple
    'Z': '#42A5F5'   # Blue
}

# Updated word colors with high contrast
word_colors = [
    "#D32F2F",  # Deep Red
    "#F57C00",  # Deep Orange
    "#7B1FA2",  # Deep Purple
    "#0288D1",  # Strong Blue
    "#388E3C",  # Strong Green
    "#C2185B",  # Deep Pink
    "#0097A7",  # Deep Cyan
    "#FBC02D",  # Strong Yellow
    "#512DA8",  # Deep Purple
    "#E64A19"   # Deep Orange Red
]
    
# Background colors with better contrast
bg_colors = [
    "#FFCDD2",  # Light Red (higher contrast)
    "#FFE0B2",  # Light Orange
    "#E1BEE7",  # Light Purple
    "#BBDEFB",  # Light Blue
    "#C8E6C9",  # Light Green
    "#F8BBD0",  # Light Pink
    "#B2EBF2",  # Light Cyan
    "#FFF9C4",  # Light Yellow
    "#D1C4E9",  # Light Purple
    "#FFCCBC"   # Light Orange Red
]
# Letters and their information
letter_data = {
    'A': {
        'word': 'Apple',
        'text': "A is for Apple. The letter A is used at the beginning of many words like Acorn, Adventure, and Amazing. It's the first letter of the alphabet and makes both long and short sounds.",
        'examples': ['Apple', 'Acorn', 'Adventure', 'Amazing']
    },
    'B': {
        'word': 'Ball',
        'text': "B is for Ball. The letter B makes a bouncy sound at the beginning of words like Balloon, Butterfly, and Banana. Can you think of other words that start with B?",
        'examples': ['Ball', 'Balloon', 'Butterfly', 'Banana']
    },
    'C': {
        'word': 'Cat',
        'text': "C is for Cat. The letter C can make two different sounds. It sounds like 'k' in words like Cat and Cookie, and it sounds like 's' in words like Circle.",
        'examples': ['Cat', 'Cookie', 'Circle', 'Car']
    },
    'D': {
        'word': 'Dog',
        'text': "D is for Dog. The letter D makes a strong sound at the start of words like Donut, Dinosaur, and Dance. Can you try making the 'd' sound?",
        'examples': ['Dog', 'Donut', 'Dinosaur', 'Dance']
    },
    'E': {
        'word': 'Elephant',
        'text': "E is for Elephant. The letter E appears in many words like Egg, Eagle, and Exit. It can make different sounds depending on the word.",
        'examples': ['Elephant', 'Egg', 'Eagle', 'Exit']
    },
    'F': {
        'word': 'Fish',
        'text': "F is for Fish. The letter F makes a sound like blowing air between your teeth and lip in words like Frog, Flower, and Friend.",
        'examples': ['Fish', 'Frog', 'Flower', 'Friend']
    },
    'G': {
        'word': 'Goat',
        'text': "G is for Goat. The letter G can sound like 'g' in words like Garden and Goat, or like 'j' in words like Giraffe when followed by e, i, or y.",
        'examples': ['Goat', 'Garden', 'Giraffe', 'Gum']
    },
    'H': {
        'word': 'House',
        'text': "H is for House. The letter H makes a sound like breathing out in words like Hat, Horse, and Heart. Sometimes H is silent in words like 'hour'.",
        'examples': ['House', 'Hat', 'Horse', 'Heart']
    },
    'I': {
        'word': 'Ice Cream',
        'text': "I is for Ice Cream. The letter I is used in words like Igloo, Island, and Insect. It can make both long and short sounds.",
        'examples': ['Ice Cream', 'Igloo', 'Island', 'Insect']
    },
    'J': {
        'word': 'Jellyfish',
        'text': "J is for Jellyfish. The letter J makes a 'juh' sound at the beginning of words like Juice, Jump, and Jungle.",
        'examples': ['Jellyfish', 'Juice', 'Jump', 'Jungle']
    },
    'K': {
        'word': 'Kite',
        'text': "K is for Kite. The letter K makes a sound like 'k' in words like Kangaroo, King, and Kitchen.",
        'examples': ['Kite', 'Kangaroo', 'King', 'Kitchen']
    },
    'L': {
        'word': 'Lion',
        'text': "L is for Lion. The letter L makes a sound with your tongue touching the roof of your mouth in words like Lemon, Leaf, and Love.",
        'examples': ['Lion', 'Lemon', 'Leaf', 'Love']
    },
    'M': {
        'word': 'Moon',
        'text': "M is for Moon. The letter M makes a sound with your lips closed in words like Monkey, Mountain, and Magic.",
        'examples': ['Moon', 'Monkey', 'Mountain', 'Magic']
    },
    'N': {
        'word': 'Nest',
        'text': "N is for Nest. The letter N makes a sound with your tongue on the roof of your mouth in words like Night, Nose, and Number.",
        'examples': ['Nest', 'Night', 'Nose', 'Number']
    },
    'O': {
        'word': 'Octopus',
        'text': "O is for Octopus. The letter O appears in words like Orange, Owl, and Ocean. It can make different sounds depending on the word.",
        'examples': ['Octopus', 'Orange', 'Owl', 'Ocean']
    },
    'P': {
        'word': 'Penguin',
        'text': "P is for Penguin. The letter P makes a popping sound with your lips in words like Pumpkin, Pizza, and Park.",
        'examples': ['Penguin', 'Pumpkin', 'Pizza', 'Park']
    },
    'Q': {
        'word': 'Queen',
        'text': "Q is for Queen. The letter Q is almost always followed by the letter U, and together they make a 'kw' sound in words like Question, Quilt, and Quiet.",
        'examples': ['Queen', 'Question', 'Quilt', 'Quiet']
    },
    'R': {
        'word': 'Rainbow',
        'text': "R is for Rainbow. The letter R makes a sound like a growling dog in words like Robot, Rocket, and Rain.",
        'examples': ['Rainbow', 'Robot', 'Rocket', 'Rain']
    },
    'S': {
        'word': 'Sun',
        'text': "S is for Sun. The letter S makes a hissing sound in words like Star, Snake, and Sand.",
        'examples': ['Sun', 'Star', 'Snake', 'Sand']
    },
    'T': {
        'word': 'Tree',
        'text': "T is for Tree. The letter T makes a sound with your tongue tapping the roof of your mouth in words like Tiger, Train, and Turtle.",
        'examples': ['Tree', 'Tiger', 'Train', 'Turtle']
    },
    'U': {
        'word': 'Umbrella',
        'text': "U is for Umbrella. The letter U appears in words like Unicorn, Ukulele, and Under. It can make different sounds depending on the word.",
        'examples': ['Umbrella', 'Unicorn', 'Ukulele', 'Under']
    },
    'V': {
        'word': 'Volcano',
        'text': "V is for Volcano. The letter V makes a sound with your top teeth on your bottom lip in words like Violin, Vegetable, and Vacation.",
        'examples': ['Volcano', 'Violin', 'Vegetable', 'Vacation']
    },
    'W': {
        'word': 'Whale',
        'text': "W is for Whale. The letter W makes a sound like blowing out a candle in words like Water, Window, and Wagon.",
        'examples': ['Whale', 'Water', 'Window', 'Wagon']
    },
    'X': {
        'word': 'X-ray',
        'text': "X is for X-ray. The letter X makes a sound like 'ks' in words like Box and Fox. At the beginning of words like Xylophone, it sounds like 'z'.",
        'examples': ['X-ray', 'Xylophone', 'Fox', 'Box']
    },
    'Y': {
        'word': 'Yo-yo',
        'text': "Y is for Yo-yo. The letter Y can be both a consonant and a vowel. It makes a 'y' sound in words like Yellow, Yogurt, and Yacht.",
        'examples': ['Yo-yo', 'Yellow', 'Yogurt', 'Yacht']
    },
    'Z': {
        'word': 'Zebra',
        'text': "Z is for Zebra. The letter Z makes a buzzing sound in words like Zoo, Zipper, and Zero.",
        'examples': ['Zebra', 'Zoo', 'Zipper', 'Zero']
    }
}

# Add color to each letter's data
for letter in letter_data:
    letter_data[letter]['color'] = button_colors.get(letter, '#6A7FDB') # Default blue if color missing

# --- Utility Functions ---

# Helper function to lighten colors for backgrounds
def lighten_color(hex_color, factor=0.6):
    """Lighten a color by the given factor (0-1)."""
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Lighten
    rgb_lightened = [min(255, int(c + (255 - c) * factor)) for c in rgb]
    
    # Convert back to hex
    return f'#{rgb_lightened[0]:02x}{rgb_lightened[1]:02x}{rgb_lightened[2]:02x}'

# Function to get a better contrast text color
def get_contrast_color(background_hex):
    """Return black or white text color for best contrast with background"""
    # Convert hex to RGB
    bg_hex = background_hex.lstrip('#')
    r, g, b = int(bg_hex[0:2], 16), int(bg_hex[2:4], 16), int(bg_hex[4:6], 16)
    
    # Calculate luminance - brighter colors have higher values
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Return black for bright backgrounds, white for dark ones
    return "#000000" if luminance > 0.55 else "#FFFFFF"

# Fix for the example words function
def display_example_words(letter, words):
    """Display example words with vibrant, varied colors using components that Streamlit can render properly."""
    # Create a color palette for the example words
    word_colors = [
        "#FF5252", "#FF9800", "#FFEB3B", "#8BC34A", "#4CAF50", 
        "#009688", "#00BCD4", "#03A9F4", "#2196F3", "#3F51B5"
    ]
    
    # Background colors (lighter versions)
    bg_colors = [
        "#FFEBEE", "#FFF3E0", "#FFFDE7", "#F1F8E9", "#E8F5E9", 
        "#E0F2F1", "#E0F7FA", "#E1F5FE", "#E3F2FD", "#EDE7F6"
    ]
    
    # Create header
    header_color = button_colors[letter]
    header_bg_color = lighten_color(header_color, 0.8)
    
    # Use st.container and st.write for the header
    container = st.container()
    container.markdown(f"""
    <h3 style="color: {header_color}; background-color: {header_bg_color}; 
            padding: 8px 16px; border-radius: 10px; display: inline-block; 
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
        Words that start with {letter}
    </h3>
    """, unsafe_allow_html=True)
    
    # Display words in columns
    cols = st.columns(len(words))
    for i, word in enumerate(words):
        color_index = i % len(word_colors)
        word_color = word_colors[color_index]
        bg_color = bg_colors[color_index]
        
        cols[i].markdown(f"""
        <div style="color: {word_color}; background-color: {bg_color}; 
                border: 2px solid {word_color}; border-radius: 20px; 
                padding: 8px 15px; margin: 5px; font-weight: 600; 
                font-size: 18px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
            {word}
        </div>
        """, unsafe_allow_html=True)

# Fix for the practice section
def display_practice_section(letter, word):
    """Display practice section using Streamlit components that render properly."""
    letter_color = button_colors[letter]
    
    # Create container for practice section
    practice_container = st.container()
    
    # Practice title
    practice_container.markdown(f"""
    <h3 style="color: {letter_color}; font-size: 24px; margin-bottom: 15px;">
        🚀 Practice Time!
    </h3>
    """, unsafe_allow_html=True)
    
    # Practice items
    practice_container.markdown(f"""
    <ul style="font-size: 18px; line-height: 1.8; padding-left: 25px;">
        <li><strong>{word}</strong> starts with the letter <strong style="color: {letter_color};">{letter}</strong>.</li>
        <li>I can write the letter <strong style="color: {letter_color};">{letter}</strong> like this: <span style="font-family: cursive; font-size: 24px; color: {letter_color};">{letter.upper()} {letter.lower()}</span></li>
        <li>Can you think of more words that start with <strong style="color: {letter_color};">{letter}</strong>?</li>
    </ul>
    """, unsafe_allow_html=True)
    
    # Tips section
    st.markdown("""
    <div style="margin-top: 25px; padding: 20px; background-color: #E3F2FD; 
            border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
            border-left: 5px solid #2196F3;">
        <h4 style="color: #2196F3; font-size: 20px; margin-bottom: 15px;">
            💡 Tips for Grown-ups
        </h4>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <p>Ask the child to find objects around them that start with the letter <strong style="color: {letter_color};">{letter}</strong>. Make it a fun scavenger hunt!</p>
    </div>
    """, unsafe_allow_html=True)


# Function to create and get audio for a letter
def get_letter_audio(letter, voice="nova", model="tts-1"):
    """
    Generate or retrieve audio for a letter. Returns the file path to the audio file.
    """
    audio_dir = Path("audio_files")
    audio_dir.mkdir(exist_ok=True)
    
    # Create a consistent filename based on letter, voice and model
    file_path = audio_dir / f"letter_{letter}_{voice}_{model}.mp3"
    
    # Only generate if file doesn't exist yet
    if not file_path.exists():
        try:
            letter_info = letter_data[letter]
            phonetic_info = phonetics[letter]
            
            # Create text to be spoken
            tts_text = f"The letter {letter}. {letter} is for {letter_info['word']}. {letter_info['text']} It is a {phonetic_info['type']} that makes the {phonetic_info['sounds']}."
            
            # Show spinner during generation
            with st.spinner(f"Generating audio for letter {letter}..."):
                # Generate speech using OpenAI
                response = client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=tts_text
                )
                
                # Save the response to a file
                with open(file_path, "wb") as f:
                    # Write the content in chunks to avoid memory issues
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                
        except Exception as e:
            st.error(f"Error generating audio for '{letter}': {str(e)}")
            # Clean up potentially corrupted file
            if file_path.exists():
                try:
                    file_path.unlink()  # Delete the file
                except Exception:
                    pass
            return None
    
    # Return the path if file exists
    if file_path.exists():
        return str(file_path)
    else:
        return None

# Function for reliable autoplay
def autoplay_audio(file_path):
    """
    Create an audio element with autoplay for the given file path.
    Returns if the audio was successfully embedded.
    """
    if not os.path.exists(file_path):
        st.warning(f"Audio file not found: {file_path}")
        return False
    
    try:
        # Read the audio file
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        
        # Convert to base64
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Generate a unique ID to avoid browser caching issues
        unique_id = f"audio_{uuid.uuid4().hex}"
        
        # Create HTML with both autoplay and controls visible
        audio_html = f"""
        <audio id="{unique_id}" autoplay controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        <script>
            // Ensure the audio plays by explicitly calling play()
            (function() {{
                var audio = document.getElementById("{unique_id}");
                if (audio) {{
                    var playPromise = audio.play();
                    if (playPromise !== undefined) {{
                        playPromise.catch(function(error) {{
                            console.log("Autoplay prevented:", error);
                            // Show play button without requiring user to click play twice
                        }});
                    }}
                }}
            }})();
        </script>
        """
        
        # Insert the HTML
        st.markdown(audio_html, unsafe_allow_html=True)
        return True
        
    except Exception as e:
        st.error(f"Error playing audio: {e}")
        return False
    
# Update the display_example_words_compact function
def display_example_words_compact(letter, words):
    """Display example words in a compact, responsive layout with better contrast and larger fonts."""
    header_color = button_colors[letter]
    header_bg_color = lighten_color(header_color, 0.8)
    header_text_color = get_contrast_color(header_bg_color)
    
    # Create a single row for all words
    st.markdown(f"""
    <h4 style="color: {header_text_color}; background-color: {header_bg_color}; 
            font-size: 28px; margin: 15px 0 10px 0; padding: 8px 15px; 
            border-radius: 10px; display: inline-block; font-weight: bold;">
        Words that start with {letter}
    </h4>
    """, unsafe_allow_html=True)
    
    # Calculate number of columns based on number of words
    num_cols = min(4, len(words))  # Max 4 columns, or fewer if fewer words
    cols = st.columns(num_cols)
    
    # Display words in a compact grid
    for i, word in enumerate(words):
        col_index = i % num_cols
        color_index = i % len(word_colors)
        
        word_color = word_colors[color_index]
        bg_color = bg_colors[color_index]
        text_color = get_contrast_color(bg_color)
        
        cols[col_index].markdown(f"""
        <div style="color: {text_color}; background-color: {bg_color}; 
                border: 2px solid {word_color}; border-radius: 15px; 
                padding: 8px 15px; margin: 5px 0; font-weight: bold; 
                font-size: 22px; text-align: center;">
            {word}
        </div>
        """, unsafe_allow_html=True)

# Update the display_practice_section_compact function
def display_practice_section_compact(letter, word):
    """Display practice section in a compact, responsive layout with larger fonts."""
    letter_color = button_colors[letter]
    
    # Practice title
    st.markdown(f"""
    <h4 style="color: {letter_color}; font-size: 28px; margin: 15px 0 10px 0; 
            display: flex; align-items: center; font-weight: bold;">
        <span style="margin-right: 5px;">🚀</span> Practice Time!
    </h4>
    """, unsafe_allow_html=True)
    
    # Practice items in a compact list with larger font
    st.markdown(f"""
    <ul style="font-size: 22px; line-height: 1.5; padding-left: 25px; margin: 10px 0;">
        <li><strong>{word}</strong> starts with the letter <strong style="color: {letter_color};">{letter}</strong>.</li>
        <li>I can write the letter <strong style="color: {letter_color};">{letter}</strong> like this: <span style="font-family: cursive; font-size: 26px; color: {letter_color};">{letter.upper()} {letter.lower()}</span></li>
        <li>Can you think of more words that start with <strong style="color: {letter_color};">{letter}</strong>?</li>
    </ul>
    """, unsafe_allow_html=True)
    
    # Tips section with larger font
    st.markdown(f"""
    <div style="margin-top: 15px; padding: 15px; background-color: #E3F2FD; 
              border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
              border-left: 3px solid #2196F3;">
        <h5 style="color: #2196F3; font-size: 24px; margin: 0 0 8px 0; 
                display: flex; align-items: center; font-weight: bold;">
            <span style="margin-right: 5px;">💡</span> Tips for Grown-ups
        </h5>
        <p style="font-size: 22px; margin: 0; line-height: 1.4;">
            Ask the child to find objects around them that start with the letter <strong style="color: {letter_color};">{letter}</strong>. Make it a fun scavenger hunt!
        </p>
    </div>
    """, unsafe_allow_html=True)

# Update the display_letter_content_compact function
def display_letter_content_compact(letter, letter_info, phonetic_info):
    """Display letter content in a compact, responsive layout using a two-column approach with larger fonts."""
    
    # Create a container for the entire content
    with st.container():
        # Two columns for letter display and info
        col1, col2 = st.columns([1, 3])
        
        # Letter display in first column
        with col1:
            st.markdown(f"""
            <div style="text-align: center;">
                <span style="font-size: 100px; font-weight: bold; color: {letter_info['color']}; 
                      text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">{letter}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Letter info in second column
        with col2:
            st.markdown(f"""
            <h3 style="color: {letter_info['color']}; font-size: 36px; margin: 0; line-height: 1.2; font-weight: bold;">
                {letter} is for {letter_info['word']}
            </h3>
            <div style="font-style: italic; color: #555; font-size: 20px; margin: 8px 0;">
                Phonetic: {phonetic_info['phonetic']} • Type: {phonetic_info['type'].capitalize()}
            </div>
            <p style="font-size: 24px; line-height: 1.4; margin: 12px 0;">
                {letter_info['text']}
            </p>
            """, unsafe_allow_html=True)
    
    # Display example words with the compact function
    display_example_words_compact(letter, letter_info['examples'])
    
    # Display practice section with the compact function
    display_practice_section_compact(letter, letter_info['word'])
    
# Initialize session state for tracking app state
if 'selected_letter' not in st.session_state:
    st.session_state.selected_letter = None

if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None

if 'current_voice' not in st.session_state:
    st.session_state.current_voice = "nova"  # Default voice

if 'current_tts_model' not in st.session_state:
    st.session_state.current_tts_model = "tts-1"  # Default model

if 'autoplay' not in st.session_state:
    st.session_state.autoplay = True  # Default is to autoplay

if 'show_details' not in st.session_state:
    st.session_state.show_details = False  # Default is to hide details

if 'audio_counter' not in st.session_state:
    st.session_state.audio_counter = 0  # Counter to force audio refresh

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Show access level info
    access_level = st.session_state.access_level
    if access_level == "demo":
        st.info("You're using the FREE demo version with access to letters A-F")
        # Add upgrade link
        st.markdown("""
        <div style="margin: 1rem 0;">
            <a href="https://lindsayhiebert.gumroad.com/l/alphabet-adventure" target="_blank" class="gumroad-button" style="display: inline-block; background-color: #FF90E8; color: #111; font-weight: bold; padding: 0.5rem 1rem; text-decoration: none; border-radius: 5px; text-align: center; width: 100%;">Upgrade for Full Access</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("You have PREMIUM access to all 26 letters")
    
    # Voice selection
    voice_options = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"]
    voice_index = voice_options.index(st.session_state.current_voice) if st.session_state.current_voice in voice_options else 0
    
    # Limit voice options for demo users
    if access_level == "demo":
        voice_options = ["nova"]
        voice_index = 0
        
    new_voice = st.selectbox(
        "Select voice:",
        voice_options,
        index=voice_index,
        disabled=(access_level == "demo")
    )
    
    if access_level == "demo" and len(voice_options) == 1:
        st.caption("More voices available with premium access")
    
    # Check if voice changed
    if new_voice != st.session_state.current_voice:
        st.session_state.current_voice = new_voice
        # Reset audio if letter is selected
        if st.session_state.selected_letter:
            # Force audio refresh when voice changes
            st.session_state.audio_counter += 1
    
    # TTS model selection
    model_options = ["tts-1", "tts-1-hd"]
    model_index = model_options.index(st.session_state.current_tts_model) if st.session_state.current_tts_model in model_options else 0
    
    # Limit model options for demo users
    if access_level == "demo":
        model_options = ["tts-1"]
        model_index = 0
    
    new_model = st.selectbox(
        "TTS Model:",
        model_options,
        index=model_index,
        help="tts-1 is faster, tts-1-hd has higher quality audio.",
        disabled=(access_level == "demo")
    )
    
    if access_level == "demo" and len(model_options) == 1:
        st.caption("HD audio available with premium access")
    
    # Check if model changed
    if new_model != st.session_state.current_tts_model:
        st.session_state.current_tts_model = new_model
        # Reset audio if letter is selected
        if st.session_state.selected_letter:
            # Force audio refresh when model changes
            st.session_state.audio_counter += 1
    
    # Autoplay option
    new_autoplay = st.checkbox(
        "Autoplay audio", 
        value=st.session_state.autoplay,
        help="Automatically play audio when a letter is selected."
    )
    
    # Check if autoplay setting changed
    if new_autoplay != st.session_state.autoplay:
        st.session_state.autoplay = new_autoplay
    
    # Advanced view option - only for premium users
    if access_level != "demo":
        st.session_state.show_details = st.checkbox(
            "Show details & JSON", 
            value=st.session_state.show_details,
            help="Display detailed phonetic information and JSON data."
        )
    
    st.markdown("---")
    st.write("### About")
    st.info("Click a letter button to learn about it and hear its sound!")
    
    st.markdown("### For Parents & Teachers")
    st.success(
        "- Encourage children to repeat sounds.\n"
        "- Practice writing letters.\n"
        "- Find objects starting with the letter.\n"
        "- Use example words for vocabulary."
    )
    
    # Reset/Logout button

    if st.button("Start Over"):
    # Make a copy of the keys to avoid modifying the dictionary during iteration
        keys_to_delete = list(st.session_state.keys())
        for key in keys_to_delete:
            del st.session_state[key]
        st.rerun()

# --- Main content ---
st.title("🔤 Alphabet Learning Adventure 🔤  ")

# Audio container that will be filled with audio player
audio_container = st.empty()

# Create the buttons in a grid
st.subheader("Click a Letter! to hear its pronunciation and learn about it!")

# For demo access, only show A-F or show all letters with some disabled
full_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
if st.session_state.access_level == "demo":
    active_alphabet = "ABCDEF"
    st.info("🔑 You're using the free demo version with access to letters A-F. [Get full access](https://lindsayhiebert.gumroad.com/l/alphabet-adventure) to unlock all 26 letters!")
else:
    active_alphabet = full_alphabet

# Create grid of 7 columns for letters
cols = st.columns(7)

# Collect CSS rules for all buttons
button_css_rules = []

# Display active letter buttons
for i, letter in enumerate(active_alphabet):
    col_index = i % 7
    color = button_colors[letter]
    
    # Button key for unique identification
    button_key = f"btn_{letter}"
    
    # Determine text color based on background lightness
    text_color = get_contrast_color(color)
    
    # Add CSS rule for this button
    button_css_rules.append(f"""
    div[data-testid="stButton"] > button[kind="secondary"][data-testid="{button_key}"] {{
        background-color: {color} !important;
        color: {text_color} !important;
        border: none !important;
    }}
    """)
    
    with cols[col_index]:
        if st.button(letter, key=button_key, use_container_width=True):
            # Set the selected letter
            st.session_state.selected_letter = letter
            
            # Increment counter to force audio refresh
            st.session_state.audio_counter += 1
            
            # Rerun to update UI
            st.rerun()

# If in demo mode, show remaining letters as disabled
if st.session_state.access_level == "demo":
    # Calculate remaining columns in the current row
    remaining_in_row = 7 - (len(active_alphabet) % 7)
    if remaining_in_row < 7:
        for _ in range(remaining_in_row):
            cols[len(active_alphabet) % 7 + _].empty()
    
    # Create new rows for remaining letters
    remaining_letters = full_alphabet[len(active_alphabet):]
    
    # Create necessary new rows
    rows_needed = (len(remaining_letters) + 6) // 7  # Ceiling division
    
    for row in range(rows_needed):
        new_cols = st.columns(7)
        for j in range(7):
            idx = row * 7 + j
            if idx < len(remaining_letters):
                letter = remaining_letters[idx]
                with new_cols[j]:
                    st.markdown(f"""
                    <div class="disabled-letter">
                        {letter}
                    </div>
                    """, unsafe_allow_html=True)

# Apply CSS rules for button colors
st.markdown(f"<style>{''.join(button_css_rules)}</style>", unsafe_allow_html=True)

# Content section
if st.session_state.selected_letter:
    letter = st.session_state.selected_letter
    
    if letter in letter_data:
        letter_info = letter_data[letter]
        phonetic_info = phonetics[letter]
        
        # Generate or get audio for the letter
        audio_path = get_letter_audio(
            letter, 
            voice=st.session_state.current_voice, 
            model=st.session_state.current_tts_model
        )
        
        # Store current audio path
        st.session_state.current_audio = audio_path
        
        # Audio playback - more compact positioning
        if audio_path and os.path.exists(audio_path):
            # For autoplay, use custom function
            if st.session_state.autoplay:
                with audio_container:
                    # Use standard audio player for controls
                    st.audio(audio_path, format="audio/mp3")
                    # Also inject autoplay version 
                    autoplay_audio(audio_path)
            else:
                # Just show standard player without autoplay
                with audio_container:
                    st.audio(audio_path, format="audio/mp3")
        else:
            with audio_container:
                st.warning("Audio could not be loaded. Please try a different letter or voice.")
        
        # Create a single container for all content to keep it compact
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            
            # Display letter content with the compact function
            display_letter_content_compact(letter, letter_info, phonetic_info)
            
            # Show detailed information
            # Show detailed information if enabled - more compact
            if st.session_state.show_details and st.session_state.access_level != "demo":
                with st.expander("Letter Details", expanded=False):
                    st.subheader("Phonetic Information:")
                    st.write(f"- Pronunciation: {phonetic_info['phonetic']}")
                    st.write(f"- Type: {phonetic_info['type'].capitalize()}")
                    st.write(f"- Sounds: {phonetic_info['sounds']}")
                    
                    st.subheader("JSON Data:")
                    st.json(letter_info)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error(f"Information for letter '{letter}' not found!")
else:
    st.info("👆 Click on a letter above to get started!")

# Footer with premium upgrade reminder for demo users
if st.session_state.access_level == "demo":
    st.markdown("""
    <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 10px; text-align: center;">
        <h3>Enjoying the Alphabet Adventure?</h3>
        <p style="font-size: 18px; margin: 10px 0;">Upgrade to premium for access to all 26 letters, 6 different voices, and HD audio!</p>
        <a href="https://lindsayhiebert.gumroad.com/l/alphabet-adventure" target="_blank" class="gumroad-button" 
           style="display: inline-block; background-color: #FF90E8; color: #111; 
                  font-weight: bold; padding: 0.7rem 1.5rem; text-decoration: none; 
                  border-radius: 5px; font-size: 18px; margin-top: 10px;">
           Get Full Access - Just $1.99
        </a>
    </div>
    """, unsafe_allow_html=True)

# Footer
# More compact footer
st.markdown("""
<footer style="margin-top: 20px; text-align: center; font-size: 18px; color: #555;">
    © 2025 Alphabet Learning Adventure. All rights reserved.<br>
    <strong>Developed and Designed by <a href="https://www.linkedin.com/in/lindsayhiebert/" target="_blank" style="text-decoration: none; color: #4285F4; font-weight: bold;">Lindsay Hiebert</a></strong>
</footer>
""", unsafe_allow_html=True)