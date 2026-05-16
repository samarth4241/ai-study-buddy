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

# HTML/JS Code for Audio Reader
def text_to_speech_js(text_content):
    clean_text = text_content.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    js_script = f"""
    <script>
    function playAudio() {{
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    }}
    function stopAudio() {{
        window.speechSynthesis.cancel();
    }}
    </script>
    <div style="margin-top: 15px; margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
        <button onclick="playAudio()" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px; font-weight: bold;">🔊 Read These Notes Aloud</button>
        <button onclick="stopAudio()" style="background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold;">⏹️ Stop Reading</button>
    </div>
    """
    return js_script

# 3. Main Interface Layout
input_type = st.radio("Choose your input method:", ("Type/Paste Text", "Upload Pictures of Notes (Up to 10) 📷"))

user_text = ""
uploaded_images_b64 = []

if input_type == "Type/Paste Text":
    user_text = st.text_area("Paste your textbook text or notes here:", height=150)
else:
    uploaded_files = st.file_uploader(
        "Choose pictures of your notes or textbook pages (Max 10)...", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"📸 Uploaded {len(uploaded_files)} images:")
        cols = st.columns(2)
        for index, uploaded_file in enumerate(uploaded_files[:10]):
            file_bytes = uploaded_file.read()
            image = Image.open(io.BytesIO(file_bytes))
            with cols[index % 2]:
                st.image(image, caption=f"Uploaded Page {index + 1}", width=350)
            uploaded_images_b64.append(encode_image(file_bytes))

st.markdown("---")
st.subheader("💡 Choose your Action")

# The exact 4 tabs in the exact order you requested
tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🃏 Revision Flashcards", "🙋‍♂️ Ask Custom Question", "📝 Detailed Notes"])

# 4. Processing Logic
if st.button("Magic Happen! ✨"):
    if not api_key:
        st.error("Please enter your OpenRouter API Key in the sidebar!")
    elif input_type == "Type/Paste Text" and not user_text:
        st.warning("Please paste some text first.")
    elif input_type == "Upload Pictures of Notes (Up to 10) 📷" and not uploaded_images_b64:
        st.warning("Please upload at least one image first.")
    else:
        with st.spinner("Analyzing your materials with Meta Llama AI..."):
            
            master_instruction = (
                "Act as an expert elite tutor. Analyze the given materials perfectly and create a comprehensive master study suite. "
                "Your response MUST split the content explicitly using these exact markers:\n\n"
                "[SUMMARY_START]\n(Provide a brief, 3-bullet point quick summary here)\n[SUMMARY_END]\n\n"
                "[FLASHCARDS_START]\n(Create 6 high-yield Question and Answer revision flashcards here)\n[FLASHCARDS_END]\n\n"
                "[NOTES_START]\n(Provide comprehensive, deep classroom notes in premium batch style like Physics Wallah notes. Expand on every concept, definition, and formula step-by-step)\n[NOTES_END]"
            )

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            if input_type == "Type/Paste Text":
                json_data = {
                    "model": "openrouter/free",
                    "messages": [{"role": "user", "content": f"{master_instruction}\n\nContent:\n{user_text}"}]
                }
            else:
                content_list = [{"type": "text", "text": master_instruction}]
                for img_b64 in uploaded_images_b64:
                    content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
                json_data = {
                    "model": "openrouter/free",
                    "messages": [{"role": "user", "content": content_list}]
                }

            try:
                response = requests.post(url="https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)
                response_json = response.json()
                
                if 'choices' in response_json:
                    st.session_state['ai_output'] = response_json['choices'][0]['message']['content']
                    st.success("Analysis Complete! Click through the tabs below to view your materials.")
                elif 'error' in response_json:
                    st.error(f"API Error: {response_json['error']['message']}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# 5. Extract and display data cleanly into your 4 tabs
if 'ai_output' in st.session_state:
    raw_data = st.session_state['ai_output']
    
    # Safe text parsing extraction logic
    def extract_section(text, start_marker, end_marker):
        try:
            start_idx = text.find(start_marker) + len(start_marker)
            end_idx = text.find(end_marker)
            if start_idx != -1 and end_idx != -1:
                return text[start_idx:end_idx].strip()
        except:
            pass
        return "Content processing error. Please try clicking 'Magic Happen' again."

    summary_text = extract_section(raw_data, "[SUMMARY_START]", "[SUMMARY_END]")
    flash_text = extract_section(raw_data, "[FLASHCARDS_START]", "[FLASHCARDS_END]")
    notes_text = extract_section(raw_data, "[NOTES_START]", "[NOTES_END]")

    with tab1:
        st.subheader("📋 Quick Executive Summary")
        st.markdown(summary_text)
        
    with tab2:
        st.subheader("🃏 Smart Revision Flashcards")
        st.markdown(flash_text)
        
    with tab4:
        st.subheader("📝 Detailed Smart Class Notes")
        # Embedding the audio reader directly at the top of the notes tab as requested!
        st.components.v1.html(text_to_speech_js(notes_text), height=80)
        st.markdown(notes_text)

# Independent Tab 3 handling for custom typing inputs
with tab3:
    st.subheader("🙋‍♂️ Ask an Independent Question")
    custom_q = st.text_input("Got a specific doubt? Ask here:")
    if st.button("Ask AI Tutor 🧠"):
        if not api_key:
            st.error("Please insert your key in the sidebar first.")
        elif not custom_q:
            st.warning("Please type a question.")
        else:
            with st.spinner("Tutor is answering..."):
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    q_json = {
                        "model": "openrouter/free",
                        "messages": [{"role": "user", "content": f"Answer this student doubt thoroughly as a supportive teacher: {custom_q}"}]
                    }
                    q_res = requests.post(url="https://openrouter.ai/api/v1/chat/completions", headers=headers, json=q_json).json()
                    st.info(q_res['choices'][0]['message']['content'])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
