from io import BytesIO
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import backend
from backend import *
import json
from PIL import Image, ImageDraw, ImageFont
from PIL import Image, UnidentifiedImageError
from streamlit_extras.let_it_rain import rain
import uuid
import re
# =========================
# LOGIN STATE
# =========================

def login_page():
    st.title("Welcome! 👋 to Pine 🌳")

    # Instruction Box
    st.info("""
    🔐 **Username Guidelines**
    • Do NOT enter personal sensitive information (email, phone number, etc.)
    • You may use your college ID or reference username
    • Allowed characters: Letters (A–Z), Numbers (0–9), Underscore (_)
    • No spaces or special characters
    • Minimum 3 characters
    """)

    user_name = st.text_input(
        "Username",
        placeholder="Enter your username (e.g., john_2024)"
    )

    if st.button("Continue"):
        cleaned_name = user_name.strip()

        if cleaned_name == "":
            st.error("Please enter a username")

        # Allow letters, numbers, underscore only
        elif not re.match("^[A-Za-z0-9_]+$", cleaned_name):
            st.error("Username can only contain letters, numbers, and underscore (_)")

        elif len(cleaned_name) < 3:
            st.error("Username must be at least 3 characters long")

        else:
            st.session_state.user_name = cleaned_name
            st.session_state.logged_in = True
            st.rerun()


# =========================
# SESSION STATE
# =========================

def initialize_session_state():
    """
    Initialize all Streamlit session variables.
    These persist across user interactions.
    """

    defaults = {
        "logged_in": False,
        "user_name": None,
        "conversation": [],
        "chat_log": [], # Stores full chat history
        "active_image_id": None, # Current image session ID
        "image_counter": 0, # Counts uploaded images
        "last_uploaded_file_name": None, # Counts uploaded images
        "mode": "Chat", # Chat | Object Detection | Point to Object
        "last_logged_action": None,
    }

    # Create session keys if they don't already exist
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================
# SIDEBAR
# =========================
def side_bar():
    """
    Renders the left sidebar UI.
    Handles image upload and mode selection.
    """

    with st.sidebar:
        logo_image = "logo.png"

        st.image(logo_image, width="stretch")

        st.markdown("### A GenAI Vision Language Model")

        st.markdown("Upload an image and ask!")

        # STREAMLIT: Image uploader widget
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png", "gif"],
        )

        # Mode selector (only shown after image upload)
        if uploaded_file is not None:
            st.radio(
                "Select Mode",
                options=["Chat", "Object Detection", "Point to Object"],
                key="mode",
            )

    return uploaded_file


# =========================
# CHAT + OBJECT UI
# =========================
def chat_UI(model, tokenizer, device, uploaded_file):
    """
    Main UI controller.
    Handles:
    - Image loading
    - Mode switching
    - Chat
    - Object detection
    - Pointing
    - DB logging for feature usage
    """

    st.header(
        f"Welcome to ***Pine*** 🌳 — {st.session_state.user_name}!"
    )

    st.divider()

    # Default is no image is loaded.
    if uploaded_file is None:
        st.info("Upload an image to continue")
        return

    # -------------------------
    # Load image (with safety)
    # -------------------------
    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)

        gif_image = None

        if uploaded_file.type == "image/gif":
            uploaded_file.seek(0)
            gif_image = Image.open(uploaded_file)
        else:
            image = image.convert("RGB")

    except (UnidentifiedImageError, OSError):
        st.error(
            "🌲 The uploaded file appears to be corrupted or not a valid image. "
            "Please upload a clear JPG, PNG, or GIF file."
        )
        return

    except Exception:
        print("Some Error Occured with the Image : Try Again! with other Image")
        return

    pine_rain()

    # -------------------------
    # Detect new image
    # -------------------------
    new_image_uploaded = (
        st.session_state.active_image_id is None
        or uploaded_file.name != st.session_state.last_uploaded_file_name
    )

    if new_image_uploaded:
        st.session_state.image_counter += 1
        st.session_state.active_image_id = st.session_state.image_counter
        st.session_state.conversation = []
        st.session_state.last_uploaded_file_name = uploaded_file.name
        pine_rain()

    # -------------------------
    # Display image
    # -------------------------
    st.subheader("Uploaded Image")

    if uploaded_file.type == "image/gif":
        uploaded_file.seek(0)
        st.image(uploaded_file, caption="Uploaded GIF", width="stretch")
    else:
        st.image(image, caption="Uploaded Image", width="stretch")

    pine_rain()

    # =========================
    # OBJECT DETECTION MODE
    # =========================
    if st.session_state.mode == "Object Detection":
        st.subheader("🎯 Object Detection")

        detect_query = st.chat_input("What object should I detect?")

        if detect_query:
            overlay = object_detection(
                model=model,
                image=image,
                query=detect_query,
            )

            st.image(
                overlay,
                caption=f"Detected: {detect_query}",
                width="stretch",
            )

            st.markdown(
                f"🍃 **Image {st.session_state.active_image_id} — Object Detection Result**"
            )

            pine_rain()

            img_bytes = image_to_bytes(overlay)

            st.download_button(
                label="📥 Download Detection Image",
                data=img_bytes,
                file_name=f"pine_detection_image_{st.session_state.active_image_id}.png",
                mime="image/png",
            )

            log_key = f"object_{st.session_state.active_image_id}_{detect_query}"

            # -------------------------
            # SAVE USAGE TO DB
            # -------------------------
            if st.session_state.last_logged_action != log_key:
                insert_user_activity(
                    user_name=st.session_state.user_name,
                    mode="Object Detection",
                    question=detect_query,
                    response="Object Detection Used"
                )
                st.session_state.last_logged_action = log_key

        return

    # =========================
    # POINT TO OBJECT MODE
    # =========================
    if st.session_state.mode == "Point to Object":
        st.subheader("📍 Point to Object")

        point_query = st.chat_input("What object should I point to?")

        if point_query:
            overlay = point_to_object(
                model=model,
                image=image,
                query=point_query,
            )

            st.image(
                overlay,
                caption=f"Points: {point_query}",
                width="stretch",
            )

            pine_rain()

            st.markdown(
                f"🍃 **Image {st.session_state.active_image_id} — Point to Object Result**"
            )

            img_bytes = image_to_bytes(overlay)

            st.download_button(
                label="📥 Download Pointed Image",
                data=img_bytes,
                file_name=f"pine_point_image_{st.session_state.active_image_id}.png",
                mime="image/png",
            )

            log_key = f"point_{st.session_state.active_image_id}_{point_query}"
            # -------------------------
            # SAVE USAGE TO DB
            # -------------------------
            if st.session_state.last_logged_action != log_key:
                insert_user_activity(
                    user_name=st.session_state.user_name,
                    mode="Point to Object",
                    question=point_query,
                    response="Point to Object Used"
                )
                st.session_state.last_logged_action = log_key

        return

    # =========================
    # CHAT MODE
    # =========================
    user_input = st.chat_input("Ask something about the image")

    if user_input:
        st.session_state.chat_log.append({
            "image_id": st.session_state.active_image_id,
            "speaker": "user",
            "message": user_input,
        })

        if uploaded_file.type == "image/gif":
            response = process_gif(model, tokenizer, device, gif_image, user_input)
        else:
            response = generate_answer(model, tokenizer, device, image, user_input)

        pine_rain()

        st.session_state.chat_log.append({
            "image_id": st.session_state.active_image_id,
            "speaker": "ai",
            "message": response,
        })

        log_key = f"chat_{st.session_state.active_image_id}_{user_input}"
        # -------------------------
        # SAVE CHAT TO DB
        # -------------------------
        if st.session_state.last_logged_action != log_key:
            insert_user_activity(
                user_name=st.session_state.user_name,
                mode="Chat",
                question=user_input,
                response=response
            )
            st.session_state.last_logged_action = log_key

    pine_rain()
    render_chat_history()

    # =========================
    # DOWNLOAD CHAT (CSV)
    # =========================
    if st.session_state.mode == "Chat" and st.session_state.chat_log:
        csv_data = build_chat_csv(st.session_state.chat_log)

        st.download_button(
            label="📥 Download Chat as CSV",
            data=csv_data,
            file_name="pine_chat_history.csv",
            mime="text/csv",
        )


# =========================
# CHAT HISTORY
# =========================
def render_chat_history():
    """
    Displays all chat messages across all images.
    """

    st.subheader("Chat Logs (All Images)")

    for msg in st.session_state.chat_log:
        if msg["speaker"] == "user":
            st.markdown(
                f"🌲 **Image {msg['image_id']} — Question:** {msg['message']}"
            )
        else:
            st.markdown(
                f"🍃 **Image {msg['image_id']} — Response:** {msg['message']}"
            )

# =========================
# LOAD CUSTOM CSS
# =========================

def load_css(path="styles.css"):
    with open(path) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# =========================
# UI ANIMATION
# =========================

def pine_rain():
    """Pine UI leaf rain effect (runs once per session)."""

    rain(
        emoji="🍃",
        font_size=30,
        falling_speed=4,
        animation_length=1,
    )

# =========================
# FOOTER
# =========================
def footer():
    st.markdown(
        "<div class='footer'> Developed with ❤️ </div>",
        unsafe_allow_html=True
    )

# =========================
# MAIN
# =========================
def main():
    st.set_page_config(
        page_title="Pine 🌳",
    )

    initialize_session_state()
    load_css()

    model, tokenizer, device = model_loading()

    if not st.session_state.logged_in:
        login_page()
        return

    uploaded_file = side_bar()
    chat_UI(model, tokenizer, device, uploaded_file)
    footer()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")