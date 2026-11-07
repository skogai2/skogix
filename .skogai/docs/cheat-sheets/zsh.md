# zsh Commands

zsh has been the default shell on macOS since Catalina and is a drop-in upgrade for bash on Linux. This sheet covers history search, aliases, completion, globbing, arrays, PATH, the startup files, plugins, and fixes for the errors it throws most.

Last updated September 11, 2026

On this page

- [History Search](#history-search)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Aliases](#aliases)
- [Completion](#completion)
- [Keybindings and Vi Mode](#keybindings-and-vi-mode)
- [Globbing](#globbing)
- [Arrays](#arrays)
- [Environment and PATH](#environment-and-path)
- [Startup Files](#startup-files)
- [Prompt](#prompt)
- [Oh My Zsh](#oh-my-zsh)
- [Plugins](#plugins)
- [Command Not Found Fixes](#command-not-found-fixes)
- [Permission Denied](#permission-denied)
- [Install and Switch Shells](#install-and-switch-shells)
- [One-Liners and Substitution](#one-liners-and-substitution)
- [zsh vs bash](#zsh-vs-bash)
- [Gotchas](#gotchas)

## History Search

[TABLE]

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

Copy

zsh: corrupt history file /Users/you/.zsh_history means the file has bad bytes in it. Salvage what is readable:

```
mv ~/.zsh_history ~/.zsh_history_bad
strings ~/.zsh_history_bad > ~/.zsh_history
fc -R ~/.zsh_history
```

Copy

## Keyboard Shortcuts

Emacs-style bindings, the default. See the next section for vi mode.

[TABLE]

## Aliases

[TABLE]

Aliases live for one session unless you put them in ~/.zshrc:

```
echo "alias ll='ls -lah'" >> ~/.zshrc
source ~/.zshrc
```

Copy

An alias cannot take arguments; anything you type is appended to the end. When you need the argument in the middle, write a function instead:

```
mkcd() { mkdir -p "$1" && cd "$1" }
gclone() { git clone "https://github.com/$1.git" && cd "${1##*/}" }
```

Copy

## Completion

zsh's completion system knows flags, hostnames, git branches, and PIDs, but only after you turn it on.

[TABLE]

## Keybindings and Vi Mode

[TABLE]

In vi normal mode: k/j step through history, / searches it, v opens the line in your editor.

## Globbing

zsh globbing does what you would otherwise need find for. Recursive \*\* works out of the box.

| Pattern             | What it matches                                  |
|---------------------|--------------------------------------------------|
| ls \*\*/\*.js       | All .js files, recursively                       |
| ls \*(.)            | Regular files only                               |
| ls \*(/)            | Directories only                                 |
| ls \*(@)            | Symlinks only                                    |
| ls \*(om\[1\])      | The most recently modified file                  |
| ls \*(om\[1,5\])    | The five most recently modified                  |
| ls \*(.Lm+10)       | Files larger than 10 MB                          |
| ls \*.txt~notes.txt | All .txt except notes.txt (needs extendedglob)   |
| ls ^\*.md           | Everything except .md files (needs extendedglob) |
| ls \*(.N)           | Files, and no error when nothing matches         |

```
setopt extendedglob   # enables ^negation and the ~exclusion operator
```

Copy

For heavier searches (by mtime, with -exec), see the [find cheat sheet](https://sshworkbench.com/cheatsheets/find).

zmv renames in bulk using the same patterns, with -n for a dry run:

```
autoload -Uz zmv
zmv -n '(*).jpeg' '$1.jpg'      # drop -n to actually rename
zmv -n '(**/)(*).log' '$1$2.txt'
zmv -nW '*.txt' 'backup_*.txt'  # -W uses plain wildcards instead of groups
```

Copy

## Arrays

zsh arrays start at 1, not 0, and a bare \$a gives every element rather than the first. Both trip up pasted bash code.

[TABLE]

## Environment and PATH

zsh ties the path array to \$PATH, so you can edit it like a list instead of pasting colons.

[TABLE]

PATH belongs in ~/.zprofile so it is set once per login instead of growing in every nested shell:

```
# ~/.zprofile
typeset -U path
path=(/opt/homebrew/bin /opt/homebrew/sbin $path ~/bin)
export PATH
```

Copy

## Startup Files

Read in this order. macOS Terminal and iTerm open login shells, so .zprofile and .zshrc both run; most Linux terminals open non-login shells, so only .zshrc runs.

[TABLE]

After editing any of them: source ~/.zshrc (or open a new tab).

## Prompt

[TABLE]

Common escapes: %n user, %m host, %~ directory with ~, %# % or \#, %T time, %? last exit code. Most people skip hand-rolling and install powerlevel10k or starship, which come with git status, exit codes, and language versions built in.

## Oh My Zsh

A config framework: themes, completion tweaks, and plugins in one install. Everything lives in ~/.zshrc after it is set up.

[TABLE]

The git plugin is why most people install it. The aliases you will actually use:

[TABLE]

Run alias \| grep git to see the full list (150+).

## Plugins

The two everyone installs are autosuggestions and syntax highlighting. Neither needs a framework; they are repos you source from ~/.zshrc.

[TABLE]

```
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.zsh/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.zsh/zsh-syntax-highlighting

# in ~/.zshrc, syntax highlighting must be sourced last
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

Copy

With Oh My Zsh, clone into \$ZSH_CUSTOM/plugins instead and add the names to the plugins=(...) line. If startup gets slow, a manager that lazy-loads (zinit, antidote, zim) is the usual next step, or drop the framework and keep the source lines.

## Command Not Found Fixes

zsh: command not found: X means the binary is not on your PATH or is not a binary at all. The pattern is the same for brew, pip, npm, nvm, docker, and code.

[TABLE]

## Permission Denied

zsh: permission denied: ./deploy.sh is about the file, not about zsh. The shell found it and the kernel refused to run it.

[TABLE]

## Install and Switch Shells

[TABLE]

On Windows there is no native zsh. Install it inside WSL (wsl --install, then sudo apt install zsh) and set it as the default shell in the Linux distro, not in PowerShell.

## One-Liners and Substitution

| Command | What it does |
|----|----|
| cd /tmp && ls | Run the second only if the first succeeds |
| make; echo done | Run both regardless |
| ping -c1 host \|\| echo down | Run the second only if the first fails |
| out=\$(hostname) | Capture a command's output in a variable |
| echo "Today is \$(date +%F)" | Substitute output inline |
| echo \$(( 7 \* 6 )) | Arithmetic |
| for f in \*.log; do gzip "\$f"; done | Loop over files on one line |

## zsh vs bash

Typing commands feels identical, since ls, grep, git and ssh are programs, not shell features. What differs is quoting, arrays and globbing. For bash syntax itself, see the [bash cheat sheet](https://sshworkbench.com/cheatsheets/bash).

[TABLE]

The three that break a pasted bash snippet:

```
files="a.txt b.txt"
ls $files      # zsh looks for one file named "a.txt b.txt"; use ${=files} to split

a=(x y z)
echo $a[1]     # zsh prints x; the same array in bash starts at ${a[0]}

ls *.nope      # zsh: "no matches found" and ls never runs; bash passes *.nope to ls
```

Copy

Scripts are unaffected: a \#!/bin/bash shebang runs the script in bash whatever your login shell is. Write new scripts for the shell you name in the shebang.

## Gotchas

- zsh: no matches found
  when a URL contains
  ?
  or
  \*
  : zsh globs the argument. Quote it (
  curl 'https://api.example.com/x?y=1'
  ) or
  setopt no_nomatch
  .
- \#
  comments do not work at the interactive prompt by default:
  setopt interactive_comments
  (Oh My Zsh turns this on for you).
- zsh: event not found
  on a command containing
  !
  inside double quotes: history expansion fires before anything else. Use single quotes, or
  setopt no_bang_hist
  to switch it off.
- zsh: you have suspended jobs
  when you try to exit: run
  jobs
  to see them,
  fg
  to finish one, or
  disown -a
  to cut them loose. A second
  exit
  also works.
- zsh: killed
  on a Mac binary you downloaded is Gatekeeper, not memory:
  xattr -d com.apple.quarantine ./tool
  . On a server it usually is memory, and
  dmesg \| tail
  will say so.
- Pasted multi-line snippets run line by line as they land. Paste into
  Ctrl+X Ctrl+E
  (editor) if you want to review first.
- A new PATH entry in
  ~/.zshrc
  only applies to new shells;
  source ~/.zshrc
  fixes the current one.
- zsh writes each terminal's history at exit by default;
  setopt SHARE_HISTORY
  if you want tabs to see each other's commands live.
- Long remote sessions die with the connection. Run zsh inside [tmux](https://sshworkbench.com/cheatsheets/tmux) on servers so your shell survives a dropped SSH connection.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## zsh FAQ

### Why zsh over bash?

Apple switched the macOS default in Catalina (2019) because the bash it shipped was stuck at version 3.2 from 2007; newer bash releases moved to the GPLv3 license, which Apple avoids. What you get over bash 3.2 day to day: completion that knows flags, hostnames, git branches and PIDs, glob qualifiers that replace most simple find calls, suffix and global aliases, and spelling correction on mistyped commands. What you give up is nothing, since your scripts keep running under their own shebang. On Linux bash is fine and stays the system shell; zsh is a choice about your interactive prompt, not about your servers.

### Should I use .zshrc or .zprofile?

~/.zprofile runs once per login shell, ~/.zshrc runs for every interactive shell, and .zprofile runs first. PATH edits and eval "\$(brew shellenv)" belong in .zprofile so they run once; aliases, functions, keybindings, completion and prompt config belong in .zshrc. The reason it matters is duplication: PATH lines in .zshrc run again in every nested shell, so PATH grows every time you type zsh or open a subshell. If you keep PATH in .zshrc anyway, add typeset -U path so duplicate entries collapse. On macOS every terminal tab is a login shell so both files run; on Linux terminals are usually non-login, so anything you put only in .zprofile is missing until you log in fresh.

### Does zsh use .bashrc?

No. zsh never reads ~/.bashrc or ~/.bash_profile, which is why everything seems to vanish the day you switch. It does not read ~/.profile either unless you source it yourself. Move your aliases, functions, PATH exports and tool init lines (nvm, pyenv, conda, rbenv) into ~/.zshrc or ~/.zprofile by hand. Sourcing .bashrc from .zshrc mostly works for plain exports and aliases but breaks on shopt, complete, PROMPT_COMMAND and PS1 escapes, so copy the lines you want instead of sourcing the file.

### Can zsh run bash scripts?

Yes. A script with a \#!/bin/bash shebang runs in bash no matter which shell you launched it from, so your login shell never changes how a script behaves. The trap is scripts with no shebang, or bash snippets you paste straight into an interactive zsh prompt: there zsh's own rules apply, and three of them bite. Unquoted variables are not word-split, arrays are indexed from 1, and a glob that matches nothing is a hard error instead of being passed through literally. Run bash script.sh explicitly when you are unsure, and see the bash cheat sheet at /cheatsheets/bash for the syntax itself.

### Why is zsh slow to start?

Almost always a plugin or a version manager, not zsh. Measure before you cut: add zmodload zsh/zprof as the first line of ~/.zshrc and run zprof in a new shell to get a ranked list of what ran. Common culprits are nvm (200ms or more on its own, fixable with lazy loading or by switching to fnm), conda init, pyenv init, and compinit rebuilding its cache on every start. Replace the plain compinit call with a once-a-day version: autoload -Uz compinit; compinit -C, with a full compinit run only when ~/.zcompdump is older than a day. If the prompt is the slow part, powerlevel10k's instant prompt paints the line before the rest of the config loads.

---
Källa: https://sshworkbench.com/cheatsheets/zsh
