# Text Monkey 1.0.0

Text Monkey is a Python Tkinter text editor built to demonstrate core Operating System concepts through a desktop application. It includes file handling, memory buffering, logging, threading, autosave recovery, version snapshots, compression, plugin loading, and a built-in Python runner.

## Key Highlights

1. File management with open, save, rename, and delete
2. Threaded file opening/saving to prevent UI freezing
3. 5-file memory buffer with FIFO eviction
4. Timestamped system logging in `log.txt`
5. Autosave and session recovery
6. Version snapshots with restore option
7. ZIP compression with in-memory text optimization
8. Dynamic plugin system using the `plugins/` folder
9. Python code runner with output, errors, and timeout protection
10. Multi-tab editor with sidebar explorer
11. Search, analytics, and formatting toolbar
12. Pink pixel-style UI with custom Text Monkey icon

## Keyboard Shortcuts

| Shortcut   | Action          |
| `Ctrl + S` | Save file       |
| `Ctrl + Z` | Undo            |
| `Ctrl + Y` | Redo            |
| `Ctrl + F` | Search          |
| `Ctrl + C` | Copy            |
| `Ctrl + V` | Paste           |
| `Ctrl + X` | Cut             |
| `Ctrl + A` | Select all      |
| `Ctrl + B` | Bold            |
| `Ctrl + I` | Italic          |
| `Ctrl + U` | Underline       |


## Features

### File and Editor Tools

- Open, save, rename, and delete files
- Multi-tab editing with close/switch support
- Sidebar file explorer with folder navigation
- Copy, paste, cut, select all, undo, and redo
- Search bar with highlighted matches
- Formatting toolbar for font, size, color, bold, italic, and underline

### Memory, Logging, and Recovery

- Stores recently opened files in a dictionary buffer
- Limits memory buffer to 5 files
- Uses FIFO eviction when the buffer is full
- Logs major actions with timestamps in `log.txt`
- Autosaves editor content
- Prompts to restore unsaved work after restart

### Versioning and Compression

- Saves file snapshots in `.versions`
- Restores previous file versions
- Optimizes text in memory before compression
- Creates `_compressed.zip` archives
- Avoids extraction name collisions using `_compressed` file names

### Python Runner

- Runs Python code directly from the editor
- Displays output in a separate window
- Shows errors and tracebacks
- Stops long-running code after a timeout

### Plugin System

- Loads external Python plugins from `plugins/`
- Supports plugin reload without editing core app code
- Includes plugins for:
  - Insert Date/Time
  - Insert TODO List
  - Check Grammar (Beta)
  - Clear Grammar Marks

### UI and Analytics

- Pink pixel-style custom theme
- Dark mode support
- Status bar showing word count, character count, line count, file name, and cursor position

## Operating System Concepts Used

| OS Concept        | Project Usage |
| File Management   | Open, save, rename, delete, browse files |
| Thread Management | Background file open/save operations |
| Memory Management | Dictionary-based 5-file buffer |
| FIFO Replacement  | Oldest cached file removed first |
| System Logging    | Timestamped `log.txt` action records |
| Recovery System   | Autosave file and restore prompt |
| Storage Management| ZIP compression and text optimization |
| Version Control   | File snapshots and restore system |
| Process Management| Python runner uses `subprocess` |
| Dynamic Loading   | Plugins loaded with `importlib` |


## Technologies Used

- Python
- Tkinter / ttk
- `os`
- `threading`
- `zipfile`
- `subprocess`
- `tempfile`
- `importlib`
- `pathlib`
- `datetime`
- `language_tool_python` optional for Grammar Checker Beta

## Notes

- Grammar Checker is marked **Beta** because LanguageTool depends on local package/Java setup and may need further improvement.
- Very small files may become larger after ZIP compression due to archive metadata overhead.

## How to Run

Run the main application file:
 
python main.py

## UI

![Text Monkey Screenshot](images/Screenshot%202026-05-05%20142057.png)
