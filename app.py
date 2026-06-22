from flask import Flask, render_template, request, jsonify
import os
import re
import json
from commands import process_command, load_android_state, save_android_state, load_custom_commands, save_custom_commands

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/command", methods=["POST"])
def run_command_api():
    data = request.get_json() or {}
    cmd = data.get("command", "").strip()
    if not cmd:
        return jsonify({"responses": ["I didn't catch that command."]})
    
    responses = []
    def collect_speak(text):
        responses.append(text)
    
    process_command(cmd, collect_speak)
    if not responses:
        responses.append("Command processed.")
        
    return jsonify({
        "responses": responses,
        "state": load_android_state()
    })

@app.route("/api/state", methods=["GET", "POST"])
def state_api():
    if request.method == "POST":
        data = request.get_json() or {}
        state = load_android_state()
        for key in ["wifi", "bluetooth", "flashlight", "brightness", "volume"]:
            if key in data:
                state[key] = data[key]
        if "add_notification" in data:
            notif = data["add_notification"]
            if "from" in notif and "app" in notif and "message" in notif:
                state["notifications"].insert(0, {
                    "from": notif["from"],
                    "app": notif["app"],
                    "message": notif["message"]
                })
                state["notifications"] = state["notifications"][:10]
        if "clear_notifications" in data:
            state["notifications"] = []
        save_android_state(state)
        return jsonify(state)
    else:
        return jsonify(load_android_state())

@app.route("/api/knowledge", methods=["GET", "POST", "DELETE"])
def knowledge_api():
    kb_path = "knowledge_base.txt"
    if request.method == "GET":
        items = []
        if os.path.exists(kb_path):
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    for line in f.readlines():
                        if ":" in line:
                            q, a = line.split(":", 1)
                            items.append({"question": q.strip(), "answer": a.strip()})
            except Exception:
                pass
        return jsonify(items)
        
    elif request.method == "POST":
        data = request.get_json() or {}
        q = data.get("question", "").strip()
        a = data.get("answer", "").strip()
        if q and a:
            try:
                with open(kb_path, "a", encoding="utf-8") as f:
                    f.write(f"\n{q} : {a}")
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        return jsonify({"status": "error", "message": "Missing question or answer"}), 400
        
    elif request.method == "DELETE":
        data = request.get_json() or {}
        q = data.get("question", "").strip().lower()
        if q:
            try:
                if os.path.exists(kb_path):
                    with open(kb_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    new_lines = []
                    deleted = False
                    for line in lines:
                        if ":" in line:
                            question, answer = line.split(":", 1)
                            norm_q = re.sub(r"[^a-z0-9\s]", " ", question.lower())
                            norm_q = re.sub(r"\s+", " ", norm_q).strip()
                            if norm_q == q or q in norm_q or norm_q in q:
                                deleted = True
                                continue
                        new_lines.append(line)
                    with open(kb_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    return jsonify({"status": "success", "deleted": deleted})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        return jsonify({"status": "error", "message": "Missing question identifier"}), 400

@app.route("/api/commands", methods=["GET", "POST", "DELETE"])
def commands_api():
    if request.method == "GET":
        cmds = load_custom_commands()
        return jsonify([{"phrase": k, "action": v} for k, v in cmds.items()])
        
    elif request.method == "POST":
        data = request.get_json() or {}
        phrase = data.get("phrase", "").strip().lower()
        action = data.get("action", "").strip()
        if phrase and action:
            cmds = load_custom_commands()
            cmds[phrase] = action
            save_custom_commands(cmds)
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Missing phrase or action"}), 400
        
    elif request.method == "DELETE":
        data = request.get_json() or {}
        phrase = data.get("phrase", "").strip().lower()
        if phrase:
            cmds = load_custom_commands()
            if phrase in cmds:
                del cmds[phrase]
                save_custom_commands(cmds)
                return jsonify({"status": "success"})
            return jsonify({"status": "error", "message": "Command not found"}), 404
        return jsonify({"status": "error", "message": "Missing phrase"}), 400

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=True)
