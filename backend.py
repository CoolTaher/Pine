from io import BytesIO
import os
from dataclasses import dataclass
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st
import pyvips
import json
from PIL import Image, ImageDraw, ImageFont
import csv
from io import StringIO
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import datetime
import bcrypt

# -------------------------
# SUPABASE REST CONFIG
# -------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}


# Message structure for chat history
@dataclass
class Message:
    actor: str # "user" or "ai"
    payload: str # message content

# Stores full conversation history
conversation_history = []

def initialize_session_state():
    """
    Initialize Streamlit session state with a default AI greeting.
    Runs only once per session.
    """
    if "messages" not in st.session_state:
        st.session_state["messages"] = [Message(actor="ai", payload="Hi! How can I help you?")]


# Initialize session on app start
initialize_session_state()

def chat_record(speaker, message):
    """
    Append a new message to the session chat history.
    """
    st.session_state["messages"].append(Message(actor=speaker, payload=message))


@st.cache_resource
def model_loading():
    """
    Load model and tokenizer once and cache them.
    Uses GPU if available.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_id = "vikhyatk/moondream2"
    revision="2025-06-21"
    model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, revision=revision).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

    return model, tokenizer, device

def generate_answer(model, tokenizer, device, image, question):
    """
    Generate an answer for a single image-question pair.
    """

    enc_image = model.encode_image(image) #Encoding image for the model compatibility

    if isinstance(enc_image, torch.Tensor): # Moving image embedding to correct device
        enc_image = enc_image.to(device)

    #MODEL CHAT OPTION
    answer = model.answer_question(enc_image, question, tokenizer)
    return answer


def process_gif(model, tokenizer, device, gif_image, question):
    """
    Process GIF by sampling frames and answering from them.
    """
    frame_count = 0
    answers = []

    while True:
        try:
            # Move to next frame
            gif_image.seek(frame_count)

            # Sample every 10th valid frame
            if frame_count % 10 == 0 and gif_image.getbbox():
                frame = gif_image.convert("RGB")
                enc_image = model.encode_image(frame)

                if isinstance(enc_image, torch.Tensor):
                    enc_image = enc_image.to(device)

                answer = model.answer_question(enc_image, question, tokenizer)
                answers.append(answer)

            frame_count += 1

        except EOFError: #End of Frames
            break

    # Return first valid answer depending on the frames that are been processed.
    return answers[0] if answers else "No answer could be generated from the GIF."


def object_detection(model, image, query):
    """
    Perform object detection on a single image and return an overlay image.
    Args:
        model: Loaded detection-capable model
        image: PIL.Image (original image, RGB)
        query: str (object to detect)
    Returns:
        PIL.Image with bounding boxes drawn
    """

    # Run detection
    detections = model.detect(image, query).get("objects", [])

    # Always draw on a fresh copy of the original image
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)

    width, height = overlay.size

    # Draw bounding boxes
    for box in detections:
        x_min = int(box["x_min"] * width)
        y_min = int(box["y_min"] * height)
        x_max = int(box["x_max"] * width)
        y_max = int(box["y_max"] * height)

        draw.rectangle(
            [x_min, y_min, x_max, y_max],
            outline="red",
            width=5
        )

    return overlay


def point_to_object(model, image, query):
    """
    Point to objects in an image by drawing numbered circles at detected points.
    Args:
        model: Loaded model with point-detection capability
        image: PIL.Image (original image, RGB)
        query: str describing object to point at
    Returns:
        PIL.Image overlay with numbered points
    """
    # Ensure image is RGB for drawing
    if image.mode != "RGB":
        image = image.convert("RGB")
    # Run point detection
    points_data = model.point(image, query).get("points", [])

    # Fresh overlay on original image
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    width, height = overlay.size

    # Circle radius
    r = 25

    # Use default font
    font = ImageFont.load_default()

    # Draw points
    for i, pt in enumerate(points_data, start=1):
        x = int(pt["x"] * width)
        y = int(pt["y"] * height)

        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill="lightblue",
            outline="white",
            width=5,
        )

        # Draw number inside circle
        text = str(i)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        draw.text(
            (x - text_w // 2, y - text_h // 2),
            text,
            fill="white",
            font=font,
        )

    return overlay


def build_chat_csv(chat_log):
    """
    Convert chat_log into CSV (Question, Response).
    Only user-ai pairs are considered.
    """

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Question", "Response"])

    temp_question = None
    temp_image_id = None

    for msg in chat_log:
        if msg["speaker"] == "user":
            temp_question = f"Image {msg['image_id']} — Question: {msg['message']}"
            temp_image_id = msg["image_id"]

        elif msg["speaker"] == "ai" and temp_question is not None:
            writer.writerow([temp_question, msg["message"]])
            temp_question = None
            temp_image_id = None

    return output.getvalue()


def image_to_bytes(image, format="PNG"):
    """
    Convert PIL Image to downloadable bytes.
    """
    buf = BytesIO()
    image.save(buf, format=format)
    buf.seek(0)
    return buf

#SUPABASE INSERT FUNCTION
def insert_user_activity(user_name, mode, question=None, response=None):
    """
    Insert a user activity record into Supabase via REST API.
    """

    payload = {
        "user_name": user_name,
        "mode": mode,
        "question": question,
        "response": response
    }

    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/user_activity",
            headers=SUPABASE_HEADERS,
            json=payload,
            timeout=10
        )

        if res.status_code not in (200, 201):
            print("DB INSERT FAILED:", res.text)

    except Exception as e:
        print("DB INSERT ERROR:", e)