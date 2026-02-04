import streamlit as st
from chatbot import YouTubeAssistant

if 'assistant' not in st.session_state:
    st.session_state.assistant = YouTubeAssistant()

st.header('Your Own YouTube Assistant :smile:')

url = st.sidebar.text_input('Enter the video URL ')

if st.sidebar.button('Enter'):
    video_id = url.split('v=')[-1] if 'v=' in url else url
    if video_id:
        st.sidebar.success(f'Got the video id {video_id}')
        if 'video_id' not in st.session_state or st.session_state.video_id!=video_id:
            st.session_state.video_id = video_id
            st.session_state['transcript']=st.session_state.assistant.get_transcript(video_id)
            st.session_state['vs']=st.session_state.assistant.create_vector_store(st.session_state['transcript'])
            
    else:    
        st.sidebar.write('ID not found')
st.sidebar.markdown('> Caution! This Assistant is not for Summarizing the whole video, it is just a Q/A bot')



if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat['role']):
        st.markdown(chat['content'])

if user_input := st.chat_input('Enter your query regarding video'):
    if 'vs' in st.session_state:
        st.session_state.chat_history.append({'role':'user', 'content': user_input})
        
        with st.chat_message('user'):
            st.markdown(user_input)

        with st.chat_message('assistant'):
            with st.spinner('Thinking for you'):
                response = st.session_state.assistant.get_response(user_input, st.session_state.vs)
                st.markdown(response)
                st.session_state.chat_history.append({'role':'assistant', 'content':response})
    else:
        st.warning("Please Enter a valid ID or link 1st")
