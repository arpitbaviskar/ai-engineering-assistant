import streamlit as st
import requests, uuid

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Engineering Assistant",
                    page_icon="🤖", layout="wide")
st.title("🤖 AI Engineering Assistant")

# persistent session ID for memory endpoint
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Ask (no memory)",
    "🧠 Chat (with memory)",
    "⚙️ Code Generator",
    "📷 Vision Diagnostics"
])

# ── Tab 1: basic RAG Q&A ──────────────────────────
with tab1:
    q = st.text_input("Engineering question",
                       placeholder="Why does my servo jitter?")
    if st.button("Ask", key="ask1") and q:
        with st.spinner("Thinking..."):
            r = requests.post(f"{API}/ask",
                              json={"question": q})
        if r.status_code == 200:
            data = r.json()
            st.markdown("### Answer")
            st.write(data["answer"])
            if data["sources"]:
                st.caption("Sources: " + ", ".join(data["sources"]))
        else:
            st.error("API error")

# ── Tab 2: memory chat ────────────────────────────
with tab2:
    st.caption(f"Session: {st.session_state.session_id[:8]}...")
    for turn in st.session_state.history:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.write(turn["assistant"])

    q2 = st.chat_input("Ask anything — I remember context")
    if q2:
        with st.spinner("Thinking..."):
            r = requests.post(f"{API}/ask/memory", json={
                "session_id": st.session_state.session_id,
                "question": q2
            })
        if r.status_code == 200:
            ans = r.json()["answer"]
            st.session_state.history.append(
                {"user": q2, "assistant": ans})
            st.rerun()

    if st.button("Clear conversation"):
        st.session_state.history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# ── Tab 3: code generator ─────────────────────────
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        robot = st.text_input("Robot", "4 DOF robotic arm")
        controller = st.selectbox("Controller",
            ["Arduino Uno", "Arduino Mega", "ESP32",
             "Raspberry Pi", "ROS2"])
    with col2:
        language = st.selectbox("Language",
            ["Arduino C++", "MicroPython", "Python ROS2"])
        task = st.text_input("Task", "rotate base servo to 90 degrees")
    if st.button("Generate Code") and task:
        with st.spinner("Generating..."):
            r = requests.post(f"{API}/generate", json={
                "robot": robot, "controller": controller,
                "task": task, "language": language})
        if r.status_code == 200:
            st.code(r.json()["code"], language="cpp")

# ── Tab 4: vision diagnostics ─────────────────────
with tab4:
    uploaded = st.file_uploader("Upload machine image",
                                  type=["jpg", "jpeg", "png"])
    if uploaded and st.button("Analyze"):
        with st.spinner("Running YOLO + LLM..."):
            r = requests.post(f"{API}/vision",
                files={"file": (uploaded.name,
                                  uploaded.getvalue(),
                                  uploaded.type)})
        if r.status_code == 200:
            data = r.json()
            st.markdown("### Detected components")
            for d in data["detections"]:
                st.write(f"• {d['label']} ({d['confidence']*100:.0f}%)")
            st.markdown("### Diagnosis")
            st.write(data["diagnosis"])