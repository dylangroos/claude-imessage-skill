#!/usr/bin/env python3
"""
Simple iMessage monitor script.
Watches for new messages and prints them to stdout.
"""

import os
import sqlite3
import time
from datetime import datetime

DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")
POLL_INTERVAL = 2.0  # seconds
APPLE_EPOCH = 978307200  # Seconds between Unix epoch and Apple epoch (2001-01-01)


def get_latest_rowid():
    """Get the most recent message ROWID."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(ROWID) FROM message")
    result = cursor.fetchone()[0] or 0
    conn.close()
    return result


def convert_timestamp(apple_timestamp):
    """Convert Apple timestamp to datetime."""
    if apple_timestamp == 0:
        return datetime.now()
    unix_timestamp = (apple_timestamp / 1_000_000_000) + APPLE_EPOCH
    return datetime.fromtimestamp(unix_timestamp)


def get_new_messages(last_rowid):
    """Fetch messages newer than last_rowid."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            m.ROWID,
            m.text,
            m.date,
            m.is_from_me,
            h.id as sender
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        WHERE m.ROWID > ?
        ORDER BY m.ROWID ASC
        """,
        (last_rowid,),
    )

    messages = []
    for row in cursor.fetchall():
        rowid, text, date, is_from_me, sender = row
        if text:  # Skip messages without text (attachments, etc.)
            messages.append({
                "rowid": rowid,
                "text": text,
                "timestamp": convert_timestamp(date),
                "from_me": bool(is_from_me),
                "sender": sender or "unknown",
            })

    conn.close()
    return messages


def main():
    """Main monitoring loop."""
    print("iMessage Monitor Started")
    print(f"Watching: {DB_PATH}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print("-" * 50)

    last_rowid = get_latest_rowid()
    print(f"Starting from ROWID: {last_rowid}\n")

    try:
        while True:
            messages = get_new_messages(last_rowid)

            for msg in messages:
                direction = "→ OUT" if msg["from_me"] else "← IN"
                print(f"[{msg['timestamp'].strftime('%H:%M:%S')}] {direction}")
                print(f"From: {msg['sender']}")
                print(f"Text: {msg['text'][:100]}...")
                print("-" * 50)

                last_rowid = max(last_rowid, msg["rowid"])

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitor stopped")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Error: iMessage database not found at {DB_PATH}")
        print("Make sure Messages.app is set up on this Mac.")
        exit(1)

    main()
