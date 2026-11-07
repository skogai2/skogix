# Bash Cheat Sheet

Bash is the default shell on most Linux servers, so half of any bash cheat sheet is just Linux commands. This sheet covers both sides: the commands you type at the prompt and the syntax that only matters in scripts, from test operators to arrays and parameter expansion.

Last updated September 11, 2026

On this page

- [Navigation](#navigation)
- [File Commands](#file-commands)
- [Networking](#networking)
- [Jobs and Processes](#jobs-and-processes)
- [Variables](#variables)
- [If and Test Operators](#if-and-test-operators)
- [Case Statements](#case-statements)
- [Loops](#loops)
- [Arrays](#arrays)
- [Parameter Expansion](#parameter-expansion)
- [Arithmetic](#arithmetic)
- [Globbing](#globbing)
- [Redirection and Pipes](#redirection-and-pipes)
- [Command Substitution](#command-substitution)
- [Reading Input](#reading-input)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Vi Mode](#vi-mode)
- [History](#history)
- [Startup Files](#startup-files)
- [Exit Codes](#exit-codes)
- [Regex](#regex)
- [Functions](#functions)
- [Running Scripts](#running-scripts)
- [Script Arguments](#script-arguments)
- [Windows Equivalents](#windows-equivalents)
- [Gotchas](#gotchas)

## Navigation

[TABLE]

## File Commands

[TABLE]

## Networking

Not bash itself, but the commands every bash cheat sheet gets used for on a server.

[TABLE]

## Jobs and Processes

[TABLE]

If exit answers "There are stopped jobs", run jobs to see them, then fg to finish each one or kill %1 to drop it. A second exit leaves anyway and kills them.

## Variables

No spaces around the equals sign, and quote expansions unless you want word splitting.

[TABLE]

## If and Test Operators

Use \[\[ \]\] in bash: it is safer with unquoted variables than \[ \] and adds glob and regex matching.

```
if [[ -f "$conf" ]]; then
  echo "found"
elif [[ -d /etc/nginx ]]; then
  echo "directory only"
else
  echo "missing"
fi
```

Copy

[TABLE]

Combine with && and \|\| inside \[\[ \]\], negate with !.

## Case Statements

Cleaner than a stack of elif when one value has several possible shapes.

```
case "$1" in
  start)          systemctl start app ;;
  stop)           systemctl stop app ;;
  restart|reload) systemctl restart app ;;   # | separates alternatives
  *.log)          echo "that is a log file" ;;
  "")             echo "no argument given" ;;
  *)              echo "usage: $0 {start|stop|restart}" >&2; exit 2 ;;
esac
```

Copy

- The patterns are globs, not regex, and the first match wins, so
  \*)
  goes last as the catch-all.
- ;;
  ends a branch.
  ;&
  falls straight into the next branch,
  ;;&
  carries on testing the remaining patterns (bash 4+).
- shopt -s nocasematch
  makes the matching case-insensitive.

## Loops

```
for f in *.log; do            # every .log file here
  echo "$f"
done

for i in {1..5}; do           # brace range: 1 2 3 4 5
  echo "$i"
done

for ((i = 0; i < 3; i++)); do  # C-style counter
  echo "$i"
done

while read -r line; do        # a file, one line at a time
  echo "$line"
done < servers.txt

until ssh -q web1 true; do    # retry until it succeeds
  sleep 5
done
```

Copy

break leaves the loop, continue skips to the next round.

## Arrays

Indexed from 0, and "\${arr\[@\]}" must be quoted or elements with spaces split apart.

```
arr=(one two three)
arr+=(four)              # append
echo "${arr[0]}"         # first element
echo "${arr[-1]}"        # last element
echo "${arr[@]}"         # all elements
echo "${#arr[@]}"        # how many
unset 'arr[1]'           # remove one (indexes keep their gaps)

for item in "${arr[@]}"; do
  echo "$item"
done

declare -A port=([http]=80 [ssh]=22)   # associative array, bash 4+
echo "${port[ssh]}"
for key in "${!port[@]}"; do
  echo "$key -> ${port[$key]}"
done
```

Copy

## Parameter Expansion

String surgery without spawning sed. The keyboard is the mnemonic for the confusing pair: \# sits left of \$ and cuts from the front, % sits right of it and cuts from the back. One symbol takes the shortest match, doubled takes the longest. The patterns are globs, not regex.

[TABLE]

## Arithmetic

Integers only. Bash cannot do decimals on its own.

[TABLE]

\$(( )) is arithmetic, \$( ) runs a command. A stray space between the parentheses changes which one you get.

## Globbing

Bash expands these before the command ever runs, so rm \*.log is the shell handing rm a list of names.

[TABLE]

Quote the pattern when the command should do its own matching: find . -name "\*.log" and rsync --exclude '\*.tmp' both want the pattern intact, not a list of files the shell already expanded.

## Redirection and Pipes

[TABLE]

Multi-line input goes through a heredoc; quote the delimiter (\<\<'EOF') to stop expansion inside it.

```
cat > /etc/motd <<EOF
Welcome to $(hostname)
EOF
```

Copy

## Command Substitution

[TABLE]

\$( ) nests cleanly, as in \$(basename "\$(pwd)"). Backticks do the same job but are the legacy form.

## Reading Input

Always pass -r, or read eats backslashes in the input.

[TABLE]

A yes/no prompt, defaulting to no:

```
read -rp "Deploy to production? [y/N] " ans
[[ "$ans" == [yY]* ]] || exit 0
```

Copy

Prompting inside a while read ... done \< file loop does not work: the loop already owns stdin, so the prompt reads the next line of the file. Add \< /dev/tty to the inner read.

## Keyboard Shortcuts

Bash line editing is readline; these work in any readline program, psql and python included.

[TABLE]

## Vi Mode

The table above is emacs mode, the bash default. set -o vi swaps it for vi keys; put it in ~/.bashrc, or set editing-mode vi in ~/.inputrc to change every readline program at once. You start in insert mode, so press Esc first.

[TABLE]

Ctrl+R and Ctrl+C still work from insert mode, so history search does not go away.

## History

[TABLE]

Worth setting in ~/.bashrc:

```
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTTIMEFORMAT='%F %T '
export HISTCONTROL=ignoredups:ignorespace  # skip duplicates; a leading space hides a command
```

Copy

## Startup Files

[TABLE]

- A login shell does not read
  ~/.bashrc
  . That is why most
  ~/.bash_profile
  files contain
  \[\[ -f ~/.bashrc \]\] && . ~/.bashrc
  , and why a
  PATH
  you set in one file is missing in the other.
- These files are sourced, not executed, so they need no
  chmod +x
  and no shebang.
- ssh host 'command'
  starts a non-interactive shell. Bash does read
  ~/.bashrc
  there, but most distro copies open with a line that returns early when the shell is not interactive, so anything below it never applies to remote commands.
- A prompt that redraws over itself usually means unescaped colour codes in
  PS1
  . Wrap every escape sequence in
  \\
  and
  \\
  so bash does not count it towards the line width.

## Exit Codes

| Command | What it does |
|----|----|
| echo \$? | Exit code of the last command; 0 means success |
| cmd && next | Run next only if cmd succeeded |
| cmd \|\| fallback | Run fallback only if cmd failed |
| exit 1 | Leave the script with that code |
| set -e | Stop the script at the first failing command |
| set -u | Treat unset variables as errors |
| set -o pipefail | A pipeline fails if any stage fails, not just the last |
| set -euo pipefail | All three; the usual first line after the shebang |
| trap 'rm -f "\$tmp"' EXIT | Run cleanup when the script exits, however it exits |

Codes worth recognising: 126 found but not executable, 127 command not found, 130 killed with Ctrl+C, and 128+N killed by signal N.

## Regex

\[\[ =~ \]\] matches POSIX extended regex; capture groups land in BASH_REMATCH.

```
re='^([0-9]+)\.([0-9]+)'
if [[ $version =~ $re ]]; then
  major="${BASH_REMATCH[1]}"
  minor="${BASH_REMATCH[2]}"
fi
```

Copy

- Keep the pattern in a variable and unquoted after
  =~
  ; quoting it makes bash match the text literally.
- POSIX extended regex has no
  \d
  ,
  \w
  or
  \s
  . Write
  \[0-9\]
  ,
  \[\[:alnum:\]\]
  and
  \[\[:space:\]\]
  instead.
- BASH_REMATCH
  is overwritten by the next
  =~
  , so copy what you need straight away.
- case
  statements and
  \[\[ == \]\]
  use globs (
  \*
  ,
  ?
  ,
  \[a-z\]
  ), not regex.
- To match inside files use [grep](https://sshworkbench.com/cheatsheets/grep); to edit with a pattern use [sed](https://sshworkbench.com/cheatsheets/sed).

## Functions

```
deploy() {
  local target="$1"
  if [[ -z "$target" ]]; then
    echo "usage: deploy <host>" >&2
    return 2
  fi
  rsync -az ./site/ "$target:/var/www/"
}

deploy web1
```

Copy

- local
  keeps a variable inside the function; without it, everything leaks into the script.
- return
  only sets an exit code (0 to 255). To hand back data,
  echo
  it and capture with
  out=\$(deploy web1)
  .
- Define a function before its first call; bash reads top to bottom.

## Running Scripts

[TABLE]

"command not found" for a script sitting right in front of you is the missing ./. The current directory is not on PATH, so bash never looks there.

## Script Arguments

[TABLE]

Flag parsing with the getopts builtin:

```
while getopts "f:v" opt; do
  case "$opt" in
    f) file="$OPTARG" ;;
    v) verbose=1 ;;
    *) echo "usage: $0 [-v] [-f file]" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))   # what remains is in "$@"
```

Copy

## Windows Equivalents

For moving between a Linux box and a Windows one. Windows PowerShell 5.1 aliases the short names (ls, cp, cat); PowerShell 7 on Linux and macOS drops those aliases so the real commands still work.

| Bash | PowerShell | CMD |
|----|----|----|
| ls | Get-ChildItem | dir |
| pwd | Get-Location | cd |
| cd dir | Set-Location dir | cd dir |
| cp a b | Copy-Item a b | copy a b |
| mv a b | Move-Item a b | move a b |
| rm -r dir | Remove-Item -Recurse dir | rmdir /s dir |
| cat file | Get-Content file | type file |
| grep pattern file | Select-String pattern file | findstr pattern file |
| find . -name "\*.log" | Get-ChildItem -Recurse -Filter \*.log | dir /s /b \*.log |
| which cmd | Get-Command cmd | where cmd |
| ps | Get-Process | tasklist |
| kill 1234 | Stop-Process -Id 1234 | taskkill /PID 1234 |
| export VAR=x | \$env:VAR = "x" | set VAR=x |
| echo "\$VAR" | \$env:VAR | echo %VAR% |
| curl url | Invoke-WebRequest url | curl.exe url |
| man cmd | Get-Help cmd | cmd /? |

Bash itself runs on Windows through WSL or Git Bash, which is usually easier than translating a script.

## Gotchas

- name = value
  is not an assignment; it runs a command called
  name
  . No spaces around
  =
  .
- An unquoted
  \$var
  splits on spaces and expands globs. Quote every expansion:
  "\$var"
  ,
  "\${arr\[@\]}"
  ,
  "\$@"
  .
- sh script.sh
  is not bash on Debian and Ubuntu;
  /bin/sh
  is dash there, and
  \[\[
  , arrays, and
  {1..5}
  all fail. Use a
  \#!/usr/bin/env bash
  shebang and run with
  bash
  .
- macOS ships bash 3.2 from 2007, so
  declare -A
  ,
  \${var^^}
  , and
  mapfile
  fail on a Mac. The macOS default shell is [zsh](https://sshworkbench.com/cheatsheets/zsh) now; a current bash comes from Homebrew.
- cat file \| while read
  runs the loop in a subshell, so variables set inside it vanish afterwards. Feed the loop with
  done \< file
  instead.
- rm -rf "\$dir/"\*
  with an unset
  \$dir
  expands to
  /\*
  .
  set -u
  at the top turns that typo into an error instead of a disaster.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## Bash FAQ

### Are bash commands the same as Linux commands?

Mostly, which is why the two cheat sheets blur together. Commands like ls, grep, and ssh are separate programs that bash merely runs, and they work the same from zsh or any other shell. What actually belongs to bash is the syntax around them: variables, \[\[ \]\] tests, loops, redirection, and builtins like cd, export, and alias. Type ls into any Linux shell and it works; write a script full of \[\[ \]\] and arrays and it only runs under bash.

### What is the difference between sh and bash?

sh is the POSIX shell specification; bash is one implementation of it plus a lot of extras: \[\[ \]\], arrays, \${var//old/new} expansions, brace ranges like {1..10}, and =~ regex matching. On Debian and Ubuntu, /bin/sh points at dash, a minimal shell, so running sh script.sh or using \#!/bin/sh strips the bash extras and you get errors like "\[\[: not found". If a script uses anything from this page beyond plain commands and pipes, start it with \#!/usr/bin/env bash and run it with bash.

### How do I check if a file exists in bash?

\[\[ -f /path/file \]\] is true for a regular file, \[\[ -d /path \]\] for a directory, and \[\[ -e /path \]\] for anything at that path. Negate with an exclamation mark: \[\[ ! -f config \]\] && cp default config. Two traps: quote the variable, \[\[ -f "\$file" \]\], so paths with spaces work, and remember -f follows symlinks, so a link pointing at a deleted file tests false. In a script that must also run under plain sh, use \[ -f file \] or test -f file instead.

### Can a bash function return a value?

Not the way other languages do. return only sets an exit code, a number from 0 to 255, and anything larger wraps around, so return 300 comes back as 44. To hand back data, echo it and capture the call: out=\$(myfunc). That runs the function in a subshell, so any variable it sets is gone afterwards. When you need both a value and side effects, assign to a variable the caller already knows about, or take the name as an argument and use declare -n ref="\$1" to write through it, which is a bash 4.3 feature. Checking a function with if myfunc; then uses its exit code, not its output.

### Should bash variables be uppercase?

Bash does not care, but the convention exists for a good reason. Uppercase is for environment variables and things you export, since that is the namespace PATH, HOME, EDITOR and every other system variable lives in. Lowercase is for variables local to your script, which keeps you from quietly overwriting something the system needs. Naming a loop counter PATH really will break the rest of the script. Bash also has read-only names such as UID, BASH_VERSION and RANDOM that fail to assign. Only letters, digits and underscores are allowed, and a name cannot start with a digit.

---
Källa: https://sshworkbench.com/cheatsheets/bash
