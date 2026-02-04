import config
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_huggingface import ChatHuggingFace, HuggingFaceEmbeddings, HuggingFaceEndpoint, HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv

load_dotenv()

class YouTubeAssistant:
    def __init__(self):
        print('--- Initializing---')
        self.embedding_model = HuggingFaceEmbeddings(
        model=config.EMBEDDING_MODEL
        )
        llm = HuggingFaceEndpoint(repo_id = config.CHAT_MODEL_ID, task = 'text-generation')
        self.model = ChatHuggingFace(llm = llm)
        self.Parser = StrOutputParser()

    def get_transcript(self,video_id):
        print('---Getting Transcript of Video---')
        generator = YouTubeTranscriptApi()
        transcript_tuple = generator.fetch(video_id)
        transcript = ' '.join(t.text for t in transcript_tuple)
        return transcript

    def create_vector_store(self, text):
        print('---Creating Vector Store---')
        splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        chunks = splitter.create_documents([text])
        vector_store = FAISS.from_documents(chunks, self.embedding_model)
        return vector_store
    
    def format_context(self, retrieved_docs):
        print('---Formatting the Retrieved Documents---')
        return ' '.join(doc.page_content for doc in retrieved_docs)
    
    def get_response(self, query, vector_store):
        print('---Generating Response---')
        retriever = vector_store.as_retriever(search_type = 'similarity', search_kwargs = {'k':4})
        template = PromptTemplate(template =  ''' Answer the query only from the following context if the context is insufficient or answer is not available in context just say you don't know
                context:
                {context}\n

                question:
                {question}''', 
                            input_variables=['context', 'question'])
        parallel_chain = RunnableParallel({'context': retriever | RunnableLambda(self.format_context), 'question': RunnablePassthrough()})
        chain = parallel_chain | template | self.model | self.Parser
        return chain.invoke(query)
    


assistant = YouTubeAssistant()
transcript = assistant.get_transcript('7xTGNNLPyMI')
vector_store = assistant.create_vector_store(transcript)
result = assistant.get_response('How Tokenization takes place in conversations?', vector_store)
print(result)