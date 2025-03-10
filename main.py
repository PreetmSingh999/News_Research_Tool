import os
import streamlit as st
import pickle
import time
from langchain_openai import OpenAI # Corrected Import
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Manually Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"  # Replace with your actual API key

st.title("RockyBot: News Research Tool 📈")
st.sidebar.title("News Article URLs")

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i + 1}")
    if url:  # Avoid empty URLs
        urls.append(url)

process_url_clicked = st.sidebar.button("Process URLs")
file_path = "faiss_store_openai.pkl"

main_placeholder = st.empty()
llm = OpenAI(temperature=0.9, max_tokens=500)

if process_url_clicked:
    if urls:  # Ensure URLs are provided
        # Load data
        loader = UnstructuredURLLoader(urls=urls)
        main_placeholder.text("Data Loading...Started...✅✅✅")
        data = loader.load()

        # Split data
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=1000
        )
        main_placeholder.text("Text Splitter...Started...✅✅✅")
        docs = text_splitter.split_documents(data)

        # Create embeddings and save to FAISS index
        embeddings = OpenAIEmbeddings()
        vectorstore_openai = FAISS.from_documents(docs, embeddings)
        main_placeholder.text("Embedding Vector Started Building...✅✅✅")
        time.sleep(2)

        # Save FAISS index to a pickle file
        with open(file_path, "wb") as f:
            pickle.dump(vectorstore_openai, f)
    else:
        st.error("Please enter at least one valid URL.")

query = main_placeholder.text_input("Question: ")
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
            result = chain({"question": query}, return_only_outputs=True)

            st.header("Answer")
            st.write(result.get("answer", "No answer found."))

            # Display sources, if available
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                for source in sources.split("\n"):
                    st.write(source)
    else:
        st.error("No processed data found. Please process URLs first.")
