# 🌳 Pine – Vision Language Model Web Application

Pine is a multimodal AI application that enables users to interact with images using natural language. By combining visual understanding and language reasoning, the system allows users to upload images, ask questions, detect objects, and locate specific items through an intuitive web interface.

This project demonstrates how Vision Language Models (VLMs) can bridge the gap between visual understanding and human interaction, making AI more accessible and practical for real-world applications.

---

## 📸 Application Preview

### Main Interface

![Pine Main Interface](assets/ui-home.jpg)

### Image Analysis Workspace

![Pine Analysis Workspace](assets/ui-analysis.jpg)

---

## 🚀 Features

### 🧠 Chat With Image

Interact with uploaded images using natural language prompts.

**Examples**

* What is happening in this image?
* Describe the scene.
* What objects are visible?
* What might be occurring in the background?

The Vision Language Model analyzes both image and text inputs to generate contextual responses.

### 🎯 Object Detection

Detect and identify objects present in an image.

**Capabilities**

* Multiple object detection
* Bounding box visualization
* Downloadable detection results

### 📍 Point to Object

Locate and highlight specific objects requested by the user.

**Examples**

* Find the laptop
* Point to the bicycle
* Locate the person

### 📥 Export Functionality

Download generated outputs including:

* Chat history as CSV
* Object detection results as images
* Pointing results as images

### 💾 Activity Logging

Store user interactions for administrative monitoring and analysis using Supabase PostgreSQL.

---

## 🎯 Problem Statement

Traditional AI systems often separate image understanding from conversational interaction.

### Challenges

* Image processing systems primarily focus on object detection.
* Conversational AI systems primarily understand text.
* Many advanced multimodal solutions require paid access or usage restrictions.

### Our Solution

Pine combines image understanding and natural language interaction into a single platform where users can:

* Interact naturally with images
* Ask unlimited questions about uploaded content
* Detect and locate objects
* Store and retrieve interaction history
* Access multimodal AI through a simple web interface

---

## 🛠 Technology Stack

| Component             | Technology            |
| --------------------- | --------------------- |
| Frontend              | Streamlit             |
| Backend               | Python                |
| Vision Language Model | Moondream             |
| Database              | Supabase PostgreSQL   |
| Deployment            | Hugging Face Spaces   |
| Image Processing      | Pillow, PyVips        |
| AI Framework          | Transformers, PyTorch |

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pine
```

### 2. Install System Dependencies

#### Linux (Required for PyVips)

```bash
sudo apt-get update
sudo apt-get install -y libvips42 libvips-dev
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 5. Run the Application

```bash
streamlit run app.py
```

---

## 🗄 Database Setup

Pine uses PostgreSQL through Supabase to store user interactions and application activity logs.

1. Create a new Supabase project.
2. Open the SQL Editor.
3. Execute the SQL script located at:

```text
database/pine_schema.sql
```

4. Navigate to **Project Settings → API**.
5. Copy your **Project URL** and **Anon Key**.
6. Add them to your `.env` file.

The application will automatically connect to your Supabase database.

---

## 📁 Project Structure

```text
pine/
├── ui-home.png
├── ui-analysis.png
├── pine_schema.sql
├── style.css
├── app.py
├── backend.py
├── requirements.txt
├── packages.txt
├── .env.example
├── .gitignore
└── README.md
```

```

---

## ✅ Advantages

* Simple and intuitive user interface
* Multimodal AI interaction
* Lightweight and efficient Vision Language Model
* Cloud deployment support
* Multiple AI-powered capabilities in one platform
* Downloadable outputs and interaction tracking

---

## ⚠️ Limitations

* Performance depends on model accuracy
* Responses may occasionally contain hallucinations
* Large images and GIF processing can be resource intensive
* GPU hardware is recommended for optimal performance

---

## 🔮 Future Scope

* 🎥 Video understanding and analysis
* 🗣 Voice input and output
* 🤖 Robotics integration
* 📱 Mobile application support
* 🧠 Domain-specific fine-tuned models

  * Medical Imaging
  * Security Systems
  * Scientific Research
* ⚡ Real-time camera analysis

---

## 🌍 Potential Applications

* Education
* Healthcare
* Surveillance
* Assistive Technologies
* Forensics
* Retail Analytics
* Scientific Research
* Space Exploration

---

## 💎 Acknowledgements

This project utilizes the Moondream Vision Language Model.

Model Repository:

https://huggingface.co/vikhyatk/moondream2

Credit for the model architecture, training methodology, weights, and research contributions belongs to the original authors and maintainers of the Moondream project.

---

## 📄 License

This project is intended for educational, research, and demonstration purposes.
