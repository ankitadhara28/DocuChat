import streamlit as st
import requests
import os # for accessing environment variables

# Config
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="PDF Q&A Chatbot",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# Header
st.title("📄 PDF Q&A Chatbot")
st.markdown("Upload a PDF document and ask questions about its content")

# Sidebar for PDF upload
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to ask questions about"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        st.session_state.pdf_uploaded = True
        st.session_state.pdf_name = uploaded_file.name
        
        # Display file details
        file_size = uploaded_file.size / 1024  # Convert to KB
        st.info(f"File size: {file_size:.2f} KB")
        
        # Process button (calls backend)
        if st.button("Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                    }
                    resp = requests.post(f"{BACKEND_URL}/process_pdf", files=files, timeout=120)
                    if resp.status_code == 200:
                        st.success("PDF processed successfully on backend!")
                    else:
                        st.error(f"Backend returned status {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"Error when calling backend: {e}")
    else:
        st.session_state.pdf_uploaded = False
        st.info("Please upload a PDF to get started")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Backend configuration helper (useful in Colab)
    st.divider()
    st.subheader("Backend & Settings")
    st.text_input("Backend URL", value=BACKEND_URL, key="backend_url_input", help="Set this to your Aryan's backend (e.g. http://localhost:8000 or http://abcd.ngrok.io)")
    if st.button("Apply backend URL"):
        # update environment variable and reload
        os.environ["BACKEND_URL"] = st.session_state.backend_url_input
        st.success("Backend URL updated. Reloading...")
        st.experimental_rerun()

    st.divider()
    st.subheader("Settings")
    temperature = st.slider(
        "Response Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make responses more creative"
    )

# Main chat interface
if not st.session_state.pdf_uploaded:
    st.info("👈 Please upload a PDF file from the sidebar to begin")
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"]) 
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your PDF..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response (call backend)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "question": prompt,
                        "pdf_name": st.session_state.pdf_name,
                        "temperature": temperature
                    }
                    resp = requests.post(f"{os.environ.get('BACKEND_URL', BACKEND_URL)}/ask_question", json=payload, timeout=60)
                    if resp.status_code == 200:
                        answer = resp.json().get("answer", "(No answer returned by backend)")
                    else:
                        answer = f"Error from backend: {resp.status_code} - {resp.text}"
                except Exception as e:
                    answer = f"Error when calling backend: {e}"
                st.markdown(answer)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": answer})

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <small>PDF Q&A Chatbot | Built with Streamlit</small>
    </div>
""", unsafe_allow_html=True)
