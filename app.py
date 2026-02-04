import streamlit as st
from chatbot import YoutubeAssistant
import config

# Initialize our logic class
assistant = YoutubeAssistant()


st.title("📹 YouTube Video Assistant")

# Sidebar for Video Input
video_url = st.sidebar.text_input("Enter YouTube Video URL")
video_id = video_url.split("v=")[-1] if "v=" in video_url else video_url

if video_id:
    # We use st.session_state so we don't re-index the video every time you ask a question
    if 'vs' not in st.session_state or st.session_state.get('current_id') != video_id:
        with st.spinner("Analyzing video content..."):
            text = assistant.get_transcript(video_id)
            if text:
                st.session_state.vs = assistant.create_vector_store(text)
                st.session_state.current_id = video_id
                st.sidebar.success("Video indexed!")
            else:
                st.sidebar.error("Could not find a transcript for this video.")

# Chat History UI
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handling User Input
if user_query := st.chat_input("Ask a question about the video"):
    if 'vs' in st.session_state:
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate and display response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Using your get_response method
                response = assistant.get_response(user_query, st.session_state.vs)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    else:
        st.warning("Please enter a valid YouTube link first.")