import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="AI Study Buddy", page_icon="📚", layout="wide")
st.title("📚 AI Study Buddy & Note Architect")
st.markdown("---")

# 2. Permanent Sidebar Credits
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.subheader("👑 Created by Samarth")
st.sidebar.write("Available for students worldwide.")

# Helper function to convert uploaded image to base64
def encode_image(file_bytes):
    return base64.b64encode(file_bytes).decode('utf-8')

# 3. User Inputs (Options upgraded for Detailed PW-Style Notes)
option = st.selectbox("What do you want to do?", 
                     ("Generate Detailed PW-Style Notes 📝", "Generate Flashcards 🃏", "Ask a Question 🙋‍♂️"))

input_type = st.radio("Choose your input method:", ("Type/Paste Text", "Upload Pictures of Notes (Up to 10) 📷"))

user_text = ""
uploaded_images_b64 = []

if input_type == "Type/Paste Text":
    user_text = st.text_area("Paste your textbook text or notes here:", height=200)
else:
    uploaded_files = st.file_uploader(
        "Choose pictures of your notes or textbook pages (Max 10)...", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"📸 Uploaded {len(uploaded_files)} images:")
        
        # Displaying up to 10 images in grid style with custom sizing
        cols = st.columns(2)  # Side-by-side view to prevent infinite scrolling
        for index, uploaded_file in enumerate(uploaded_files[:10]):
            file_bytes = uploaded_file.read()
            image = Image.open(io.BytesIO(file_bytes))
            
            # Displays the image beautifully at a standard column width
            with cols[index % 2]:
                st.image(image, caption=f"Uploaded Page {index + 1}", width=350)
            
            # Encode for AI processing
            uploaded_images_b64.append(encode_image(file_bytes))

# 4. Processing Logic
if st.button("Magic Happen! ✨"):
    if not api_key:
        st.error("Please enter your OpenRouter API Key in the sidebar!")
    elif input_type == "Type/Paste Text" and not user_text:
        st.warning("Please paste some text first.")
    elif input_type == "Upload Pictures of Notes (Up to 10) 📷" and not uploaded_images_b64:
        st.warning("Please upload at least one image first.")
    else:
        with st.spinner("Analyzing with OpenRouter Free AI..."):
            
            # Formulating the custom PW-style prompt instructions
            if option == "Generate Detailed PW-Style Notes 📝":
                instruction = (
                    "Act as a premium, highly engaging tuition teacher (like Physics Wallah style). "
                    "Analyze the given material and generate incredibly comprehensive, highly detailed study notes. "
                    "DO NOT give a brief summary. Expand on every single concept, definition, and formula found. "
                    "Structure your output beautifully using the following format:\n"
                    "1. 🌟 CHAPTER SUMMARY & CORE CONCEPTS (Detailed breakdown)\n"
                    "2. 💡 IMPORTANT DEFINITIONS (Highlighted using bold tags)\n"
                    "3. 🔢 FORMULAS & DERIVATIONS (Written out clearly step-by-step using Markdown formatting)\n"
                    "4. ⚠️ COMMON MISTAKES / COACHING TIPS (Things students usually get wrong in exams)\n"
                    "Make sure the notes look visually striking with bullet points, numbered lists, and distinct sections."
                )
            elif option == "Generate Flashcards 🃏":
                instruction = "Create 8 highly effective Question and Answer revision flashcards based on all the provided material."
            else:
                instruction = "Act as an expert tutor. Carefully analyze all uploaded materials and explain the main topic thoroughly."

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Building the execution payload
            if input_type == "Type/Paste Text":
                json_data = {
                    "model": "openrouter/free",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{instruction}\n\nContent:\n{user_text}"
                        }
                    ]
                }
            else:
                content_list = [{"type": "text", "text": instruction}]
                for img_b64 in uploaded_images_b64:
                    content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    })
                
                json_data = {
                    "model": "openrouter/free",
                    "messages": [{"role": "user", "content": content_list}]
                }

            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=json_data
                )
                
                response_json = response.json()
                
                if 'choices' in response_json:
                    result = response_json['choices'][0]['message']['content']
                    st.success("✨ Here are your comprehensive Batch Notes:")
                    st.markdown(result)
                elif 'error' in response_json:
                    st.error(f"API Error: {response_json['error']['message']}")
                else:
                    st.error("Unexpected response structure. Please check your API configuration.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
