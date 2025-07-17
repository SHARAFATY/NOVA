# NOVA: Local Linux AI Assistant

NOVA is a fully local, modular, sci-fi-inspired AI assistant for Linux. She controls, automates, and monitors your system with voice or keyboard activation, a glowing glass UI, and evolving intelligence.

## Features
- Voice and hotkey activation
- Floating, transparent PyQt6 UI
- Modular tool system for system, network, files, users, and more
- Persistent memory and logs
- Self-evolving brain module
- Fully offline, privacy-first

## Installation
1. Clone this repo
2. `cd nova`
3. Install dependencies: `pip install -r requirements.txt`

## Usage
- Run with: `python nova/main.py`
- Activate with Ctrl+; or say "Nova" (if mic enabled)
- Type or speak commands (e.g., "restart network", "clean junk files")

## Extending
- Drop new tools in `nova/tools/custom/` — NOVA will auto-detect them

## Security
- Destructive actions require confirmation
- Memory and logs are local and can be encrypted

---

*Build as if she's a living entity. NOVA is your subtle, smart, fast Linux guide.* 