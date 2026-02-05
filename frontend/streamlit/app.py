import streamlit as st
import requests

# ----------------------------
# Config
# ----------------------------
BACKEND_URL = "http://127.0.0.1:8000"
API_KEY = "dev-key-123"   # must match backend .env

HEADERS = {
    "X-API-Key": API_KEY,
}

st.set_page_config(page_title="Agentic Research Assistant", layout="wide")

# ----------------------------
# Session state init
# ----------------------------
if "chats" not in st.session_state:
    st.session_state.chats = []

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Helper API functions
# ----------------------------
def api_get(path):
    r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def api_post(path, json=None, files=None):
    r = requests.post(
        f"{BACKEND_URL}{path}",
        headers=HEADERS if files is None else HEADERS,
        json=json,
        files=files,
    )
    r.raise_for_status()
    return r.json()

# ----------------------------
# Sidebar: Chats + Upload
# ----------------------------
with st.sidebar:
    st.title("📂 Chats")

    # Refresh chats
    if st.button("🔄 Refresh chats"):
        st.session_state.chats = api_get("/chats")

    # Load chats initially
    if not st.session_state.chats:
        try:
            st.session_state.chats = api_get("/chats")
        except Exception:
            st.session_state.chats = []

    # Chat list
    for chat in st.session_state.chats:
        label = chat["title"] or "Untitled chat"
        if st.button(label, key=chat["chat_id"]):
            st.session_state.active_chat_id = chat["chat_id"]
            st.session_state.messages = api_get(f"/chats/{chat['chat_id']}/messages")

    st.divider()
    st.subheader("📄 Upload PDF")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Create chat from PDF"):
            with st.spinner("Uploading and indexing..."):
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                upload_resp = requests.post(
                    f"{BACKEND_URL}/upload",
                    headers=HEADERS,
                    files=files,
                )
                upload_resp.raise_for_status()
                report_id = upload_resp.json()["report_id"]

                chat_resp = api_post(
                    "/chats",
                    json={"report_id": report_id, "title": uploaded_file.name},
                )

                st.session_state.chats.insert(0, chat_resp)
                st.session_state.active_chat_id = chat_resp["chat_id"]
                st.session_state.messages = []

                st.success("Chat created!")

# ----------------------------
# Main chat area
# ----------------------------
st.title("💬 Agentic Research Assistant")

if not st.session_state.active_chat_id:
    st.info("Upload a PDF or select a chat from the sidebar to start.")
    st.stop()

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ask a question about this report...")

if prompt:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        resp = api_post(
            f"/chats/{st.session_state.active_chat_id}/messages",
            json={"message": prompt},
        )

        answer = resp["answer"]

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
