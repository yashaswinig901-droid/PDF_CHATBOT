import streamlit as st 
import os
import tempfile
from main import create_or_load_vectorstore, get_qa_chain

st.set_page_config(page_title="📄 PDF Chatbot", layout="centered")

st.title("📄 Chat with your PDF")
st.markdown("Upload a PDF and start asking questions about it.")

# File uploader
uploaded_file = st.file_uploader("📂 Upload your PDF", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file to a temp directory
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name

    st.success(f"✅ PDF uploaded: {uploaded_file.name}")

    # Create vectorstore and QA chain
    with st.spinner("🔍 Processing PDF and creating vector store..."):
        vectorstore = create_or_load_vectorstore(pdf_path, index_path=f"faiss_index_{uploaded_file.name}")
        qa_chain = get_qa_chain(vectorstore)

    st.success("✅ PDF processed successfully! You can now ask questions.")

    # User query input
    query = st.text_input("💬 Ask something about the PDF:")

    if query:
        with st.spinner("💡 Generating answer..."):
            response = qa_chain.invoke({"query": query})
            st.write("🧠 Answer:")
            st.write(response.get("result", "⚠️ No answer returned."))

            # Show sources if available
            if "source_documents" in response:
                st.write("📑 Sources:")
                for doc in response["source_documents"]:
                    st.write(f"- {doc.metadata.get('source', 'Unknown')}")
else:
    st.info("👆 Please upload a PDF to start chatting.")


