import streamlit as st
from dotenv import load_dotenv
import langchain
from langchain.llms import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import time

"""
Main YT example showing the entire process from embedding
to storing to the FAISS index, finally to querying
"""

load_dotenv()
st.title("New Research Tool:")
st.sidebar.title("News Article URLs")

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

# initialize the main LLM - in this case we are using OpenAI (but HuggingFace seems better??)
embeddings = OpenAIEmbeddings()
llm = OpenAI(temperature=0.9, max_tokens=500)
embed_name = "faiss_url_embeddings"

# placeholder for loading data bar
main_placefolder = st.empty()

process_url_clicked = st.sidebar.button("Process URLs")
if process_url_clicked:
    # load the urls with unstructured 
    loader = UnstructuredURLLoader(urls=urls)
    main_placefolder.text("Data Loading...Started...") 
    data = loader.load()

    # split the data using recursive splitter
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],
	chunk_size=1000
    )
    main_placefolder.text("Text Splitter...Started...") 
    docs = text_splitter.split_documents(data)

    # create new embeddings and set FAISS index
    vectorstore_openai = FAISS.from_documents(docs, embeddings) 

    main_placefolder.text("Embedding Vector Building...")
    time.sleep(2)
    
    # store the vector index as local pkl
    vectorstore_openai.save_local(embed_name) 
   
# prompty the user for a question query
query = main_placefolder.text_input("Question: ") 
if query:
    # load the local embeddings stored in pkl
    persisted_index = FAISS.load_local(embed_name, embeddings)
    print("FAISS Persisted Index:")
    print(persisted_index)
    print("\n")
   
    # create retrieval QA with sources chain using LLM and QA 
    chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=persisted_index.as_retriever())
    print("RAG Chain:")
    print(chain)
    print("\n")
   
    # issue query to the chain
    langchain.debug=True
    result = chain({"question": query}, return_only_outputs=True)
    print("Result:")
    print(result)
    print("\n")

    # the result is an object {answer: x, sources: y}
    st.header("Answer:")
    st.subheader(result["answer"])

