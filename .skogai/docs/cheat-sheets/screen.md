# screen Command Linux Cheat Sheet

GNU screen keeps a shell running on the server after you disconnect: detach, log off, and reattach later with everything still going. This sheet covers the session commands, the Ctrl+a shortcuts, copy mode, background jobs, serial ports, and how screen maps to tmux.

Last updated September 11, 2026

On this page

- [Detach and Reattach](#detach-and-reattach)
- [Sessions](#sessions)
- [Run in the Background](#run-in-the-background)
- [Kill a Session](#kill-a-session)
- [Scrolling and Copy Mode](#scrolling-and-copy-mode)
- [Windows](#windows)
- [Split Screen](#split-screen)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Serial Ports](#serial-ports)
- [Logging](#logging)
- [Install](#install)
- [PuTTY and WSL](#putty-and-wsl)
- [screen vs tmux](#screen-vs-tmux)
- [Gotchas](#gotchas)

## Detach and Reattach

Ctrl+a is screen's command key: press Ctrl+a, release, then the letter. Detaching leaves everything running; exit is what actually ends things.

| Command | What it does |
|----|----|
| Ctrl+a d | Detach, leaving the session and its jobs running |
| Ctrl+a D D | Detach and log out of the shell that started screen |
| screen -r | Reattach to the detached session |
| screen -r deploy | Reattach to a session by name (or PID) |
| screen -rd | Detach it from wherever it is attached, then reattach here |
| screen -x | Attach without detaching anyone; both of you see the same screen |
| screen -RR | Reattach to the first session found, creating one if none exist |
| screen -d 12345 | Detach a session from outside it |
| exit | Close the current window; closing the last one ends the session |

A dropped SSH connection detaches you automatically, so a long job inside screen survives it; screen -rd gets you back in. To stop the drops themselves, see [ssh broken pipe](https://sshworkbench.com/fix/ssh-broken-pipe).

## Sessions

| Command | What it does |
|----|----|
| screen | Start a new session |
| screen -S deploy | Start a session named deploy, which beats PIDs for reattaching |
| screen -ls | List sessions and whether each is Attached or Detached |
| screen -dmS backup ./backup.sh | Start a detached session running a command (scripts, cron) |
| screen -S deploy -X stuff \$'ls\n' | Type a command into a session from outside |
| Ctrl+a :sessionname newname | Rename the current session |
| screen -wipe | Remove sessions marked Dead from the list |

## Run in the Background

-d -m (or -dmS with a name) starts a session already detached, which is how scripts, cron jobs, and game servers get a shell that outlives the login.

| Command | What it does |
|----|----|
| screen -dmS backup ./backup.sh | Run a script in a detached session named backup |
| screen -dmS api bash -c './server; exec bash' | Keep the window open after the command exits, so you can read the error |
| screen -L -dmS build make all | Same, logging output to screenlog.0 |
| screen -S api -X screen ./worker.sh | Open another window running a command in a session that already exists |
| screen -S api -X stuff \$'restart\n' | Send a line to the session as if you typed it |
| screen -S mc -p 0 -X stuff \$'stop\n' | Send it to window 0 specifically (how people stop a Minecraft server) |
| screen -ls \| grep backup | Check whether the background session is still alive |

A detached session is owned by your login, so it dies with a reboot and with an aggressive systemd user-session cleanup. Anything that must come back on its own belongs in a service unit rather than screen.

## Kill a Session

| Command | What it does |
|----|----|
| Ctrl+a k | Kill the current window (asks first) |
| Ctrl+a \\ | Kill every window and end the session (asks first) |
| screen -S deploy -X quit | Kill a session from outside, without attaching |
| exit | Close windows one at a time; the session ends with the last one |

Kill every detached session at once:

```
screen -ls | grep Detached | cut -d. -f1 | xargs -r kill
```

Copy

## Scrolling and Copy Mode

PgUp and the mouse wheel talk to your terminal, not to screen. Scrolling back happens in copy mode.

[TABLE]

The default buffer is only 100 lines. Put defscrollback 10000 in ~/.screenrc so every window starts with real history.

## Windows

Windows are full-screen tabs inside one session.

[TABLE]

## Split Screen

A new region starts empty: move into it with Ctrl+a Tab, then open a window in it.

[TABLE]

## Keyboard Shortcuts

The rest of the Ctrl+a keys worth knowing.

| Key       | Action                                                |
|-----------|-------------------------------------------------------|
| Ctrl+a ?  | List every keybinding                                 |
| Ctrl+a a  | Send a literal Ctrl+a through (start of line in bash) |
| Ctrl+a :  | Command prompt for screen's own commands              |
| Ctrl+a x  | Lock the session behind your password                 |
| Ctrl+a H  | Start or stop logging the window                      |
| Ctrl+a h  | Write a snapshot of the visible window to hardcopy.0  |
| Ctrl+a \* | List the displays attached to this session            |

## Serial Ports

screen doubles as a serial terminal, which is the main thing it does that tmux does not. Settings default to 8N1; give the baud rate after the device.

[TABLE]

Detaching with Ctrl+a d keeps the port locked, so end serial sessions with Ctrl+a k. Permission denied on the device means your user is not in the right group: sudo usermod -aG dialout \$USER, then log in again.

## Logging

[TABLE]

## Install

"screen: command not found" means the package is missing, which is normal on minimal images and containers.

[TABLE]

macOS still has /usr/bin/screen at version 4.00.03, which is missing -Logfile and a lot of the copy-mode keys. Homebrew's build lands in PATH ahead of it.

## PuTTY and WSL

Windows has no screen of its own. You either run it on the Linux box you connect to, or run it locally under WSL.

[TABLE]

PuTTY has its own serial mode, so on Windows you pick a COM port there instead of screen /dev/ttyUSB0. The [PuTTY cheat sheet](https://sshworkbench.com/cheatsheets/putty) covers the Windows side.

## screen vs tmux

The keys map almost one to one, so switching either way is cheap. tmux has better splits, a status bar, and active development; screen is preinstalled more often and handles serial ports. The [tmux cheat sheet](https://sshworkbench.com/cheatsheets/tmux) covers the other side in full.

[TABLE]

## Gotchas

- Detach is not exit.
  Ctrl+a d
  keeps everything running;
  exit
  closes the window, and the last window takes the session with it ("\[screen is terminating\]").
- The scrollback buffer defaults to 100 lines. Add
  defscrollback 10000
  to
  ~/.screenrc
  before you need it, not after.
- screen eats Ctrl+a, which bash uses for start of line. Press
  Ctrl+a a
  to send it through, or move the command key with
  escape ^Jj
  in
  ~/.screenrc
  .
- "There is no screen to be resumed" while
  screen -ls
  shows a session Attached means a dead client is holding it.
  screen -rd
  takes it over.
- screen inside screen (a session on the far end of an SSH window):
  Ctrl+a a d
  detaches the inner one,
  Ctrl+a d
  the outer.
- Sessions do not survive a reboot. screen protects you from disconnects, not from restarts; anything that must outlive a reboot belongs in a systemd service.

### Tired of typing all of this?

SSH Workbench turns your servers into a dashboard over plain SSH: files, services, Docker, logs, and cron with a click, and a real terminal when you want one.

[Try free for 7 days](https://sshworkbench.com/#install)

## screen FAQ

### How do I exit the screen command?

There are three exits and they do different things. Ctrl+a then d detaches: the shell and every job in it keep running, screen -ls shows the session as Detached, and screen -r brings it back. Typing exit (or Ctrl+d) closes the current window, and when the last window goes the session ends for good and prints screen is terminating. Ctrl+a then backslash kills every window at once after a confirmation. From outside, screen -S deploy -X quit ends a session without attaching to it first. If Ctrl+a d does nothing you are probably not inside screen: run echo \$STY, which prints the session name inside screen and nothing outside it.

### How do I scroll up inside screen?

Press Ctrl+a then \[ to enter copy mode, scroll with PgUp, PgDn, or the arrow keys, and press q to get back to a live prompt. The mouse wheel usually scrolls your terminal's own buffer instead, which mixes windows together, so copy mode is the reliable way. The real catch is the buffer size: screen keeps only 100 lines by default. Put defscrollback 10000 in ~/.screenrc, or run Ctrl+a :scrollback 10000 for the current window, and the history becomes worth scrolling.

### How do I kill all screen sessions at once?

pkill screen ends every session your user owns, attached ones included, so check screen -ls before running it. For detached sessions only, pipe the list into kill: screen -ls \| grep Detached \| cut -d. -f1 \| xargs -r kill. The PID is the number before the dot in each entry, so you can also kill them one at a time from that list. A single named session dies with screen -S deploy -X quit, no attaching needed. screen -wipe is not a kill: it only drops entries already marked Dead off the list.

### Why does screen say command not found?

screen is not installed. Minimal images, containers, and fresh cloud instances usually ship without it, and some distros dropped it from the default set. Install it with sudo apt install screen on Debian, Ubuntu, and Raspberry Pi OS, sudo dnf install screen on Fedora, RHEL, and Rocky, sudo apk add screen on Alpine, or sudo pacman -S screen on Arch. macOS carries an ancient 4.00.03 build at /usr/bin/screen; brew install screen puts a current one ahead of it in PATH. Windows has no screen, so run it inside WSL or on the Linux host you SSH into. With no sudo rights, check whether tmux is already there.

### Should I use screen or tmux?

For plain detach and reattach over SSH, either works and the keys map almost one to one: screen -S is tmux new -s, screen -r is tmux attach, and Ctrl+a d is Ctrl+b d. tmux is the better multiplexer, with real pane splitting, a status bar, a scriptable command language, and active development. screen keeps two advantages: it is preinstalled on more old and minimal systems, and it doubles as a serial terminal with screen /dev/ttyUSB0 115200, which tmux cannot do. On a box that has both, pick tmux; on a box you cannot install anything on, screen is usually already there.

---
Källa: https://sshworkbench.com/cheatsheets/screen
