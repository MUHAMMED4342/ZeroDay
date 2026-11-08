# ZERO DAY

An audio hacking game for blind and low-vision players. You scan a corporate network, exploit old software, crack tone locks, tune frequency locks, dodge firewalls while you download the target file, and try to stay under the trace. Everything is played with sound and text. Sounds are placed in your left and right ear, so wear headphones.

## Quick start

    pip install wxPython pygame
    python gui.py            # window with terminal, notes, history, mission and translation editors
    python game.py           # plain terminal version (no extra window)

Optional: `pip install accessible-output2` makes the window speak through your screen reader.
Type `help` in the game for all commands. A good first move is `scan`.

## Build the game folder (Windows)

1. Install Python 3.11 or 3.12 from python.org and tick "Add Python to PATH".
2. Double-click `build.bat`. The first run downloads the tools and takes a few minutes.
3. The game is the folder `dist\ZeroDay`. It holds `ZeroDay.exe`, PyInstaller's `_internal` folder and real `lang`, `missions` and `sounds` folders, plus `README.txt` and `LICENSE.txt`. Copy or zip the whole folder.

The build uses PyInstaller's folder mode (`--onedir`) on purpose. Nothing is packed inside the exe, so the language files and missions players edit are the only copies, and nothing gets mixed up with a hidden packed copy.

Add an `icon.ico` next to `build.bat` before building for a custom icon. Building again replaces `dist\ZeroDay`, so keep your own edits in the `lang`, `missions` and `sounds` folders next to `build.bat`.

Do not put the game folder in a protected place such as Program Files, because the editors must be able to write there.

## The window

- Tabs: **Terminal** (Ctrl+1), **Notes** (Ctrl+2, saved automatically), **History** (Ctrl+3, every message from every session, with search). Ctrl+L returns to the command box.
- During the tone lock, frequency lock and firewall minigames, single keys go straight to the game. Left and right arrows work as A and D.
- Notes and history are stored in `~/.zeroday/` (your user folder).

## Mission editor (Tools menu, Ctrl+M)

Missions are data files in `missions/*.json` (servers, services, locks, files, story, per-language text). The editor writes them and checks that the target file can be reached. The game lists all missions at the start and asks which one to play. Built in: `training_lab`, `open_doors`, `ransom_clock`, `lost_signal`, `clean_water`, `city_archive` and `zero_day` (the `order` field sets the list order). The editor has a step-by-step **Translate this mission** dialog, so nobody has to edit JSON by hand.


## Translation editor (Tools menu, Ctrl+T)

One step-by-step dialog translates everything: `lang/<code>.json` (219 texts), and the texts of every mission. It starts at the first untranslated text, checks `{placeholders}`, and writes only what was translated: the language file, plus the changed `missions/*.json` next to the program. A broken placeholder can no longer crash the game (the English text is used). `language.txt` next to the program forces a language. Built-in `lang_text` missions (Zero Day) only translate their name there; the rest comes from the language file.

## Languages

The language follows the device language automatically. Force one with `--lang tr`. To translate, copy `lang/en.json` to `lang/<code>.json` and translate the values only; keep the keys and `{placeholders}`. Missing keys fall back to English. Command words you add under `cmd` work next to the English ones.

## Sounds

Without sound files the game generates all sounds itself. To use your own, add files named as listed in `SOUNDS.md` (ogg, mp3 or wav). Prefer CC0 sounds so the game stays free to share.

## License

The code is released into the public domain under the Unlicense (see `LICENSE`): anyone may use, change, sell or share it. Sound files you add keep their own licenses.
