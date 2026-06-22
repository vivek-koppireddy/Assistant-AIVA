import os
import re
import json
from commands import process_command, load_custom_commands, save_custom_commands, load_android_state, save_android_state

def test_suite():
    print("=" * 60)
    print("RUNNING AUTOMATED UNIT TESTS FOR AIVA COMMANDS...")
    print("=" * 60)

    # 1. Back up existing databases
    kb_backup = None
    if os.path.exists("knowledge_base.txt"):
        with open("knowledge_base.txt", "r", encoding="utf-8") as f:
            kb_backup = f.read()
    
    cmd_backup = None
    if os.path.exists("custom_commands.json"):
        with open("custom_commands.json", "r", encoding="utf-8") as f:
            cmd_backup = f.read()
            
    state_backup = None
    if os.path.exists("android_state.json"):
        with open("android_state.json", "r", encoding="utf-8") as f:
            state_backup = f.read()

    # Clear/initialize databases for clean testing
    with open("knowledge_base.txt", "w", encoding="utf-8") as f:
        f.write("who created you : Python technology\n")
        
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        f.write("{}")

    if os.path.exists("android_state.json"):
        os.remove("android_state.json")

    # Mocks
    last_spoken = []
    def mock_speak(text):
        last_spoken.append(text)

    try:
        # TEST 1: Basic Q&A Knowledge Lookup
        last_spoken.clear()
        process_command("who created you", mock_speak)
        assert len(last_spoken) > 0, "Failed: Should speak a response"
        assert "Python technology" in last_spoken[0], f"Failed: Expected Python technology, got {last_spoken}"
        print("[PASS] Test 1: Basic Q&A Lookup")

        # TEST 2: Dynamic Q&A Training
        last_spoken.clear()
        process_command("train my super power is coding", mock_speak)
        assert any("learned" in s or "remember" in s for s in last_spoken), f"Failed: Expected training confirmation, got {last_spoken}"
        
        last_spoken.clear()
        process_command("my super power", mock_speak)
        assert len(last_spoken) > 0 and "coding" in last_spoken[0], f"Failed: Expected trained answer 'coding', got {last_spoken}"
        print("[PASS] Test 2: Dynamic Q&A Training & Retrieval")

        # TEST 3: Dynamic Command Training
        last_spoken.clear()
        process_command("train command watch logs to notepad.exe", mock_speak)
        assert any("notepad.exe" in s for s in last_spoken), f"Failed: Expected custom command confirmation, got {last_spoken}"
        
        cmds = load_custom_commands()
        assert cmds.get("watch logs") == "notepad.exe", f"Failed: custom command mapping incorrect: {cmds}"
        print("[PASS] Test 3: Dynamic Custom Command Training")

        # TEST 4: Android Wi-Fi Simulation
        last_spoken.clear()
        process_command("turn off wifi", mock_speak)
        state = load_android_state()
        assert state["wifi"] == "OFF", f"Failed: Wi-Fi should be OFF, got {state}"
        assert any("off" in s.lower() for s in last_spoken), f"Failed: Expected speaker output confirming OFF, got {last_spoken}"
        print("[PASS] Test 4: Android Wi-Fi toggle")

        # TEST 5: Android Volume level simulation
        last_spoken.clear()
        process_command("set volume to 85 percent", mock_speak)
        state = load_android_state()
        assert state["volume"] == "85%", f"Failed: Volume level should be 85%, got {state}"
        print("[PASS] Test 5: Android Volume adjustment")

        # TEST 6: Android Notification spawning & reading
        last_spoken.clear()
        # Mock add a notification
        state = load_android_state()
        state["notifications"] = [{"from": "Vivek", "app": "WhatsApp", "message": "Tests are passing!"}]
        save_android_state(state)
        
        process_command("read my latest messages", mock_speak)
        assert any("Vivek" in s and "WhatsApp" in s and "passing" in s for s in last_spoken), f"Failed: Did not read notification, got {last_spoken}"
        print("[PASS] Test 6: Android Notification reading")

        # TEST 7: Forget Trained elements
        last_spoken.clear()
        process_command("forget knowledge my super power", mock_speak)
        last_spoken.clear()
        process_command("my super power", mock_speak)
        # Should not find it in knowledge base
        assert not any("coding" in s for s in last_spoken), "Failed: Knowledge was not forgotten"
        print("[PASS] Test 7: Forget trained knowledge")

        print("=" * 60)
        print("ALL AUTOMATED TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    finally:
        # Restore backups
        if kb_backup is not None:
            with open("knowledge_base.txt", "w", encoding="utf-8") as f:
                f.write(kb_backup)
        else:
            if os.path.exists("knowledge_base.txt"):
                os.remove("knowledge_base.txt")

        if cmd_backup is not None:
            with open("custom_commands.json", "w", encoding="utf-8") as f:
                f.write(cmd_backup)
        else:
            if os.path.exists("custom_commands.json"):
                os.remove("custom_commands.json")

        if state_backup is not None:
            with open("android_state.json", "w", encoding="utf-8") as f:
                f.write(state_backup)
        else:
            if os.path.exists("android_state.json"):
                os.remove("android_state.json")

if __name__ == "__main__":
    test_suite()
