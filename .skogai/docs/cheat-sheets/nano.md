# nano Editor Cheat Sheet

nano is the editor that opens when you type nano file.conf over SSH, and on Debian and Ubuntu it is what crontab -e, visudo, and git hand you by default. This sheet covers the shortcuts people look up: saving and exiting, cut and paste, search and replace, undo, and the nanorc settings worth turning on.

## Save and Exit

^X means Ctrl+X, and case does not matter. These keys are the reason most people open this page.

| Keybinding | Action |
|---|---|
| `Ctrl+O` | WriteOut: save current buffer to file |
| `Ctrl+X` | Exit Nano (prompts to save modified buffer) |
| `Ctrl+C` | Cancel current prompt or operation |

## Shortcut Notation

The two lines at the bottom of the screen use the same notation as this page.

| Prefix | Meaning |
|---|---|
| `^` | Control key (e.g. `^O` means `Ctrl+O`) |
| `M-` | Meta key: `Alt` on Linux/Windows, `Option` or `Esc` on macOS |

## Cut, Copy and Paste

nano keeps its own cutbuffer. It is not the system clipboard, and over SSH it lives on the server.

| Keybinding | Action |
|---|---|
| `Ctrl+K` | Cut (kill) current line into cutbuffer |
| `Alt+6` or `M-6` | Copy current line or marked selection into cutbuffer |
| `Ctrl+U` | Paste (uncut) contents of cutbuffer at cursor |

## Delete

| Keybinding | Action |
|---|---|
| `Ctrl+D` | Delete character under cursor |
| `Ctrl+H` / `Backspace` | Delete character before cursor |
| `Ctrl+K` | Delete entire line |

## Select Text

nano calls a selection the mark.

| Keybinding | Action |
|---|---|
| `Alt+A` or `M-A` | Toggle selection mark start/stop |
| Arrow Keys | Expand selection while mark is set |
| `Ctrl+K` | Cut selected text |
| `Alt+6` | Copy selected text |

## Search

| Keybinding | Action |
|---|---|
| `Ctrl+W` | Where Is: search for string |
| `Alt+W` | Search next occurrence of previous search string |
| `Ctrl+C` | Cancel search dialog |

Searches wrap around the end of the file, and the status bar says so when they do.

## Search and Replace

| Keybinding | Action |
|---|---|
| `Alt+R` or `Ctrl+\` | Where Is and Replace: search and substitute text |
| `Y` / `N` | Confirm / skip individual replacement |
| `A` | Replace all remaining matches without prompt |

The pattern syntax is the POSIX set, the same one [grep](https://sshworkbench.com/cheatsheets/grep) uses. For the same edit across many files, [sed](https://sshworkbench.com/cheatsheets/sed) is faster than opening each one.

## Undo and Redo

| Keybinding | Action |
|---|---|
| `Alt+U` | Undo last text action |
| `Alt+E` | Redo last undone action |

Undo is on by default in current nano; builds older than 4.0 needed set undo in the nanorc. The history is per open file and goes away when you exit, so undo cannot rescue a file you already saved and closed. set backup keeps the previous version for that.

## Move Around

| Keybinding | Action |
|---|---|
| `Ctrl+A` / `Ctrl+E` | Move cursor to beginning / end of line |
| `Ctrl+Y` / `Ctrl+V` | Page up / page down |
| `Ctrl+P` / `Ctrl+N` | Move to previous / next line |
| `Alt+\` / `Alt+/` | Jump to beginning / end of file |

M-< and M-> switched to horizontal scrolling in nano 9.0. Use M-, and M-. to move between buffers.

## Line Numbers

| Keybinding | Action |
|---|---|
| `Alt+N` | Toggle line numbers on/off |
| `Ctrl+C` | Display current line number, column, and character position |
| `Ctrl+_` or `Alt+G` | Go to line and column number |

## Insert and Save Files

| Keybinding | Action |
|---|---|
| `Ctrl+R` | Read file and insert its content at cursor |
| `Ctrl+O` | Save current buffer (allows specifying alternate filename) |

## Command Line Options

| Flag | Meaning |
|---|---|
| `nano -l file` | Open file with line numbers displayed (`--linenumbers`) |
| `nano -m file` | Enable mouse support (`--mouse`) |
| `nano -v file` | View only (read-only mode, disables editing) |
| `nano -c file` | Constantly show cursor position in status bar |
| `nano -B file` | Create backup file with `~` suffix when saving |

## nanorc Config

Your settings go in ~/.nanorc, the machine-wide ones in /etc/nanorc.

| Directive | What it does |
|---|---|
| `set linenumbers` | Always display line numbers |
| `set tabsize 4` | Set tab display width to 4 columns |
| `set tabstospaces` | Convert typed tabs to spaces |
| `set mouse` | Enable mouse clicking to position cursor |
| `include /usr/share/nano/*.nanorc` | Enable syntax highlighting for programming languages |

A starter file:

```
set linenumbers
set constantshow
set tabsize 4
set tabstospaces
set softwrap
set historylog
set positionlog
set backup
include /usr/share/nano/*.nanorc
```

Settings take effect the next time nano starts. A syntax error in the file stops nano at launch with the offending line number, so check it before you rely on the machine.

## Default Editor

What opens for crontab -e, visudo, and git commit is set outside nano.

| Command | What it does |
|---|---|
| `export EDITOR=nano` | Set Nano as default editor in current shell (`~/.bashrc`) |
| `export VISUAL=nano` | Set Nano for visual editor invocations |
| `sudo update-alternatives --config editor` | Set system-wide default editor on Debian/Ubuntu |

## Mac Keyboard

Ctrl shortcuts work as printed. Only the Meta (Alt) ones need setting up.

| Key | macOS Equivalent |
|---|---|
| `Ctrl` | Control key (`^`) |
| `Alt` / `Meta` | `Option` (must enable "Use Option as Meta Key" in Terminal preferences) |
| `Esc` prefix | Press `Esc`, release, then press key (alternative to `Meta`) |

Over [SSH](https://sshworkbench.com/cheatsheets/ssh) you are running the server's nano, so the pico substitution never bites you there. The Option key setting does.

## nano vs Vim

| Feature | Nano | Vim |
|---|---|---|
| Learning Curve | Very gentle; menu shown on screen | Steep; requires learning modal editing |
| Modes | Modeless (typing always inserts text) | Modal (Normal, Insert, Visual, Command) |
| System Presence | Common default on Ubuntu and Debian | Standard on almost every Unix/Linux server |
| Extensibility | Basic syntax highlighting and keybinds | Extensive plugins, LSP, scripting, macros |

Learning both pays off, because the box that has one often lacks the other. The [Vim cheat sheet](https://sshworkbench.com/cheatsheets/vim) covers the other half.

## Gotchas

- ^X leaves straight away when nothing changed. If it asks "Save modified buffer?", something did change, even if it was one stray keystroke. Y saves, N discards, ^C goes back.
- The cutbuffer is not your system clipboard. ^K on the server then Cmd+V on your laptop pastes whatever the laptop had, not the line you cut.
- Pasted YAML or Python that comes out stair-stepped means auto-indent is on. M-I turns it off, then paste again.
- Editing a root-owned file without sudo only fails at the end, when the write is refused. Save elsewhere with ^O and move it, or reopen with sudoedit.
- ^S saves in current nano. If the terminal freezes instead, it took ^S as flow control: press ^Q to unfreeze. nano -p hands both keys back to the terminal on purpose.
- ^Z does not suspend by default. It prints a hint pointing at ^T ^Z, which does; fg brings nano back. bind ^Z suspend main in your nanorc restores the shell habit.
- nano -w on a config file is still worth typing. Hard wrapping is off by default now, but /etc/nanorc on an older box can have it on, and a wrapped line in nginx or sshd config breaks the service.

## nano FAQ

### How do I save and exit nano?

Press Ctrl+O to write the file, Enter to accept the filename it offers, then Ctrl+X to leave. Ctrl+S saves without the filename prompt, so Ctrl+S then Ctrl+X does the whole job. If you press Ctrl+X with unsaved changes, nano asks "Save modified buffer?": Y then Enter saves, N quits and throws the changes away, and Ctrl+C cancels and puts you back in the file. One catch on server configs: if you opened a root-owned file without sudo, nothing fails until the write, and then it says Permission denied. Save a copy somewhere you can write (Ctrl+O, then type /tmp/myfile) and move it with sudo, or quit and reopen with sudoedit.

### How do I copy and paste in nano?

Ctrl+K cuts the current line and Ctrl+U pastes it back; press Ctrl+K several times in a row and the lines pile into one buffer that Ctrl+U pastes together. To copy without removing, use Alt+6. To work on a block, set the mark with Ctrl+6 (or Alt+A), move to the other end, then Ctrl+K to cut it or Alt+6 to copy it. That cutbuffer belongs to nano and is not your system clipboard, which matters over SSH: text you cut in nano lives on the server. To get it onto your own machine, select it with the mouse in your terminal instead (hold Shift if nano has mouse mode on). Pasting the other way is a normal terminal paste, but if the result comes out stair-stepped, auto-indent is on: press Alt+I to turn it off and paste again.

### How do I select all text in nano and delete it?

Alt+\\ goes to the top of the file, Ctrl+6 sets the mark, Alt+/ goes to the end, and Ctrl+K cuts everything in between (Alt+6 copies it instead). If you only want the file empty, skip the marking: Alt+\\ to the top, then Alt+T cuts from the cursor to the end of the buffer in one keystroke. For a single line, Alt+Del deletes it without disturbing the cutbuffer. Alt+U undoes any of it if you cut more than you meant to, and nothing touches the file on disk until you save.

### Why do the Alt (M-) shortcuts not work in nano on a Mac?

macOS terminals do not send Option as Meta by default. In Terminal.app turn on Settings > Profiles > Keyboard > "Use Option as Meta Key"; in iTerm2 set Profiles > Keys > Left Option key to Esc+. You can also skip the setting entirely: press Esc, release it, then the letter, so Esc U is Alt+U (undo) and Esc G is Alt+G (go to line). Ctrl shortcuts need no setup. One more Mac quirk, for local files only: /usr/bin/nano on recent macOS is a symlink to pico (UW PICO 5.09), not GNU nano, so undo and line numbers are missing. Run brew install nano if you want the real thing locally. Over SSH you are using the server's nano, so only the Option key setting matters.

### How do I make nano the default editor?

Add export EDITOR=nano and export VISUAL=nano to ~/.bashrc or ~/.zshrc for anything that reads the environment. Git has its own setting: git config --global core.editor nano. On Debian and Ubuntu, sudo update-alternatives --config editor sets the system-wide choice that visudo and crontab -e follow. For one command, put it on the line: EDITOR=nano visudo. Note that sudo clears the environment, so sudo crontab -e uses root's editor, not yours; sudo EDITOR=nano crontab -e fixes that. kubectl reads KUBE_EDITOR.

---
Source: https://sshworkbench.com/cheatsheets/nano
