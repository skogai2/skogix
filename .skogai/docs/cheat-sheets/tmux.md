# tmux Cheat Sheet

tmux is a terminal multiplexer: one SSH connection, many windows and panes, and sessions that keep running after you disconnect. The prefix is Ctrl+b unless you remapped it. Press it, let go, then press the key.

## Sessions

| Command | What it does |
|----|----|
| tmux | Start a new unnamed session |
| tmux new -s work | Start a session named work |
| tmux new -A -s work | Attach to work if it exists, otherwise create it |
| tmux new -d -s work | Create a session detached (scripts) |
| tmux ls | List sessions |
| tmux attach -t work | Attach to work |
| tmux a | Attach to the most recent session |
| tmux attach -d -t work | Attach and detach any other client (after a dropped connection) |
| tmux rename-session -t old new | Rename a session |
| tmux switch -t work | Switch sessions from inside tmux |
| tmux kill-session -t work | Kill one session |
| tmux kill-session -a | Kill every session except the current one |
| tmux kill-server | Kill everything |

| Command | What it does |
|---|---|
| `tmux` | Start new unnamed session |
| `tmux new -s dev` | Start new session named `dev` |
| `tmux ls` | List active sessions |
| `tmux attach -t dev` | Attach to existing session `dev` (`tmux a -t dev`) |
| `tmux kill-session -t dev` | Terminate session `dev` |
| `tmux kill-server` | Kill all tmux sessions and background server |

## Windows

Windows are tabs. The status bar at the bottom lists them by number.

| Keybinding | Action |
|---|---|
| `prefix c` | Create new window |
| `prefix ,` | Rename current window |
| `prefix n` / `prefix p` | Move to next / previous window |
| `prefix 0..9` | Select window by number |
| `prefix w` | Interactive visual window/session list |
| `prefix &` | Kill current window |

| Command                    | What it does                     |
|----------------------------|----------------------------------|
| tmux new-window -n logs    | New window named logs            |
| tmux rename-window logs    | Rename the current window        |
| tmux kill-window -t 2      | Kill window 2                    |
| tmux swap-window -s 2 -t 1 | Swap windows 2 and 1             |
| tmux move-window -t 0      | Renumber the current window to 0 |
| tmux select-window -t logs | Switch by name                   |

## Panes

prefix : opens a command prompt inside tmux; the : commands below go there.

| Keybinding | Action |
|---|---|
| `prefix %` | Split current pane horizontally (left / right) |
| `prefix "` | Split current pane vertically (top / bottom) |
| `prefix o` | Cycle focus to next pane |
| `prefix ;` | Toggle to previously active pane |
| `prefix x` | Close / kill current pane |
| `prefix z` | Toggle pane zoom (maximize / restore) |
| `prefix {` / `prefix }` | Swap current pane with previous / next pane |
| `prefix Space` | Cycle through preset pane layouts |
| `prefix q` | Briefly display pane index numbers |

| CLI / Prompt Command | What it does |
|---|---|
| `tmux split-window -h` | Split horizontally |
| `tmux split-window -v` | Split vertically |
| `tmux select-pane -L/-R/-U/-D` | Focus pane to the left, right, up, down |
| `tmux resize-pane -U 5` | Resize current pane 5 cells upward |
| `tmux kill-pane` | Terminate active pane |

## Copy Mode and Scrolling

prefix [ enters copy mode, which is also how you scroll back. Keys depend on mode-keys: emacs by default, vi after setw -g mode-keys vi.

| Emacs Keybinding (Default) | Vi Keybinding (`mode-keys vi`) | Action |
|---|---|---|
| `prefix [` | `prefix [` | Enter copy mode (enables scrolling) |
| `Page Up / Down` | `Ctrl+B / Ctrl+F` | Scroll full page up / down |
| `Ctrl+P / Ctrl+N` | `k / j` | Move up / down by line |
| `Ctrl+Space` | `v` or `Space` | Begin text selection |
| `Alt+W` | `y` | Copy selection into tmux buffer |
| `prefix ]` | `prefix ]` | Paste contents of tmux buffer |
| `q` | `q` or `Esc` | Exit copy mode |

| Emacs Keybinding (Default) | Vi Keybinding (`mode-keys vi`) | Action |
|---|---|---|
| `prefix [` | `prefix [` | Enter copy mode (enables scrolling) |
| `Page Up / Down` | `Ctrl+B / Ctrl+F` | Scroll full page up / down |
| `Ctrl+P / Ctrl+N` | `k / j` | Move up / down by line |
| `Ctrl+Space` | `v` or `Space` | Begin text selection |
| `Alt+W` | `y` | Copy selection into tmux buffer |
| `prefix ]` | `prefix ]` | Paste contents of tmux buffer |
| `q` | `q` or `Esc` | Exit copy mode |

Copies land in tmux's buffer, not the system clipboard. The config below pipes them to pbcopy; on Linux use xclip -selection clipboard or wl-copy.

## Prefix Key and Keybindings

| Keybinding | Default Binding | Description |
|---|---|---|
| Prefix Key | `Ctrl+B` | Leader key pressed before every tmux command shortcut |
| Command Prompt | `prefix :` | Open interactive tmux command prompt |
| Help / Keybindings | `prefix ?` | Display list of all active keybindings |
| Detach Session | `prefix d` | Detach from tmux while leaving processes running |
| Clock | `prefix t` | Display full-screen digital clock in active pane |

| Keybinding | Default Binding | Description |
|---|---|---|
| Prefix Key | `Ctrl+B` | Leader key pressed before every tmux command shortcut |
| Command Prompt | `prefix :` | Open interactive tmux command prompt |
| Help / Keybindings | `prefix ?` | Display list of all active keybindings |
| Detach Session | `prefix d` | Detach from tmux while leaving processes running |
| Clock | `prefix t` | Display full-screen digital clock in active pane |

## Config

The file is ~/.tmux.conf. tmux 3.1 and newer also read ~/.config/tmux/tmux.conf (or $XDG_CONFIG_HOME/tmux/tmux.conf), and a system-wide /etc/tmux.conf loads first when it exists. Changes apply to the running server after a reload.

| Command | What it does |
|----|----|
| tmux source-file ~/.tmux.conf | Reload the config |
| prefix :source-file ~/.tmux.conf | Same, from inside tmux |
| tmux show -g | Print the global options |
| tmux show -g prefix | Show the current prefix |
| tmux -f other.conf | Start with a different config file |
| tmux -V | Version; binding syntax changed in 2.4, so check this when a snippet fails |

A minimal .tmux.conf:

```
# Prefix on Ctrl+a, like screen
set -g prefix C-a
unbind C-b
bind C-a send-prefix

set -g mouse on
set -g history-limit 50000
set -g base-index 1
setw -g pane-base-index 1
setw -g mode-keys vi
set -g default-terminal "tmux-256color"
set -sg escape-time 10

# Splits that open in the current directory
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

bind r source-file ~/.tmux.conf \; display "Reloaded"

# vi-style select and copy to the system clipboard
bind -T copy-mode-vi v send -X begin-selection
bind -T copy-mode-vi y send -X copy-pipe-and-cancel "pbcopy"
```

Swap pbcopy for xclip -selection clipboard on X11 or wl-copy on Wayland.

## Status Bar

The bar at the bottom is configured with set -g status-* options, in ~/.tmux.conf or live from prefix :.

| Option | Default / Value | Description |
|---|---|---|
| `set -g status on` | `on` | Toggle status bar visibility (`on`/`off`) |
| `set -g status-position` | `bottom` | Place status bar at `top` or `bottom` |
| `set -g status-interval` | `15` | Update interval in seconds |
| `set -g status-left` | `"[#S] "` | Information on left side (session name) |
| `set -g status-right` | `"%H:%M %d-%b-%y"` | Information on right side (date/time, hostname) |

Anything in \#{...} is a format variable (#{pane_current_path}, \#{window_index}); \#(command) runs a shell command and shows its output. Colours accept names, colour0 to colour255, or \#RRGGBB, and 256-colour styles only render once set -g default-terminal "tmux-256color" is set.

## Plugins

Most tmux plugins are installed through TPM, the tmux Plugin Manager. Clone it once:

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

Then list plugins in ~/.tmux.conf, keeping the run line last:

```
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @plugin 'tmux-plugins/tmux-yank'

run '~/.tmux/plugins/tpm/tpm'
```

| Key or command | What it does |
|----|----|
| prefix I | Install everything listed in the config (capital I) |
| prefix U | Update plugins, with a picker |
| prefix Alt+u | Remove plugins no longer listed in the config |
| set -g @plugin 'user/repo' | Add a plugin; any GitHub repo works |
| prefix Ctrl+s | tmux-resurrect: save the current layout to disk |
| prefix Ctrl+r | tmux-resurrect: restore the saved layout |
| set -g @continuum-restore 'on' | tmux-continuum: restore automatically when the server starts |

Plugins land in ~/.tmux/plugins/, or ~/.config/tmux/plugins/ if your config lives under ~/.config/tmux, in which case clone TPM there instead. prefix I does nothing until the config with the @plugin lines has been sourced at least once.

## Install

tmux is not preinstalled on macOS and is missing from most minimal images and containers.

| Distribution | Command |
|---|---|
| Debian / Ubuntu | `sudo apt install tmux` |
| Arch Linux | `sudo pacman -S tmux` |
| Fedora / RHEL | `sudo dnf install tmux` |
| macOS (Homebrew) | `brew install tmux` |

Windows has no native tmux. Run it under WSL, or run it on the Linux host you connect to and let the client pass the keys through; the [PuTTY cheat sheet](https://sshworkbench.com/cheatsheets/putty) covers that side. With no root on the remote box, check for [screen](https://sshworkbench.com/cheatsheets/screen) first, since it is preinstalled more often, and fall back to building tmux from source with ./configure --prefix=$HOME/.local (it needs libevent and ncurses headers).

## Gotchas

- The prefix is a sequence, not a chord. Press Ctrl+b, release, then the key. Holding Ctrl through the whole thing sends Ctrl+c, Ctrl+d, and friends instead.
- Copy mode copies to tmux's own buffer. Nothing reaches the system clipboard until you add a copy-pipe binding or turn on set-clipboard on a terminal that supports it.
- A dropped SSH connection does not kill tmux. Reconnect and run tmux a; if it says the session is attached, tmux a -d. This is the reason to start every long job inside tmux; see [ssh broken pipe](https://sshworkbench.com/fix/ssh-broken-pipe) for stopping the drops themselves.
- With mouse on, the terminal's native drag-select is taken over by tmux. Hold Shift (Option in iTerm2, Fn in Terminal.app) to select with the terminal instead.
- Inside tmux over SSH inside another tmux, press the prefix twice to reach the inner one, or give the remote a different prefix.
- Vim feels sluggish on Esc until set -sg escape-time 10 is in the config.
- Snippets using bind -t vi-copy are for tmux 2.3 and older. Modern tmux wants bind -T copy-mode-vi ... send -X ....
- A reboot kills the tmux server and every session in it. Dropped connections are survivable, power cycles are not; see the Plugins section for tmux-resurrect.
- Coming from screen: the prefix is Ctrl+b instead of Ctrl+a, and screen -r is tmux a. The [screen cheat sheet](https://sshworkbench.com/cheatsheets/screen) has the rest of the key mapping.

## tmux FAQ

### How do I scroll up in tmux?

Press Ctrl+b then [ to enter copy mode, scroll with PgUp, PgDn, or the arrow keys, and press q to get back to the prompt. The mouse wheel does nothing until you add set -g mouse on to ~/.tmux.conf and reload; after that the wheel scrolls and enters copy mode on its own. How far back you can go is history-limit, which defaults to 2000 lines per pane; set -g history-limit 50000 is cheap and only applies to panes created after the reload.

### How do I exit tmux without closing the session?

Detach instead of exiting: Ctrl+b then d drops you back to the plain shell and leaves every program in the session running. Typing exit or pressing Ctrl+d does the opposite, closing the pane, then the window, and the session dies with its last window, taking the jobs with it. From another terminal, tmux detach -t work detaches a session you are not in, and Ctrl+b then D asks which client to kick off when several are attached. To check which happened, run tmux ls: a listed session is still alive, while "no server running" means everything really did exit.

### Do tmux sessions survive a reboot?

No. The tmux server is an ordinary process, so a reboot or a shutdown ends it along with every session and every command inside. What it does survive is the client going away: a dropped SSH connection, a closed terminal, or a laptop going to sleep. For layouts you want back after a reboot, the tmux-resurrect plugin saves the windows, panes, and working directories to disk with prefix Ctrl+s and restores them with prefix Ctrl+r, and tmux-continuum saves every 15 minutes and can restore on its own at startup. Neither brings running programs back to where they were, so anything that genuinely must outlive a reboot belongs in a systemd unit, not in tmux.

### Is tmux better than screen?

For most people, yes. tmux has real pane splitting, a scriptable command language, a status bar, and it is actively developed; screen is older and its pane support is an afterthought. screen still wins in two cases: it is preinstalled on more old or minimal systems, so it is what you get on a box you cannot install to, and it can attach to serial ports with screen /dev/ttyUSB0 115200, which tmux cannot do at all. The one thing that catches people switching is the prefix, Ctrl+a in screen against Ctrl+b in tmux; set -g prefix C-a moves it back. The screen cheat sheet on this site maps the rest of the keys.

### Does tmux work on Windows?

There is no native Windows build and no official port, so tmux on Windows means one of two things. Either run it inside WSL, where sudo apt install tmux works exactly as it does on Ubuntu, or run it on the Linux server you connect to and let PuTTY or Windows Terminal simply carry the keystrokes, which is what most people actually want. Git Bash bundles an MSYS2 tmux that mostly works but has redraw and clipboard quirks. If all you want is split panes on the Windows side, Windows Terminal does that itself with Alt+Shift+plus and Alt+Shift+minus, no tmux involved.

---
Source: https://sshworkbench.com/cheatsheets/tmux
