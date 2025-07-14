import asyncio
import os
import json
from telegram import Bot

# 🆕 New imports
import feedparser
from datetime import datetime, timezone
from telegram import Update
from telegram.constants import ChatType

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# Global variables to hold settings
feeds = {}
last_scan = "1970-01-01T00:00:00+00:00"


async def send_init_pinned_message():
    bot = Bot(token=TELEGRAM_API_KEY)
    msg = await bot.send_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        text=json.dumps({
            "feeds": {
                "220Triathlon": "https://www.220triathlon.com/feed/atom"
            },
            "last_scan": "1970-01-01T00:00:00+00:00"
        }, indent=2),
        parse_mode="HTML"
    )
    # Pin the message silently
    await bot.pin_chat_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        message_id=msg.message_id,
        disable_notification=True
    )
    return msg.message_id

async def read_settings():
    global feeds, last_scan
    bot = Bot(token=TELEGRAM_API_KEY)
    chat = await bot.get_chat(TELEGRAM_CHANNEL_ID)
    pinned = chat.pinned_message
    if not pinned:
        raise RuntimeError("No pinned message found")
    try:
        data = json.loads(pinned.text)
    except json.JSONDecodeError as e:
        raise ValueError("Pinned message JSON invalid") from e
    feeds = data.get("feeds", {})
    last_scan = data.get("last_scan", "1970-01-01T00:00:00+00:00")


async def save_settings():
    global feeds, last_scan
    bot = Bot(token=TELEGRAM_API_KEY)
    chat = await bot.get_chat(TELEGRAM_CHANNEL_ID)
    pinned = chat.pinned_message
    if not pinned:
        raise RuntimeError("No pinned message found")

    # Read previous data for comparison
    try:
        prev_data = json.loads(pinned.text)
    except json.JSONDecodeError:
        prev_data = {}

    prev_feeds = prev_data.get("feeds", {})
    prev_last_scan = prev_data.get("last_scan", "1970-01-01T00:00:00+00:00")

    print("🔁 Saving updated settings:")
    print(f"  Feeds: unchanged" if prev_feeds == feeds else f"  Feeds changed from:\n    {json.dumps(prev_feeds, indent=4)}\n  to:\n    {json.dumps(feeds, indent=4)}")
    print(f"  Last scan changed from: {prev_last_scan}")
    print(f"                      to: {last_scan}")

    if prev_feeds == feeds and prev_last_scan == last_scan:
        return

    # Save new data
    data = {
        "feeds": feeds,
        "last_scan": last_scan
    }
    text = json.dumps(data, indent=2)
    await bot.edit_message_text(
        chat_id=TELEGRAM_CHANNEL_ID,
        message_id=pinned.message_id,
        text=text,
        parse_mode="HTML"
    )
    await bot.pin_chat_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        message_id=pinned.message_id,
        disable_notification=True
    )

async def fetch_and_send_rss_entries():
    global last_scan, feeds
    bot = Bot(token=TELEGRAM_API_KEY)

    last_scan_dt = datetime.fromisoformat(last_scan.replace("Z", "+00:00"))

    feed_counter = 0
    for source_title, url in feeds.items():
        feed_counter += 1
        print(f"\n🔗 {source_title}: {url}")
        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"⚠️  Failed to parse feed: {feed.bozo_exception}")
            continue

        print(f"Parsing feed {feed_counter} / {len(feeds.items())}: {len(feed.entries)} items.")
        await asyncio.sleep(1)

        old_news_count = 0

        for entry in feed.entries:
            title = entry.get("title", "(no title)")
            link = entry.get("link", "")
            summary = entry.get("summary", "").strip()

            # Try to extract publish date
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if not published:
                continue
            published_dt = datetime(*published[:6], tzinfo=timezone.utc)

            if published_dt <= last_scan_dt:
                old_news_count += 1
                continue

            # Extract first paragraph from summary
            # first_paragraph = summary.split("\n\n")[0].split("</p>")[0]
            # if '<' in first_paragraph:
            #     from html import unescape
            #     import re
            #     first_paragraph = re.sub('<[^<]+?>', '', first_paragraph)
            #     first_paragraph = unescape(first_paragraph).strip()

            message = (
                f"<b>{title}</b>\n"
                f"<a href=\"{link}\">Read more</a>"
            )

            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=False
            )

            print(f"✅ Sent: {title}")
            await asyncio.sleep(1)  # <-- prevents hitting Telegram or network timeouts

        print(f"Skipped: {old_news_count}")

async def main():
    global last_scan
    await read_settings()
    print(f"Last scanned: {last_scan}")

    print("✅ Loaded RSS feeds from pinned message:")
    for title, url in feeds.items():
        print(f"- {title}: {url}")

    await fetch_and_send_rss_entries()

    last_scan = datetime.now(timezone.utc).isoformat(timespec="seconds")

    await save_settings()


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(send_init_pinned_message())
