import streamlit as st
import requests

API_URL = "http://localhost:8000"

def login(username, password):
    response = requests.post(
        f"{API_URL}/login",
        auth=(username, password)
    )
    if response.status_code == 200:
        return response.json()
    return None

def ask_question(query, username, password):
    response = requests.post(
        f"{API_URL}/chat",
        params={"query": query},
        auth=(username, password)
    )
    if response.status_code == 200:
        return response.json()["answer"]
    else:
        return "❌ Authentication failed or error occurred."


st.set_page_config(page_title="RAG Role-Based Assistant")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.password = ""

if not st.session_state.logged_in:
    st.title("🔐 Login to RAG Assistant")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_data = login(username, password)
        if user_data:
            st.session_state.logged_in = True
            st.session_state.username = user_data["username"]
            st.session_state.role = user_data["role"]
            st.session_state.password = password
        else:
            st.error("Invalid username or password")

else:
    # Header with username + role
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("💬 RAG Role-Based Assistant")
    with col2:
        st.markdown(f"👤 **{st.session_state.username}**")
        st.markdown(f"🎭 **{st.session_state.role}**")

    query = st.text_input("Enter your query")

    if st.button("Ask"):
        if query.strip():
            with st.spinner("Generating..."):
                answer = ask_question(query, st.session_state.username, st.session_state.password)
            st.subheader("Answer")
            st.write(answer)
        else:
            st.warning("Please enter a query.")