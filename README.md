# Claude iMessage Skill

A Claude Code skill for reading and sending iMessages directly from your Claude sessions.

## Features

- `/imessage read` - Read recent iMessages
- `/imessage send <recipient> <message>` - Send an iMessage
- `/imessage monitor` - Monitor for new messages and auto-respond

## Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/dylangroos/claude-imessage-skill.git
   ```

2. Link to Claude plugins:
   ```bash
   ln -s ~/claude-imessage-skill ~/.claude/plugins/imessage
   ```

3. Grant Full Disk Access to Terminal:
   - System Settings > Privacy & Security > Full Disk Access
   - Add Terminal.app (or your IDE)

## Requirements

- macOS with Messages.app
- Full Disk Access permission
- Claude Code CLI

## Usage

### Read recent messages
```
/imessage read
```

### Send a message
```
/imessage send +16158819950 "Hello from Claude!"
```

### Start monitoring (auto-respond mode)
```
/imessage monitor
```

## How it works

- Reads from `~/Library/Messages/chat.db` (SQLite)
- Sends via AppleScript automation
- Uses Claude to generate intelligent responses

## License

MIT
