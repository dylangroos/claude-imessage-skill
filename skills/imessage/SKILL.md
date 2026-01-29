---
name: imessage
description: This skill should be used when the user asks to "read messages", "send an iMessage", "check iMessage", "text someone", "reply to a message", mentions "Messages app", or discusses iMessage conversations and texting.
version: 1.0.0
---

# iMessage Integration Skill

Access and control iMessages directly from Claude Code. Read conversations, send messages, and interact with your Messages.app on macOS.

## Overview

This skill provides three main capabilities:
1. **Read Messages** - Query the iMessage database to read conversations
2. **Send Messages** - Send iMessages via AppleScript
3. **Monitor Messages** - Watch for new messages in real-time

## Prerequisites

- macOS with Messages.app
- Full Disk Access permission for Terminal/IDE
- iMessage must be set up and signed in

## Reading Messages

### Get Recent Messages

Use the Bash tool to query the iMessage database:

```bash
sqlite3 ~/Library/Messages/chat.db "
SELECT
    datetime(date/1000000000 + 978307200, 'unixepoch', 'localtime') as time,
    h.id as sender,
    CASE
        WHEN m.text IS NOT NULL THEN m.text
        ELSE '[attachment]'
    END as message
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.is_from_me = 0
ORDER BY m.date DESC
LIMIT 10
"
```

### Search for Messages from a Specific Person

```bash
sqlite3 ~/Library/Messages/chat.db "
SELECT
    datetime(date/1000000000 + 978307200, 'unixepoch', 'localtime') as time,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE h.id LIKE '%PHONE_OR_EMAIL%'
  AND m.text IS NOT NULL
ORDER BY m.date DESC
LIMIT 20
"
```

Replace `PHONE_OR_EMAIL` with the person's phone number or iCloud email.

### Get Unread Message Count

```bash
sqlite3 ~/Library/Messages/chat.db "
SELECT COUNT(*) as unread
FROM message
WHERE is_read = 0 AND is_from_me = 0
"
```

## Sending Messages

### Send via AppleScript

Use AppleScript to send messages through Messages.app:

```bash
osascript -e 'tell application "Messages"
    set targetBuddy to buddy "RECIPIENT" of (first service whose service type = iMessage)
    send "MESSAGE_TEXT" to targetBuddy
end tell'
```

Replace:
- `RECIPIENT` with phone number (+1234567890) or iCloud email
- `MESSAGE_TEXT` with your message

### Alternative Send Method

For better reliability with various recipient formats:

```bash
osascript -e 'tell application "Messages"
    send "MESSAGE_TEXT" to participant "RECIPIENT" of (first account whose service type is iMessage)
end tell'
```

## Monitoring for New Messages

### One-time Check

```bash
# Get the latest ROWID
latest=$(sqlite3 ~/Library/Messages/chat.db "SELECT MAX(ROWID) FROM message")

# After some time, check for new messages
sqlite3 ~/Library/Messages/chat.db "
SELECT
    datetime(date/1000000000 + 978307200, 'unixepoch', 'localtime') as time,
    h.id as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.ROWID > $latest
  AND m.is_from_me = 0
ORDER BY m.ROWID
"
```

### Continuous Monitoring

For continuous monitoring, use the Python script included in this plugin:

```bash
python3 ~/.claude/plugins/imessage/scripts/monitor.py
```

## Important Notes

### Database Path
The iMessage database is located at:
```
~/Library/Messages/chat.db
```

### Timestamps
iMessage stores timestamps as nanoseconds since 2001-01-01. Convert to readable format:
```
datetime(date/1000000000 + 978307200, 'unixepoch', 'localtime')
```

### AttributedBody
In macOS Ventura+, some messages store text in the `attributedBody` BLOB instead of the `text` column. If `text` is NULL, the message content is in the binary blob and requires parsing.

### Permissions
Reading the database requires **Full Disk Access**:
1. Open System Settings > Privacy & Security > Full Disk Access
2. Add Terminal.app (or your IDE)
3. Restart the application

Sending messages requires **Automation** permission for Messages.app.

## Common Queries

### Get All Conversations

```bash
sqlite3 ~/Library/Messages/chat.db "
SELECT DISTINCT h.id as contact, COUNT(*) as message_count
FROM message m
JOIN handle h ON m.handle_id = h.ROWID
GROUP BY h.id
ORDER BY message_count DESC
LIMIT 20
"
```

### Get Messages from Last Hour

```bash
sqlite3 ~/Library/Messages/chat.db "
SELECT
    datetime(date/1000000000 + 978307200, 'unixepoch', 'localtime') as time,
    h.id as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.date > (strftime('%s', 'now') - strftime('%s', '2001-01-01')) * 1000000000 - 3600 * 1000000000
  AND m.text IS NOT NULL
ORDER BY m.date DESC
"
```

## Example Workflows

### Check and Respond Workflow

1. **Read recent messages**:
   ```bash
   sqlite3 ~/Library/Messages/chat.db "SELECT ..." # Use query above
   ```

2. **Send a reply**:
   ```bash
   osascript -e 'tell application "Messages" ...'
   ```

### Auto-Reply Bot

Use the monitoring script to watch for messages and auto-respond based on content.

## Troubleshooting

### "unable to open database" Error
- Grant Full Disk Access to your terminal/IDE
- Check that Messages.app is set up

### Message Not Sending
- Verify recipient format (+1234567890 or email@icloud.com)
- Ensure Messages.app is running
- Check Automation permissions

### Empty Results
- Messages might be in attributedBody BLOB (requires parsing)
- Check that iMessage is signed in and synced

## See Also

- [Apple Messages AppleScript Reference](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
