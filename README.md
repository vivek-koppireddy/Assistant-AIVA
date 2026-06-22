# 🤖 AIVA — Artificial Intelligent Virtual Assistant

AIVA is a highly interactive, cross-platform virtual assistant designed to run as a Windows desktop utility, an interactive console CLI, and a dynamic web application. It features automated system app execution, directory traversal, dynamic knowledge training (real-time Q&A adaptation), custom command mapping, and a simulated Android device manager.

---

## 🌟 Key Features

### 🎙️ Multi-Modal Interfaces
*   **Web Dashboard**: A fully responsive web interface featuring glassmorphic design, simulated device dashboard, real-time command processing log console, and custom training managers.
*   **Desktop Voice Mode**: A hands-free, voice-activated desktop assistant using speech recognition and local text-to-speech synthesis (offline fallback supported).
*   **Interactive Console CLI**: A lightweight, colorized terminal console for command-line control of the assistant.

### 🧠 Dynamic Knowledge Training & Q&A
*   Teach AIVA facts in real-time. For example: `train AIVA is the best assistant`. AIVA remembers and retrieves this knowledge dynamically.
*   Manage trained knowledge directly via voice, text, or the web dashboard.
*   Commands to view (`list knowledge`) or remove (`forget knowledge [fact]`) facts are supported out of the box.

### ⚙️ Custom Command Training
*   Register custom shortcut commands dynamically, mapping text triggers to system programs, files, folders, or web URLs.
*   Example: `train command watch logs to notepad.exe` registers `watch logs` as a trigger to open Notepad.
*   Supports opening websites/URLs, opening local files/folders, and running local scripts/executables.

### 📱 Simulated Android Device Manager
*   Simulate a connected Android device's hardware toggle states: Wi-Fi, Bluetooth, Flashlight, Volume, and Brightness.
*   Send simulated WhatsApp messages or trigger calls.
*   Inspect and read notifications aloud via voice or web dashboard logs.
*   Persists simulation state in `android_state.json`.

### 📂 Intelligent Windows Shell Navigation
*   **App Launcher**: Automatically walks Windows Start Menu directories and scans system PATH to search, locate, and launch installed applications (like Chrome, Word, Slack, etc.).
*   **Folder Finder**: Searches standard user directories (`Desktop`, `Documents`, `Downloads`, `Music`, `Pictures`, `Videos`) down to specified depths to open requested directories directly.
*   **Web Fallback**: Intelligently falls back to a web search on Google if the app/folder is not found locally.

---

## 📂 Project Structure

Here is an overview of the codebase architecture:

```text
├── main.py               # Main desktop voice entry point (Speech Recognition & TTS)
├── app.py                # Flask application backend exposing web UI & JSON APIs
├── commands.py           # Core command-processing engine and hardware simulator
├── text_main.py          # Interactive console-only CLI runner
├── test_commands.py      # Automated unit test suite validating core engine features
├── requirements.txt      # Python package dependencies
├── android_state.json    # JSON database for the simulated Android device state
├── custom_commands.json  # Database for trained custom trigger -> action mappings
├── knowledge_base.txt    # Flat text file storage for AIVA's trained QA knowledge base
├── jokes.txt             # Text database containing jokes for the /joke command
├── static/               # Assets served by the Flask app
│   ├── css/style.css     # Premium styling with glassmorphism & responsive grid
│   └── js/main.js        # Frontend state management, web API clients & sound effects
└── templates/
    └── index.html        # Main web dashboard interface template
```

---

## 🛠️ Prerequisites & Installation

To run AIVA locally, ensure you have Python (version 3.8 or higher) installed on your system.

1.  **Clone or navigate to the repository directory**:
    ```bash
    cd d:/assist
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If running the desktop voice mode, make sure your microphone input is active and configure your OS audio drivers (e.g., PyAudio is required).*

3.  *(Optional)* **Install Web GUI dependencies**:
    ```bash
    pip install flask
    ```

---

## 🚀 How to Run

### 1. Web Application Mode (Recommended)
Launch the Flask development server to access the premium web dashboard.
```bash
python app.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### 2. Interactive Console Mode
Run AIVA in a lightweight terminal shell session.
```bash
python text_main.py
```

### 3. Desktop Voice Assistant Mode
Launch the desktop listener which waits for wake-up speech commands.
```bash
python main.py
```

### 4. Running the Automated Test Suite
To verify that all command parsers, Q&A training mechanisms, and state managers are operating correctly:
```bash
python test_commands.py
```

---

## 📖 Command Guide & Cheatsheet

Below are command formats that AIVA parses. You can execute these through any interface:

| Category | Voice / Console Command Example | Description |
| :--- | :--- | :--- |
| **System Apps** | `open Chrome` / `launch Calculator` | Locates and opens application executable |
| **Folders** | `open downloads folder` / `go to documents` | Locates folder in standard paths and opens in Explorer |
| **Q&A Training** | `train my favorite language is Python` | Teaches AIVA a custom fact |
| **QA Retrieval** | `what is my favorite language` | Retrieves trained fact from the knowledge base |
| **QA Forgetting** | `forget knowledge my favorite language` | Removes the fact from the knowledge base |
| **Command Training**| `train command open code to path/to/editor` | Binds a phrase to launch an executable, URL, or file |
| **Simulate Hardware**| `turn off wifi` / `set volume to 80 percent` | Adjusts simulated Android state |
| **Communication** | `send whatsapp message to John saying Hello` | Sends simulated messaging payload |
| **Notifications** | `read latest messages` / `summarize notifications` | Reads simulated Android notification queue |
| **Web Fallback** | `search google for quantum physics` | Opens browser with Google search results |
| **Entertainment** | `tell me a joke` | Reads a random joke |

---

## 🛠️ Built With

*   **Python**: Core programming language.
*   **Flask**: Lightweight web backend for state synchronization and API routes.
*   **SpeechRecognition & pyttsx3**: Python wrappers for speech-to-text and offline text-to-speech.
*   **HTML5, Vanilla CSS, Vanilla JavaScript**: Modern dashboard interface with glassmorphism, responsive grid, dynamic alerts, and real-time state visualization.
