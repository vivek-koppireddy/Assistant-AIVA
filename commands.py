import datetime
import webbrowser
import os
import random
import re
import json

def load_custom_commands():
    path = "custom_commands.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_custom_commands(cmds):
    path = "custom_commands.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cmds, f, indent=4)
    except Exception:
        pass

def load_android_state():
    path = "android_state.json"
    default_state = {
        "wifi": "ON",
        "bluetooth": "OFF",
        "flashlight": "OFF",
        "brightness": "70%",
        "volume": "80%",
        "notifications": [
            {"from": "Rahul", "app": "WhatsApp", "message": "I will arrive at 5 PM"},
            {"from": "Mom", "app": "Phone", "message": "Missed call from Mom"},
            {"from": "Calendar", "app": "System", "message": "Team Sync in 15 mins"}
        ],
        "logs": []
    }
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_state
    return default_state

def save_android_state(state):
    path = "android_state.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception:
        pass

def add_android_log(action_text):
    state = load_android_state()
    state["logs"].append(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action_text}")
    if len(state["logs"]) > 50:
        state["logs"] = state["logs"][-50:]
    save_android_state(state)

def normalize_command(command):
    command = command.lower()
    command = re.sub(r"[^a-z0-9\s]", " ", command)
    command = re.sub(r"\b(can you|could you|please|for me|thank you|thanks|hey|aiva)\b", " ", command)
    return re.sub(r"\s+", " ", command).strip()




def find_app(app_name):
    import shutil
    app_name_lower = app_name.lower().strip()
    
    # 1. Search Start Menu programs directories for shortcuts (.lnk)
    user_start_menu = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
    common_start_menu = os.path.join(os.environ.get("ProgramData", ""), "Microsoft", "Windows", "Start Menu", "Programs")
    local_programs = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")
    
    search_dirs = [user_start_menu, common_start_menu]
    if os.path.exists(local_programs):
        search_dirs.append(local_programs)
        
    matches = []
    
    for base_dir in search_dirs:
        if not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".lnk"):
                    name_without_ext = os.path.splitext(file.lower())[0]
                    # Direct match gets highest priority
                    if app_name_lower == name_without_ext:
                        matches.insert(0, os.path.join(root, file))
                    elif app_name_lower in name_without_ext:
                        matches.append(os.path.join(root, file))
                        
    # Remove duplicates preserving order
    seen = set()
    unique_matches = []
    for m in matches:
        m_lower = m.lower()
        if m_lower not in seen:
            seen.add(m_lower)
            unique_matches.append(m)
            
    if unique_matches:
        return unique_matches
        
    # 2. Check system PATH
    path_exe = shutil.which(app_name_lower)
    if path_exe:
        return [path_exe]
        
    return []


def find_folders(folder_name, max_depth=2):
    home = os.path.expanduser("~")
    target_lower = folder_name.lower().strip()
    
    # Standard search roots to prevent scanning the entire drive
    roots = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Music"),
        os.path.join(home, "Pictures"),
        os.path.join(home, "Videos"),
        home
    ]
    
    matches = []
    visited = set()
    
    def walk_depth(current_dir, current_depth):
        if current_depth > max_depth:
            return
            
        norm_dir = os.path.normpath(current_dir).lower()
        if norm_dir in visited:
            return
        visited.add(norm_dir)
        
        try:
            with os.scandir(current_dir) as it:
                for entry in it:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            entry_name_lower = entry.name.lower()
                            # Skip system, hidden, and AppData directories
                            if entry.name.startswith('.') or entry.name.startswith('$') or entry_name_lower in ('appdata', 'application data', 'local settings', 'my documents', 'cookies', 'nethood', 'printhood', 'recent', 'sendto', 'start menu', 'templates'):
                                continue
                                
                            if target_lower == entry_name_lower:
                                matches.insert(0, entry.path)
                            elif target_lower in entry_name_lower:
                                matches.append(entry.path)
                                
                            walk_depth(entry.path, current_depth + 1)
                    except Exception:
                        continue
        except Exception:
            return

    for root in roots:
        if os.path.exists(root):
            root_name_lower = os.path.basename(root).lower()
            if target_lower == root_name_lower:
                matches.insert(0, root)
            walk_depth(root, 1)
            
    seen = set()
    unique_matches = []
    for m in matches:
        m_lower = m.lower()
        if m_lower not in seen:
            seen.add(m_lower)
            unique_matches.append(m)
            
    return unique_matches


def parse_search_command(cleaned):
    is_folder = False
    is_app = False
    
    temp = cleaned.strip()
    
    # Check for folder/app keywords
    if "folder" in temp:
        is_folder = True
    elif "app" in temp or "application" in temp:
        is_app = True
        
    # Strip suffixes
    suffixes = [" folder", " application", " app"]
    for suffix in suffixes:
        if temp.endswith(suffix):
            temp = temp[:-len(suffix)].strip()
            
    # Strip prefixes
    prefixes = [
        "open folder ", "open folder", "open application ", "open app ", "open ",
        "search for folder ", "search for application ", "search for app ", "search for ",
        "search folder ", "search application ", "search app ", "search ",
        "find folder ", "find application ", "find app ", "find ",
        "show me folder ", "show me application ", "show me app ", "show me ",
        "go to folder ", "go to ",
        "run application ", "run app ", "run ",
        "execute application ", "execute app ", "execute ",
        "launch application ", "launch app ", "launch ",
        "start application ", "start app ", "start "
    ]
    
    prefixes.sort(key=len, reverse=True)
    
    for prefix in prefixes:
        if temp.startswith(prefix):
            temp = temp[len(prefix):].strip()
            break
            
    return temp, is_folder, is_app


def check_knowledge_base(cleaned):
    try:
        kb_path = "knowledge_base.txt"
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                if ":" in line:
                    question, answer = line.split(":", 1)
                    norm_q = re.sub(r"[^a-z0-9\s]", " ", question.lower())
                    norm_q = re.sub(r"\s+", " ", norm_q).strip()
                    if norm_q == cleaned or norm_q in cleaned or cleaned in norm_q:
                        return answer.strip()
    except Exception:
        pass
    return None


def handle_generic_open(cleaned, speak):
    import subprocess
    import shutil
    import webbrowser
    
    # 1. Check knowledge base
    kb_answer = check_knowledge_base(cleaned)
    if kb_answer:
        speak(kb_answer)
        return
        
    # 2. Check if it is a question or a general web search query
    # E.g. "what is java", "search for new movies", "look up recipes"
    web_query_prefixes = ["what is ", "who is ", "how to ", "why is ", "where is ", "define ", "explain ", "search for ", "search ", "look up "]
    for prefix in web_query_prefixes:
        if cleaned.startswith(prefix):
            query = cleaned[len(prefix):].strip()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={cleaned}")
                speak(f"Searching Google for {query}")
                return

    # 3. Extract target
    target, is_folder, is_app = parse_search_command(cleaned)
    
    if not target:
        speak("I didn't catch the name of the folder or application you want to open.")
        return

    if is_folder:
        speak(f"Searching for folder {target}...")
        folders = find_folders(target)
        if folders:
            speak(f"Opening folder {os.path.basename(folders[0])}")
            try:
                os.startfile(folders[0])
            except Exception as e:
                speak(f"Failed to open folder: {str(e)}")
        else:
            # Fallback: Ask if they want to search Google
            webbrowser.open(f"https://www.google.com/search?q={target}")
            speak(f"I couldn't find a folder named {target}. Searching Google instead.")
            
    elif is_app:
        speak(f"Searching for application {target}...")
        apps = find_app(target)
        if apps:
            speak(f"Opening {os.path.basename(apps[0]).replace('.lnk', '').replace('.exe', '')}")
            try:
                os.startfile(apps[0])
            except Exception as e:
                speak("I found the application but failed to open it.")
        else:
            if shutil.which(target):
                speak(f"Opening {target}")
                try:
                    subprocess.Popen(target, shell=True)
                except Exception:
                    speak(f"Failed to open application {target}")
            else:
                # Fallback to Google Search
                webbrowser.open(f"https://www.google.com/search?q={target}")
                speak(f"I couldn't find an application named {target}. Searching Google instead.")
                
    else:
        # Generic query - try app first, then folder, then PATH
        apps = find_app(target)
        if apps:
            speak(f"Opening {os.path.basename(apps[0]).replace('.lnk', '').replace('.exe', '')}")
            try:
                os.startfile(apps[0])
                return
            except Exception:
                pass
                
        folders = find_folders(target)
        if folders:
            speak(f"Opening folder {os.path.basename(folders[0])}")
            try:
                os.startfile(folders[0])
                return
            except Exception:
                pass
                
        if shutil.which(target):
            speak(f"Opening {target}")
            try:
                subprocess.Popen(target, shell=True)
                return
            except Exception:
                pass
                
        # Ultimate fallback: Search Google for the target
        webbrowser.open(f"https://www.google.com/search?q={target}")
        speak(f"I couldn't find any application or folder named {target}. Searching Google instead.")



def process_command(command, speak):
    cleaned = normalize_command(command)

    if not cleaned:
        speak("I didn't catch that command.")
        return

    # ==========================================
    # 1. Custom Command Training & Management
    # ==========================================
    
    # Train Custom Command mapping: "train command [phrase] to [action]"
    # Match against the raw command (case-insensitive) to preserve symbols like dot, slash, colon
    train_cmd_match = re.search(r"^(?:train|remember)\s+command\s+(.+?)\s+(?:to|runs|opens|runs command)\s+(.+)$", command, re.IGNORECASE)
    if train_cmd_match:
        phrase = normalize_command(train_cmd_match.group(1))
        action = train_cmd_match.group(2).strip()
        
        custom_cmds = load_custom_commands()
        custom_cmds[phrase] = action
        save_custom_commands(custom_cmds)
        speak(f"I will now run '{action}' when you say '{phrase}'.")
        add_android_log(f"Trained Command: '{phrase}' -> '{action}'")
        return

    # Train Q&A Knowledge: "train [question] is [answer]"
    # Match against the raw command, ensuring it is not a "train command"
    if not cleaned.startswith("train command") and not cleaned.startswith("remember command"):
        train_qa_match = re.search(r"^(?:train|remember that|teach you that|teach you|remember)\s+(.+?)\s+(?:is|means|to be)\s+(.+)$", command, re.IGNORECASE)
        if train_qa_match:
            q = normalize_command(train_qa_match.group(1))
            a = train_qa_match.group(2).strip()
            
            # Append to knowledge_base.txt
            try:
                with open("knowledge_base.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n{q} : {a}")
                speak(f"I've learned that {q} is {a}.")
                add_android_log(f"Trained Q&A: '{q}' -> '{a}'")
                return
            except Exception:
                speak("Sorry, I couldn't save that information.")
                return

    # Forget Custom Command
    if cleaned.startswith("forget command "):
        phrase = cleaned.replace("forget command ", "").strip()
        custom_cmds = load_custom_commands()
        if phrase in custom_cmds:
            del custom_cmds[phrase]
            save_custom_commands(custom_cmds)
            speak(f"I have forgotten the command '{phrase}'.")
            add_android_log(f"Forgot Command: '{phrase}'")
        else:
            speak(f"I don't have a custom command registered for '{phrase}'.")
        return
        
    # Forget Knowledge
    elif cleaned.startswith("forget knowledge ") or cleaned.startswith("forget that "):
        q = cleaned.replace("forget knowledge ", "").replace("forget that ", "").strip()
        kb_path = "knowledge_base.txt"
        found = False
        if os.path.exists(kb_path):
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    if ":" in line:
                        question, answer = line.split(":", 1)
                        norm_q = re.sub(r"[^a-z0-9\s]", " ", question.lower())
                        norm_q = re.sub(r"\s+", " ", norm_q).strip()
                        if norm_q == q or q in norm_q or norm_q in q:
                            found = True
                            continue
                    new_lines.append(line)
                with open(kb_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                if found:
                     speak(f"I have forgotten about '{q}'.")
                     add_android_log(f"Forgot Knowledge: '{q}'")
                else:
                     speak(f"I couldn't find '{q}' in my knowledge base.")
            except Exception:
                speak("Sorry, I had an error updating my knowledge base.")
        else:
            speak("My knowledge base is empty.")
        return

    # List custom elements
    elif cleaned in ["list trained knowledge", "list knowledge"]:
        kb_path = "knowledge_base.txt"
        items = []
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if ":" in line:
                        items.append(line.strip())
        if items:
            speak("Here is what I know: " + ", ".join(items))
        else:
            speak("I don't have any custom knowledge trained yet.")
        return
        
    elif cleaned in ["list custom commands", "list commands"]:
        custom_cmds = load_custom_commands()
        if custom_cmds:
            lines = [f"'{k}' runs '{v}'" for k, v in custom_cmds.items()]
            speak("Here are my custom commands: " + ", ".join(lines))
        else:
            speak("I don't have any custom commands trained yet.")
        return

    # ==========================================
    # 2. Simulated Android Device Control
    # ==========================================

    # Flashlight control
    elif "flashlight" in cleaned:
        state = load_android_state()
        if "on" in cleaned:
            state["flashlight"] = "ON"
            save_android_state(state)
            speak("Flashlight is now turned ON.")
            add_android_log("Simulated Android: Flashlight turned ON")
            return
        elif "off" in cleaned:
            state["flashlight"] = "OFF"
            save_android_state(state)
            speak("Flashlight is now turned OFF.")
            add_android_log("Simulated Android: Flashlight turned OFF")
            return

    # Wi-Fi control
    elif "wifi" in cleaned or "wi fi" in cleaned:
        state = load_android_state()
        if "on" in cleaned:
            state["wifi"] = "ON"
            save_android_state(state)
            speak("Wi-Fi is now turned ON.")
            add_android_log("Simulated Android: Wi-Fi turned ON")
            return
        elif "off" in cleaned:
            state["wifi"] = "OFF"
            save_android_state(state)
            speak("Wi-Fi is now turned OFF.")
            add_android_log("Simulated Android: Wi-Fi turned OFF")
            return

    # Bluetooth control
    elif "bluetooth" in cleaned:
        state = load_android_state()
        if "on" in cleaned:
            state["bluetooth"] = "ON"
            save_android_state(state)
            speak("Bluetooth is now turned ON.")
            add_android_log("Simulated Android: Bluetooth turned ON")
            return
        elif "off" in cleaned:
            state["bluetooth"] = "OFF"
            save_android_state(state)
            speak("Bluetooth is now turned OFF.")
            add_android_log("Simulated Android: Bluetooth turned OFF")
            return

    # Volume setting
    elif "volume" in cleaned and ("set" in cleaned or "to" in cleaned):
        volume_match = re.search(r"(\d+)\s*%?", cleaned)
        if volume_match:
            val = int(volume_match.group(1))
            if 0 <= val <= 100:
                state = load_android_state()
                state["volume"] = f"{val}%"
                save_android_state(state)
                speak(f"Volume set to {val} percent.")
                add_android_log(f"Simulated Android: Volume set to {val}%")
            else:
                speak("Please specify a volume level between 0 and 100.")
            return

    # Brightness setting
    elif "brightness" in cleaned and ("set" in cleaned or "to" in cleaned):
        brightness_match = re.search(r"(\d+)\s*%?", cleaned)
        if brightness_match:
            val = int(brightness_match.group(1))
            if 0 <= val <= 100:
                state = load_android_state()
                state["brightness"] = f"{val}%"
                save_android_state(state)
                speak(f"Brightness set to {val} percent.")
                add_android_log(f"Simulated Android: Brightness set to {val}%")
            else:
                speak("Please specify a brightness level between 0 and 100.")
            return

    # ==========================================
    # 3. Simulated Android Communication
    # ==========================================

    # Call simulation
    elif cleaned.startswith("call "):
        recipient = cleaned.replace("call ", "").strip().title()
        speak(f"Calling {recipient}...")
        add_android_log(f"Simulated Android: Placing call to {recipient}")
        return

    # WhatsApp message simulation
    elif ("whatsapp" in cleaned or "message" in cleaned or "saying" in cleaned) and re.search(r"^(?:send\s+)?(?:a\s+)?(?:whatsapp\s+)?(?:message\s+to\s+)?(\w+)\s+(?:saying|with)\s+(.+)$", cleaned):
        wa_match = re.search(r"^(?:send\s+)?(?:a\s+)?(?:whatsapp\s+)?(?:message\s+to\s+)?(\w+)\s+(?:saying|with)\s+(.+)$", cleaned)
        recipient = wa_match.group(1).title()
        msg = wa_match.group(2).strip()
        speak(f"Sending message to {recipient} saying {msg}.")
        add_android_log(f"Simulated Android: Sent WhatsApp to {recipient}: '{msg}'")
        return

    # Notification Summarizing / Reading
    elif cleaned in ["read latest messages", "read my latest messages", "summarize notifications", "read my notifications", "notifications", "read messages", "messages"]:
        state = load_android_state()
        notifs = state.get("notifications", [])
        if notifs:
            summary_lines = []
            for n in notifs:
                summary_lines.append(f"a {n['app']} message from {n['from']} saying '{n['message']}'")
            speak("You have the following notifications: " + "; ".join(summary_lines))
            add_android_log("Simulated Android: Read notifications to user")
        else:
            speak("You have no new notifications.")
        return

    # Open simulated Android Apps
    elif cleaned == "open instagram":
        speak("Opening Instagram.")
        add_android_log("Simulated Android: Opened Instagram app screen")
        webbrowser.open("https://instagram.com")
        return

    elif cleaned == "open whatsapp":
        speak("Opening WhatsApp.")
        add_android_log("Simulated Android: Opened WhatsApp chat list screen")
        webbrowser.open("https://web.whatsapp.com")
        return

    elif cleaned == "open settings":
        speak("Opening device settings.")
        add_android_log("Simulated Android: Opened Settings panel screen")
        return

    # ==========================================
    # 4. Standard Desktop Command Fallbacks
    # ==========================================

    elif "time" in cleaned:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak("The time is " + current_time)

    elif "date" in cleaned:
        current_date = datetime.datetime.now().strftime("%d %B %Y")
        speak("Today is " + current_date)

    elif "open google" in cleaned or "go to google" in cleaned or "visit google" in cleaned or ("google" in cleaned and ("open" in cleaned or "browser" in cleaned or "visit" in cleaned)):
        webbrowser.open("https://google.com")
        speak("Opening Google")

    elif "open youtube" in cleaned or "play youtube" in cleaned or "youtube" in cleaned:
        # Check if searching inside youtube
        youtube_search_match = re.search(r"youtube\s+and\s+search\s+for\s+(.+)$", cleaned)
        if youtube_search_match:
            query = youtube_search_match.group(1).strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            speak(f"Opening YouTube and searching for {query}")
            add_android_log(f"Simulated Android: Searching YouTube for '{query}'")
        else:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")
        return

    elif "open calculator" in cleaned or "calculator" in cleaned:
        os.system("calc")
        speak("Opening Calculator")

    elif "open notepad" in cleaned or "notepad" in cleaned:
        os.system("notepad")
        speak("Opening Notepad")

    elif "open chrome" in cleaned or ("open" in cleaned and "browser" in cleaned) or ("start" in cleaned and "chrome" in cleaned):
        webbrowser.open("https://www.google.com")
        speak("Opening Chrome browser")

    elif "documents" in cleaned and ("folder" in cleaned or "document" in cleaned or "documents folder" in cleaned or "my documents" in cleaned):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.exists(documents_path):
            os.startfile(documents_path)
            speak("Opening your Documents folder")
        else:
            speak("I couldn't find your Documents folder")

    elif "play music" in cleaned or ("play" in cleaned and "music" in cleaned):
        music_folder = "music"
        if os.path.isdir(music_folder):
            songs = [file for file in os.listdir(music_folder) if file.lower().endswith((".mp3", ".wav", ".m4a", ".flac"))]
            if songs:
                os.startfile(os.path.join(music_folder, random.choice(songs)))
                speak("Playing music")
            else:
                speak("I couldn't find any music files in the music folder")
        else:
            speak("I couldn't find the music folder")

    elif "joke" in cleaned or "tell me a joke" in cleaned:
        try:
            with open("jokes.txt") as f:
                jokes = [line.strip() for line in f.readlines() if line.strip()]
            if jokes:
                speak(random.choice(jokes))
            else:
                speak("I don't have any jokes right now.")
        except FileNotFoundError:
            speak("I couldn't find the jokes file.")

    elif "help" in cleaned or "what can you do" in cleaned or "list commands" in cleaned or "commands" in cleaned:
        speak("I can tell the time, tell the date, open Google, YouTube, Chrome, Calculator, Notepad, open your Documents folder, play music, and tell jokes. You can also train me by saying: train [question] is [answer], or train command [phrase] to [action]. Say stop to exit.")
    
    elif "open chatgpt" in cleaned or ("open" in cleaned and "chatgpt" in cleaned) or ("start" in cleaned and "chatgpt" in cleaned):
        webbrowser.open("https://chatgpt.com/")
        speak("Opening ChatGPT")

    elif "search google for" in cleaned or "search on google for" in cleaned or "google search" in cleaned:
        target = cleaned.replace("search google for", "").replace("search on google for", "").replace("google search", "").strip()
        if target:
            webbrowser.open(f"https://www.google.com/search?q={target}")
            speak(f"Searching Google for {target}")
        else:
            speak("What would you like me to search on Google?")

    # ==========================================
    # 5. Executing Trained Custom Commands
    # ==========================================
    else:
        custom_cmds = load_custom_commands()
        if cleaned in custom_cmds:
            action = custom_cmds[cleaned]
            speak(f"Executing custom command for '{cleaned}'.")
            add_android_log(f"Executed custom command: '{cleaned}' -> '{action}'")
            if action.startswith("http://") or action.startswith("https://"):
                webbrowser.open(action)
            elif os.path.exists(action):
                try:
                    os.startfile(action)
                except Exception as e:
                    speak(f"Failed to open: {str(e)}")
            else:
                import subprocess
                try:
                    subprocess.Popen(action, shell=True)
                except Exception:
                    os.system(action)
            return

        handle_generic_open(cleaned, speak)