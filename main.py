import os

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def main():
    print("Telegram RSS Bot starting...")
    print(f"Using channel: {TELEGRAM_CHANNEL_ID}")

if __name__ == "__main__":
    main()