import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="AI Study Buddy", page_icon="📚")
st.title("📚 AI Study Buddy & Note Architect")
st.markdown("---")

# 2. Permanent Sidebar Credits
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.subheader("👑 Created by Samarth")
st.sidebar.write("Available for students worldwide.")

# Helper function to convert uploaded image to base64
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode('utf-8')

# 3. User Inputs (Text or Image)
option = st.selectbox("What do you want to do?", 
                     ("Summarize Notes", "Generate Flashcards", "Ask a Question"))

input_type = st.radio("Choose your input method:", ("Type/Paste Text", "Upload Picture of Notes 📷"))

user_text = ""
image_base64 = None

if input_type == "Type/Paste Text":
    user_text = st.text_area("Paste your textbook text or notes here:")
else:
    uploaded_file = st.file_uploader("Choose a picture of your notes or textbook page...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image Preview", use_container_width=True)
        # Rewind file pointer to read it for base64 encoding
        uploaded_file.seek(0)
        image_base64 = encode_image(uploaded_file)

# 4. Processing Logic
if st.button("Magic Happen! ✨"):
    if not api_key:
        st.error("Please enter your OpenRouter API Key in the sidebar!")
    elif input_type == "Type/Paste Text" and not user_text:
        st.warning("Please paste some text first.")
    elif input_type == "Upload Picture of Notes 📷" and image_base64 is None:
        st.warning("Please upload an image first.")
    else:
        with st.spinner("Analyzing with Meta Llama AI..."):
            
            # Setup task instruction based on selection
            if option == "Summarize Notes":
                instruction = "Summarize the following core content into 3 clear, highly structured bullet points for a student."
            elif option == "Generate Flashcards":
                instruction = "Create 5 highly effective Question and Answer flashcards for revision based on this content."
            else:
                instruction = "Act as an expert tutor. Carefully analyze the content and answer any implicit student questions thoroughly."

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # If it's text input, use standard text completion
            if input_type == "Type/Paste Text":
                json_data = {
                    "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{instruction}\n\nContent:\n{user_text}"
                        }
                    ]
                }
            # If it's an image input, send it to the vision model
            else:
                json_data = {
                    "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": instruction},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
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
                    st.success("Here is your result:")
                    st.write(result)
                elif 'error' in response_json:
                    st.error(f"API Error: {response_json['error']['message']}")
                else:
                    st.error("Unexpected response structure from AI platform. Please check your API key.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
