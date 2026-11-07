# zsh Commands

zsh has been the default shell on macOS since Catalina and is a drop-in upgrade for bash on Linux. This sheet covers history search, aliases, completion, globbing, arrays, PATH, the startup files, plugins, and fixes for the errors it throws most.

## History Search

| Keybinding / Command | Action |
|---|---|
| `Ctrl+R` | Incremental reverse history search |
| `Up / Down` | Browse previous commands (or history search with `up-line-or-beginning-search`) |
| `history` | Print numbered history list |
| `fc -l -N` | Show last `N` history entries |
| `fc -e -` | Re-run last command without opening editor |

History size and behaviour go in ~/.zshrc:

```
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY          # share history across open terminals
setopt HIST_IGNORE_ALL_DUPS   # keep one copy of a repeated command
setopt HIST_IGNORE_SPACE      # commands starting with a space are not saved
setopt EXTENDED_HISTORY       # record a timestamp with each command

# Up/Down search commands starting with what you typed
bindkey '^[[A' history-beginning-search-backward
bindkey '^[[B' history-beginning-search-forward
```

zsh: corrupt history file /Users/you/.zsh_history means the file has bad bytes in it. Salvage what is readable:

```
mv ~/.zsh_history ~/.zsh_history_bad
strings ~/.zsh_history_bad > ~/.zsh_history
fc -R ~/.zsh_history
```

## Keyboard Shortcuts

Emacs-style bindings, the default. See the next section for vi mode.

| Keybinding | Action |
|---|---|
| `Ctrl+A` | Move cursor to start of line |
| `Ctrl+E` | Move cursor to end of line |
| `Ctrl+U` | Delete entire line before cursor |
| `Ctrl+K` | Delete from cursor to end of line |
| `Ctrl+W` | Delete word backwards |
| `Ctrl+L` | Clear screen |

## Aliases

| Alias Type | Example | What it does |
|---|---|---|
| Standard | `alias ll='ls -la'` | Normal command alias |
| Global | `alias -g G='\| grep'` | Expanded anywhere in command line (`cat file G error`) |
| Suffix | `alias -s txt=nvim` | Running `notes.txt` directly opens it in Neovim |
| Unalias | `unalias ll` | Remove alias definition |

Aliases live for one session unless you put them in ~/.zshrc:

```
echo "alias ll='ls -lah'" >> ~/.zshrc
source ~/.zshrc
```

An alias cannot take arguments; anything you type is appended to the end. When you need the argument in the middle, write a function instead:

```bash
mkcd() { mkdir -p "$1" && cd "$1" }
gclone() { git clone "https://github.com/$1.git" && cd "${1##*/}" }
```

## Completion

zsh's completion system knows flags, hostnames, git branches, and PIDs, but only after you turn it on.

| Command / Directive | What it does |
|---|---|
| `autoload -Uz compinit && compinit` | Initialize Zsh completion system |
| `zstyle ':completion:*' menu select` | Enable visual arrow-key completion menu |
| `zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'` | Case-insensitive tab completion |

## Keybindings and Vi Mode

| Command | What it does |
|---|---|
| `bindkey -e` | Enable Emacs keybindings (default) |
| `bindkey -v` | Enable Vi keybindings (modal editing on command line) |
| `bindkey` | List all active keybindings |
| `bindkey '^R' history-incremental-search-backward` | Rebind Ctrl+R in Vi mode |

In vi normal mode: k/j step through history, / searches it, v opens the line in your editor.

## Globbing

zsh globbing does what you would otherwise need find for. Recursive ** works out of the box.

| Pattern             | What it matches                                  |
|---------------------|--------------------------------------------------|
| ls **/*.js       | All .js files, recursively                       |
| ls *(.)            | Regular files only                               |
| ls *(/)            | Directories only                                 |
| ls *(@)            | Symlinks only                                    |
| ls *(om[1])      | The most recently modified file                  |
| ls *(om[1,5])    | The five most recently modified                  |
| ls *(.Lm+10)       | Files larger than 10 MB                          |
| ls *.txt~notes.txt | All .txt except notes.txt (needs extendedglob)   |
| ls ^*.md           | Everything except .md files (needs extendedglob) |
| ls *(.N)           | Files, and no error when nothing matches         |

```
setopt extendedglob   # enables ^negation and the ~exclusion operator
```

For heavier searches (by mtime, with -exec), see the [find cheat sheet](https://sshworkbench.com/cheatsheets/find).

zmv renames in bulk using the same patterns, with -n for a dry run:

```
autoload -Uz zmv
zmv -n '(*).jpeg' '$1.jpg'      # drop -n to actually rename
zmv -n '(**/)(*).log' '$1$2.txt'
zmv -nW '*.txt' 'backup_*.txt'  # -W uses plain wildcards instead of groups
```

## Arrays

zsh arrays start at 1, not 0, and a bare $a gives every element rather than the first. Both trip up pasted bash code.

| Syntax | What it does |
|---|---|
| `arr=(alpha beta gamma)` | Create array (1-indexed in Zsh by default) |
| `echo $arr[1]` | Access first element (`alpha`, not 0-based) |
| `echo $arr[-1]` | Access last element |
| `echo $#arr` | Array length / number of elements |
| `arr+=(delta)` | Append element to array |

## Environment and PATH

zsh ties the path array to $PATH, so you can edit it like a list instead of pasting colons.

| Directive | What it does |
|---|---|
| `path=(/opt/bin $path)` | Prepend directory to `$PATH` using native array syntax |
| `typeset -U path` | Ensure all `$PATH` entries are unique (drops duplicates) |
| `export VAR="value"` | Export environment variable to child processes |

PATH belongs in ~/.zprofile so it is set once per login instead of growing in every nested shell:

```
# ~/.zprofile
typeset -U path
path=(/opt/homebrew/bin /opt/homebrew/sbin $path ~/bin)
export PATH
```

## Startup Files

Read in this order. macOS Terminal and iTerm open login shells, so .zprofile and .zshrc both run; most Linux terminals open non-login shells, so only .zshrc runs.

| File | When it runs | Purpose |
|---|---|---|
| `/etc/zshenv`, `~/.zshenv` | Every Zsh instance | Essential environment variables (read by all shells) |
| `/etc/zprofile`, `~/.zprofile` | Login shell | Setup commands run before login |
| `/etc/zshrc`, `~/.zshrc` | Interactive shell | Prompts, aliases, completion, functions, plugins |
| `/etc/zlogin`, `~/.zlogin` | Login shell | Commands run after shell is fully loaded |
| `/etc/zlogout`, `~/.zlogout` | Login shell exit | Cleanup commands executed on logout |

After editing any of them: source ~/.zshrc (or open a new tab).

## Prompt

| Prompt Escape | Meaning |
|---|---|
| `%n` | Current username |
| `%m` | Hostname (short) |
| `%~` | Current working directory with `~` replacement |
| `%#` | `#` for root, `%` for unprivileged user |
| `%F{green}...%f` | Foreground color |
| `%B...%b` | Bold text |

Common escapes: %n user, %m host, %~ directory with ~, %# % or \#, %T time, %? last exit code. Most people skip hand-rolling and install powerlevel10k or starship, which come with git status, exit codes, and language versions built in.

## Oh My Zsh

A config framework: themes, completion tweaks, and plugins in one install. Everything lives in ~/.zshrc after it is set up.

| Component | Location / Setting | Description |
|---|---|---|
| Core Directory | `~/.oh-my-zsh` | Framework installation path |
| Config File | `~/.zshrc` | Main user configuration |
| Theme | `ZSH_THEME="robbyrussell"` | Active prompt theme |
| Plugins | `plugins=(git docker z)` | Active plugin list |
| Upgrade | `omz update` | Update framework to latest release |

The git plugin is why most people install it. The aliases you will actually use:

| Component | Location / Setting | Description |
|---|---|---|
| Core Directory | `~/.oh-my-zsh` | Framework installation path |
| Config File | `~/.zshrc` | Main user configuration |
| Theme | `ZSH_THEME="robbyrussell"` | Active prompt theme |
| Plugins | `plugins=(git docker z)` | Active plugin list |
| Upgrade | `omz update` | Update framework to latest release |

Run alias \| grep git to see the full list (150+).

## Plugins

The two everyone installs are autosuggestions and syntax highlighting. Neither needs a framework; they are repos you source from ~/.zshrc.

| Popular Plugin | Purpose |
|---|---|
| `zsh-autosuggestions` | Fish-like command autosuggestions as you type |
| `zsh-syntax-highlighting` | Real-time syntax highlighting for commands |
| `zsh-completions` | Additional completion definitions for 100+ CLI tools |
| `z` / `zoxide` | Fast directory jumping based on frequency |

```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.zsh/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.zsh/zsh-syntax-highlighting

# in ~/.zshrc, syntax highlighting must be sourced last
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

With Oh My Zsh, clone into $ZSH_CUSTOM/plugins instead and add the names to the plugins=(...) line. If startup gets slow, a manager that lazy-loads (zinit, antidote, zim) is the usual next step, or drop the framework and keep the source lines.

## Command Not Found Fixes

zsh: command not found: X means the binary is not on your PATH or is not a binary at all. The pattern is the same for brew, pip, npm, nvm, docker, and code.

| Platform | Package | Purpose |
|---|---|---|
| Debian / Ubuntu | `command-not-found` | Suggests apt package when command is missing |
| Arch Linux | `pkgfile` | Suggests pacman package via `pkgfile -u` |
| Fedora | `PackageKit-command-not-found` | Suggests dnf packages |

## Permission Denied

zsh: permission denied: ./deploy.sh is about the file, not about zsh. The shell found it and the kernel refused to run it.

| Cause | Solution |
|---|---|
| File not executable | Run `chmod +x script.sh` |
| Directory unsearchable | Ensure parent directory has execute permission (`chmod +x dir`) |
| Root permissions required | Run with `sudo` |

## Install and Switch Shells

| Step | Command |
|---|---|
| Install (Debian/Ubuntu) | `sudo apt install zsh` |
| Install (Arch) | `sudo pacman -S zsh` |
| Install (Fedora) | `sudo dnf install zsh` |
| Switch default shell | `chsh -s $(which zsh)` |
| Verify current shell | `echo $SHELL` |

On Windows there is no native zsh. Install it inside WSL (wsl --install, then sudo apt install zsh) and set it as the default shell in the Linux distro, not in PowerShell.

## One-Liners and Substitution

| Command | What it does |
|----|----|
| cd /tmp && ls | Run the second only if the first succeeds |
| make; echo done | Run both regardless |
| ping -c1 host \|\| echo down | Run the second only if the first fails |
| out=$(hostname) | Capture a command's output in a variable |
| echo "Today is $(date +%F)" | Substitute output inline |
| echo $(( 7 * 6 )) | Arithmetic |
| for f in *.log; do gzip "$f"; done | Loop over files on one line |

## zsh vs bash

Typing commands feels identical, since ls, grep, git and ssh are programs, not shell features. What differs is quoting, arrays and globbing. For bash syntax itself, see the [bash cheat sheet](https://sshworkbench.com/cheatsheets/bash).

| Feature | Zsh | Bash |
|---|---|---|
| Default Array Index | 1-based (`$arr[1]`) | 0-based (`${arr[0]}`) |
| Recursive Globbing | Built-in (`**/*`) | Requires `shopt -s globstar` |
| Global / Suffix Aliases | Supported (`alias -g`, `alias -s`) | Not supported |
| Floating Point Math | Native support | Requires external tools (`bc`, `awk`) |
| Default License | MIT-like | GNU GPLv3 |

The three that break a pasted bash snippet:

```
files="a.txt b.txt"
ls $files      # zsh looks for one file named "a.txt b.txt"; use ${=files} to split

a=(x y z)
echo $a[1]     # zsh prints x; the same array in bash starts at ${a[0]}

ls *.nope      # zsh: "no matches found" and ls never runs; bash passes *.nope to ls
```

Scripts are unaffected: a \#!/bin/bash shebang runs the script in bash whatever your login shell is. Write new scripts for the shell you name in the shebang.

## Gotchas

- zsh: no matches found when a URL contains? or *: zsh globs the argument. Quote it ( curl 'https://api.example.com/x?y=1') or setopt no_nomatch.
- \# comments do not work at the interactive prompt by default: setopt interactive_comments (Oh My Zsh turns this on for you).
- zsh: event not found on a command containing ! inside double quotes: history expansion fires before anything else. Use single quotes, or setopt no_bang_hist to switch it off.
- zsh: you have suspended jobs when you try to exit: run jobs to see them, fg to finish one, or disown -a to cut them loose. A second exit also works.
- zsh: killed on a Mac binary you downloaded is Gatekeeper, not memory: xattr -d com.apple.quarantine ./tool. On a server it usually is memory, and dmesg \| tail will say so.
- Pasted multi-line snippets run line by line as they land. Paste into Ctrl+X Ctrl+E (editor) if you want to review first.
- A new PATH entry in ~/.zshrc only applies to new shells; source ~/.zshrc fixes the current one.
- zsh writes each terminal's history at exit by default; setopt SHARE_HISTORY if you want tabs to see each other's commands live.
- Long remote sessions die with the connection. Run zsh inside [tmux](https://sshworkbench.com/cheatsheets/tmux) on servers so your shell survives a dropped SSH connection.

## zsh FAQ

### Why zsh over bash?

Apple switched the macOS default in Catalina (2019) because the bash it shipped was stuck at version 3.2 from 2007; newer bash releases moved to the GPLv3 license, which Apple avoids. What you get over bash 3.2 day to day: completion that knows flags, hostnames, git branches and PIDs, glob qualifiers that replace most simple find calls, suffix and global aliases, and spelling correction on mistyped commands. What you give up is nothing, since your scripts keep running under their own shebang. On Linux bash is fine and stays the system shell; zsh is a choice about your interactive prompt, not about your servers.

### Should I use .zshrc or .zprofile?

~/.zprofile runs once per login shell, ~/.zshrc runs for every interactive shell, and .zprofile runs first. PATH edits and eval "$(brew shellenv)" belong in .zprofile so they run once; aliases, functions, keybindings, completion and prompt config belong in .zshrc. The reason it matters is duplication: PATH lines in .zshrc run again in every nested shell, so PATH grows every time you type zsh or open a subshell. If you keep PATH in .zshrc anyway, add typeset -U path so duplicate entries collapse. On macOS every terminal tab is a login shell so both files run; on Linux terminals are usually non-login, so anything you put only in .zprofile is missing until you log in fresh.

### Does zsh use .bashrc?

No. zsh never reads ~/.bashrc or ~/.bash_profile, which is why everything seems to vanish the day you switch. It does not read ~/.profile either unless you source it yourself. Move your aliases, functions, PATH exports and tool init lines (nvm, pyenv, conda, rbenv) into ~/.zshrc or ~/.zprofile by hand. Sourcing .bashrc from .zshrc mostly works for plain exports and aliases but breaks on shopt, complete, PROMPT_COMMAND and PS1 escapes, so copy the lines you want instead of sourcing the file.

### Can zsh run bash scripts?

Yes. A script with a \#!/bin/bash shebang runs in bash no matter which shell you launched it from, so your login shell never changes how a script behaves. The trap is scripts with no shebang, or bash snippets you paste straight into an interactive zsh prompt: there zsh's own rules apply, and three of them bite. Unquoted variables are not word-split, arrays are indexed from 1, and a glob that matches nothing is a hard error instead of being passed through literally. Run bash script.sh explicitly when you are unsure, and see the bash cheat sheet at /cheatsheets/bash for the syntax itself.

### Why is zsh slow to start?

Almost always a plugin or a version manager, not zsh. Measure before you cut: add zmodload zsh/zprof as the first line of ~/.zshrc and run zprof in a new shell to get a ranked list of what ran. Common culprits are nvm (200ms or more on its own, fixable with lazy loading or by switching to fnm), conda init, pyenv init, and compinit rebuilding its cache on every start. Replace the plain compinit call with a once-a-day version: autoload -Uz compinit; compinit -C, with a full compinit run only when ~/.zcompdump is older than a day. If the prompt is the slow part, powerlevel10k's instant prompt paints the line before the rest of the config loads.

---
Source: https://sshworkbench.com/cheatsheets/zsh
