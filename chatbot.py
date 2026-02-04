import config
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class YoutubeAssistant:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model = config.EMBEDDING_MODEL)
        self.model = ChatHuggingFace(llm = HuggingFaceEndpoint(
            repo_id = config.CHAT_MODEL_ID,
            task = 'text-generation',
            pipeline_kwargs={
                'temperature': 0.7, #randomness of model
                'max_new_tokens': 500
            }
        ))
        self.parser = StrOutputParser()
    def get_transcript(self, video_id):
        youtube_transcript = YouTubeTranscriptApi()
        transcript_tuple = youtube_transcript.fetch(video_id)
        transcript = ' '.join(trans.text for trans in transcript_tuple)
        return transcript
    
    def create_vector_store(self, text):
        splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        result = splitter.split_text(text)
        vector_store = FAISS.from_documents(result, self.embeddings)
        return vector_store
    
    
    def get_response(self, query, vector_store):
        retriever = vector_store.as_retriever(search_type = 'similarity', search_kwargs = {'k':4})
        template = PromptTemplate(
            template = config.TEMPLATE,
            input_variables =['context', 'question'])
        parallel_chain = RunnableParallel({'context': retriever, 'question': RunnablePassthrough()})
        chain = parallel_chain | template | self.model | self.parser
        return chain.invoke(query)
        
        