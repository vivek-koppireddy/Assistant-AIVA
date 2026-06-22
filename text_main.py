import sys
from commands import process_command

def console_speak(text):
    print(f"\033[94mAIVA:\033[0m {text}")

def main():
    print("=" * 60)
    print("\033[92mStarting AIVA (Interactive Console Mode)...\033[0m")
    print("Type your commands below. Say 'stop', 'quit', or 'exit' to exit.")
    print("=" * 60)
    
    console_speak("Hello. I am AIVA. How can I help you?")

    while True:
        try:
            command = input("\033[93mYou:\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            console_speak("Goodbye")
            break

        if not command:
            continue

        if command.lower() in ["stop", "quit", "exit", "stop aiva"]:
            console_speak("Goodbye")
            break

        # Process the command
        process_command(command, console_speak)
        print("-" * 60)

if __name__ == "__main__":
    main()
