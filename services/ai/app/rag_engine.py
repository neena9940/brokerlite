import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Get the Ollama URL from environment (defaults to localhost for local testing)
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# 2. Initialize LLM and Embeddings using the dynamic URL
llm = ChatOllama(model="llama3.1", temperature=0, base_url=OLLAMA_BASE_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)

# 2. Create a dummy financial document
FINANCIAL_REPORT = """
BrokerLite Q3 Financial Report.
Revenue increased by 25% year-over-year to $150 million.
The company launched a new AI-driven portfolio feature.
Net income rose to $40 million, beating analyst expectations.
The user base grew by 100,000 new traders this quarter.
"""


# 3. Ingest and Vectorize
def initialize_vector_db():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(FINANCIAL_REPORT)

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name="brokerlite_reports"
    )
    return vectorstore


# Initialize the DB
vectorstore = initialize_vector_db()
retriever = vectorstore.as_retriever()

# 4. Create the RAG Chain
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)


def ask_question(question: str) -> str:
    return rag_chain.invoke(question)