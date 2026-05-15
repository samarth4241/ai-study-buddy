import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="AI Study Buddy", page_icon="📚")
st.title("📚 AI Study Buddy & Note Architect")
st.markdown("---")

# 2. Sidebar for the API Key (This makes it professional)
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

# 3. User Options
option = st.selectbox("What do you want to do?", 
                     ("Summarize Notes", "Generate Flashcards", "Ask a Question"))

user_text = st.text_area("Paste your textbook text or notes here:")

if st.button("Magic Happen! ✨"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar!")
    elif not user_text:
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analyzing with Meta AI..."):
            # The prompt changes based on what the user wants
            if option == "Summarize Notes":
                prompt = f"Summarize this text into 3 easy bullet points for a student: {user_text}"
            elif option == "Generate Flashcards":
                prompt = f"Create 5 Question and Answer flashcards from this: {user_text}"
            else:
                prompt = f"Answer this question based on these notes: {user_text}"

            # Calling Meta Llama 3 via OpenRouter
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            result = response.json()['choices'][0]['message']['content']
            st.success("Here is your result:")
            st.write(result)

st.sidebar.markdown("---")
st.sidebar.write("Developed by Samarth")
