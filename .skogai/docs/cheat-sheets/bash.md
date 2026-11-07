# Bash Cheat Sheet

Bash is the default shell on most Linux servers, so half of any bash cheat sheet is just Linux commands. This sheet covers both sides: the commands you type at the prompt and the syntax that only matters in scripts, from test operators to arrays and parameter expansion.

## Navigation

| Command | What it does |
|---|---|
| `pwd` | Print working directory |
| `cd /path` | Change directory |
| `cd` or `cd ~` | Change to home directory |
| `cd ..` | Move up one directory level |
| `cd -` | Switch to previous working directory |
| `pushd /path` | Save current directory to stack and move to `/path` |
| `popd` | Pop directory from stack and return to it |
| `dirs -v` | Display directory stack with index numbers |

## File Commands

| Command | What it does |
|---|---|
| `ls -la` | List all files in long format including hidden files |
| `cp -r src/ dest/` | Copy files or directories recursively |
| `mv src dest` | Move or rename file or directory |
| `rm -rf dir/` | Forcefully remove files and directories recursively |
| `mkdir -p path/to/dir` | Create directories recursively including parents |
| `touch file` | Create empty file or update timestamp |
| `stat file` | Display detailed file status and metadata |

## Networking

Not bash itself, but the commands every bash cheat sheet gets used for on a server.

| Command | What it does |
|---|---|
| `ip a` | Show network interfaces and assigned IP addresses |
| `ss -tulpn` | List listening TCP/UDP sockets with process info |
| `ping -c 4 host` | Send 4 ICMP echo requests to test reachability |
| `curl -I https://example.com` | Fetch HTTP headers from URL |
| `dig example.com` | Query DNS records for a domain |

## Jobs and Processes

| Command / Shortcut | What it does |
|---|---|
| `Ctrl+Z` | Suspend current foreground process |
| `jobs` | List active background jobs for current shell |
| `bg %1` | Resume suspended job in background |
| `fg %1` | Bring background job into foreground |
| `kill %1` | Terminate background job number 1 |
| `kill -9 <PID>` | Force kill process by PID (SIGKILL) |
| `nohup cmd &` | Run command immune to hangups (survives shell exit) |

If exit answers "There are stopped jobs", run jobs to see them, then fg to finish each one or kill %1 to drop it. A second exit leaves anyway and kills them.

## Variables

No spaces around the equals sign, and quote expansions unless you want word splitting.

| Syntax | What it does |
|---|---|
| `NAME="value"` | Set local shell variable (no spaces around `=`) |
| `export NAME="value"` | Export variable to environment of child processes |
| `readonly NAME="value"` | Mark variable as read-only (cannot be reassigned) |
| `unset NAME` | Unset and delete variable |
| `env` | Print all exported environment variables |

## If and Test Operators

Use [[ ]] in bash: it is safer with unquoted variables than [ ] and adds glob and regex matching.

```
if [[ -f "$conf" ]]; then
  echo "found"
elif [[ -d /etc/nginx ]]; then
  echo "directory only"
else
  echo "missing"
fi
```

| Test Operator | Meaning |
|---|---|
| `[[ -f file ]]` | True if file exists and is a regular file |
| `[[ -d dir ]]` | True if path exists and is a directory |
| `[[ -e path ]]` | True if path exists (any type) |
| `[[ -s file ]]` | True if file exists and has size greater than zero |
| `[[ -r / -w / -x file ]]` | True if file is readable / writable / executable |
| `[[ -z "$str" ]]` | True if string is empty (length zero) |
| `[[ -n "$str" ]]` | True if string is not empty |
| `[[ "$a" == "$b" ]]` | String equality test (supports glob pattern on right) |
| `[[ "$a" =~ regex ]]` | Extended regular expression match |
| `[[ $n -eq $m ]]` | Numeric equality (`-ne`, `-lt`, `-le`, `-gt`, `-ge`) |

Combine with && and \|\| inside [[ ]], negate with !.

## Case Statements

Cleaner than a stack of elif when one value has several possible shapes.

```bash
case "$1" in
  start)          systemctl start app ;;
  stop)           systemctl stop app ;;
  restart|reload) systemctl restart app ;;   # | separates alternatives
  *.log)          echo "that is a log file" ;;
  "")             echo "no argument given" ;;
  *)              echo "usage: $0 {start|stop|restart}" >&2; exit 2 ;;
esac
```

- The patterns are globs, not regex, and the first match wins, so *) goes last as the catch-all.
- ;; ends a branch.;& falls straight into the next branch,;;& carries on testing the remaining patterns (bash 4+).
- shopt -s nocasematch makes the matching case-insensitive.

## Loops

```bash
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

break leaves the loop, continue skips to the next round.

## Arrays

Indexed from 0, and "${arr[@]}" must be quoted or elements with spaces split apart.

```bash
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

## Parameter Expansion

String surgery without spawning sed. The keyboard is the mnemonic for the confusing pair: \# sits left of $ and cuts from the front, % sits right of it and cuts from the back. One symbol takes the shortest match, doubled takes the longest. The patterns are globs, not regex.

| Syntax | Meaning |
|---|---|
| `${var:-default}` | If `var` is unset or null, return `default` |
| `${var:=default}` | If `var` is unset or null, set `var` to `default` and return it |
| `${var:?error}` | If `var` is unset or null, print `error` and abort script |
| `${#var}` | Length of string value in characters |
| `${var#prefix}` | Remove shortest match of `prefix` from start |
| `${var##prefix}` | Remove longest match of `prefix` from start |
| `${var%suffix}` | Remove shortest match of `suffix` from end |
| `${var%%suffix}` | Remove longest match of `suffix` from end |
| `${var/find/replace}` | Replace first occurrence of `find` with `replace` |
| `${var//find/replace}` | Replace all occurrences of `find` with `replace` |

## Arithmetic

Integers only. Bash cannot do decimals on its own.

| Syntax | What it does |
|---|---|
| `$((a + b))` | Addition |
| `$((a - b))` | Subtraction |
| `$((a * b))` | Multiplication |
| `$((a / b))` | Integer division (truncates decimals) |
| `$((a % b))` | Modulo (remainder) |
| `$((a ** b))` | Exponentiation |
| `((count++))` | Increment variable in place (arithmetic command) |

$(( )) is arithmetic, $( ) runs a command. A stray space between the parentheses changes which one you get.

## Globbing

Bash expands these before the command ever runs, so rm *.log is the shell handing rm a list of names.

| Glob Pattern | Meaning |
|---|---|
| `*` | Matches any string of characters (skips hidden dotfiles) |
| `?` | Matches any single character |
| `[abc]` | Matches any character enclosed in brackets |
| `[a-z0-9]` | Matches character range |
| `**` | Recursive directory globbing (requires `shopt -s globstar`) |
| `!(pattern)` | Negative match (requires `shopt -s extglob`) |

Quote the pattern when the command should do its own matching: find . -name "*.log" and rsync --exclude '*.tmp' both want the pattern intact, not a list of files the shell already expanded.

## Redirection and Pipes

| Operator | Meaning |
|---|---|
| `cmd > file` | Redirect standard output (stdout) to file (overwrites) |
| `cmd >> file` | Append standard output to file |
| `cmd 2> file` | Redirect standard error (stderr) to file |
| `cmd 2>&1` | Redirect standard error into standard output |
| `cmd &> file` | Redirect both stdout and stderr to file |
| `cmd < file` | Feed file content into standard input (stdin) |
| `cmd1 \| cmd2` | Pipe stdout of `cmd1` into stdin of `cmd2` |
| `cmd1 \|& cmd2` | Pipe both stdout and stderr of `cmd1` into `cmd2` |

Multi-line input goes through a heredoc; quote the delimiter (<<'EOF') to stop expansion inside it.

```
cat > /etc/motd <<EOF
Welcome to $(hostname)
EOF
```

## Command Substitution

| Syntax | What it does |
|---|---|
| `$(command)` | Execute command and substitute standard output (recommended) |
| `` `command` `` | Older backtick syntax for command substitution |
| `$(<file)` | Fast bash built-in equivalent to `$(cat file)` |

$( ) nests cleanly, as in $(basename "$(pwd)"). Backticks do the same job but are the legacy form.

## Reading Input

Always pass -r, or read eats backslashes in the input.

| Command | What it does |
|---|---|
| `read var` | Read single line of user input into variable `var` |
| `read -p "Prompt: " var` | Display prompt message before reading input |
| `read -s -p "Password: " pw` | Read input silently without echoing characters (passwords) |
| `read -r line` | Raw input mode (prevents backslash escapes from being parsed) |
| `read -a myarray` | Read input fields into an array |

A yes/no prompt, defaulting to no:

```
read -rp "Deploy to production? [y/N] " ans
[[ "$ans" == [yY]* ]] || exit 0
```

Prompting inside a while read ... done < file loop does not work: the loop already owns stdin, so the prompt reads the next line of the file. Add < /dev/tty to the inner read.

## Keyboard Shortcuts

Bash line editing is readline; these work in any readline program, psql and python included.

| Keybinding | Action |
|---|---|
| `Ctrl+A` | Move cursor to start of line |
| `Ctrl+E` | Move cursor to end of line |
| `Ctrl+U` | Cut/erase from cursor to start of line |
| `Ctrl+K` | Cut/erase from cursor to end of line |
| `Ctrl+W` | Cut/erase word before cursor |
| `Ctrl+Y` | Paste (yank) previously cut text |
| `Ctrl+L` | Clear terminal screen |
| `Ctrl+C` | Send SIGINT to abort current command |
| `Ctrl+D` | Send EOF / exit shell |

## Vi Mode

The table above is emacs mode, the bash default. set -o vi swaps it for vi keys; put it in ~/.bashrc, or set editing-mode vi in ~/.inputrc to change every readline program at once. You start in insert mode, so press Esc first.

| Key (Normal Mode) | Action |
|---|---|
| `set -o vi` | Turn on vi editing mode in bash |
| `Esc` | Enter Normal mode |
| `i` / `a` | Enter Insert mode (before / after cursor) |
| `h / j / k / l` | Move cursor left / down / up / right |
| `w / b` | Jump forward / backward by word |
| `0 / $` | Jump to beginning / end of line |
| `dd` | Delete entire line |
| `yy / p` | Yank (copy) line / put (paste) line |

Ctrl+R and Ctrl+C still work from insert mode, so history search does not go away.

## History

| Command / Expansion | What it does |
|---|---|
| `history` | List command history with line numbers |
| `!$` | Expand to last argument of previous command |
| `!^` | Expand to first argument of previous command |
| `!!` | Repeat the previous command |
| `!n` | Repeat command number `n` from history |
| `!-n` | Repeat command `n` lines back |
| `Ctrl+R` | Incremental reverse history search |

Worth setting in ~/.bashrc:

```
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTTIMEFORMAT='%F %T '
export HISTCONTROL=ignoredups:ignorespace  # skip duplicates; a leading space hides a command
```

## Startup Files

| File | When it runs | Purpose |
|---|---|---|
| `/etc/profile` | Login shell | System-wide environment initialization |
| `~/.bash_profile` | Login shell | User-specific environment and startup commands |
| `~/.bash_login` | Login shell | Used if `~/.bash_profile` is absent |
| `~/.profile` | Login shell | Used if both bash-specific login files are absent |
| `~/.bashrc` | Interactive non-login shell | User aliases, functions, prompt, and shell config |
| `~/.bash_logout` | Login shell exit | User cleanup commands executed upon exit |

- A login shell does not read ~/.bashrc. That is why most ~/.bash_profile files contain [[ -f ~/.bashrc ]] && . ~/.bashrc, and why a PATH you set in one file is missing in the other.
- These files are sourced, not executed, so they need no chmod +x and no shebang.
- ssh host 'command' starts a non-interactive shell. Bash does read ~/.bashrc there, but most distro copies open with a line that returns early when the shell is not interactive, so anything below it never applies to remote commands.
- A prompt that redraws over itself usually means unescaped colour codes in PS1. Wrap every escape sequence in \\ and \\ so bash does not count it towards the line width.

## Exit Codes

| Command | What it does |
|----|----|
| echo $? | Exit code of the last command; 0 means success |
| cmd && next | Run next only if cmd succeeded |
| cmd \|\| fallback | Run fallback only if cmd failed |
| exit 1 | Leave the script with that code |
| set -e | Stop the script at the first failing command |
| set -u | Treat unset variables as errors |
| set -o pipefail | A pipeline fails if any stage fails, not just the last |
| set -euo pipefail | All three; the usual first line after the shebang |
| trap 'rm -f "$tmp"' EXIT | Run cleanup when the script exits, however it exits |

Codes worth recognising: 126 found but not executable, 127 command not found, 130 killed with Ctrl+C, and 128+N killed by signal N.

## Regex

[[ =~ ]] matches POSIX extended regex; capture groups land in BASH_REMATCH.

```
re='^([0-9]+)\.([0-9]+)'
if [[ $version =~ $re ]]; then
  major="${BASH_REMATCH[1]}"
  minor="${BASH_REMATCH[2]}"
fi
```

- Keep the pattern in a variable and unquoted after =~; quoting it makes bash match the text literally.
- POSIX extended regex has no \d, \w or \s. Write [0-9], [[:alnum:]] and [[:space:]] instead.
- BASH_REMATCH is overwritten by the next =~, so copy what you need straight away.
- case statements and [[ == ]] use globs ( *,?, [a-z]), not regex.
- To match inside files use [grep](https://sshworkbench.com/cheatsheets/grep); to edit with a pattern use [sed](https://sshworkbench.com/cheatsheets/sed).

## Functions

```bash
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

- local keeps a variable inside the function; without it, everything leaks into the script.
- return only sets an exit code (0 to 255). To hand back data, echo it and capture with out=$(deploy web1).
- Define a function before its first call; bash reads top to bottom.

## Running Scripts

| Invocation | What it does |
|---|---|
| `./script.sh` | Execute script using kernel shebang (`#!/bin/bash`) |
| `bash script.sh` | Run script inside a subshell (no execute bit needed) |
| `source script.sh` | Run script inside the current shell environment (`. script.sh`) |
| `bash -x script.sh` | Run script in debug mode, printing each executed command |
| `bash -n script.sh` | Syntax-check script without executing any commands |

"command not found" for a script sitting right in front of you is the missing ./. The current directory is not on PATH, so bash never looks there.

## Script Arguments

| Variable | Meaning |
|---|---|
| `$0` | Script name / invocation path |
| `$1` .. `$9` | Positional arguments 1 through 9 |
| `${10}` | Positional argument 10 and beyond (braces required) |
| `$#` | Number of positional arguments passed |
| `$@` | All positional arguments as separate quoted words (`"$1" "$2" ...`) |
| `$*` | All positional arguments joined as single string (`"$1 $2 ..."`) |
| `$$` | Process ID (PID) of current shell script |
| `$?` | Exit status code of most recently executed command |
| `shift` | Shift positional arguments down by one (`$2` becomes `$1`) |

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
| find . -name "*.log" | Get-ChildItem -Recurse -Filter *.log | dir /s /b *.log |
| which cmd | Get-Command cmd | where cmd |
| ps | Get-Process | tasklist |
| kill 1234 | Stop-Process -Id 1234 | taskkill /PID 1234 |
| export VAR=x | $env:VAR = "x" | set VAR=x |
| echo "$VAR" | $env:VAR | echo %VAR% |
| curl url | Invoke-WebRequest url | curl.exe url |
| man cmd | Get-Help cmd | cmd /? |

Bash itself runs on Windows through WSL or Git Bash, which is usually easier than translating a script.

## Gotchas

- name = value is not an assignment; it runs a command called name. No spaces around =.
- An unquoted $var splits on spaces and expands globs. Quote every expansion: "$var", "${arr[@]}", "$@".
- sh script.sh is not bash on Debian and Ubuntu; /bin/sh is dash there, and [[, arrays, and {1..5} all fail. Use a \#!/usr/bin/env bash shebang and run with bash.
- macOS ships bash 3.2 from 2007, so declare -A, ${var^^}, and mapfile fail on a Mac. The macOS default shell is [zsh](https://sshworkbench.com/cheatsheets/zsh) now; a current bash comes from Homebrew.
- cat file \| while read runs the loop in a subshell, so variables set inside it vanish afterwards. Feed the loop with done < file instead.
- rm -rf "$dir/"* with an unset $dir expands to /*. set -u at the top turns that typo into an error instead of a disaster.

## Bash FAQ

### Are bash commands the same as Linux commands?

Mostly, which is why the two cheat sheets blur together. Commands like ls, grep, and ssh are separate programs that bash merely runs, and they work the same from zsh or any other shell. What actually belongs to bash is the syntax around them: variables, [[ ]] tests, loops, redirection, and builtins like cd, export, and alias. Type ls into any Linux shell and it works; write a script full of [[ ]] and arrays and it only runs under bash.

### What is the difference between sh and bash?

sh is the POSIX shell specification; bash is one implementation of it plus a lot of extras: [[ ]], arrays, ${var//old/new} expansions, brace ranges like {1..10}, and =~ regex matching. On Debian and Ubuntu, /bin/sh points at dash, a minimal shell, so running sh script.sh or using \#!/bin/sh strips the bash extras and you get errors like "[[: not found". If a script uses anything from this page beyond plain commands and pipes, start it with \#!/usr/bin/env bash and run it with bash.

### How do I check if a file exists in bash?

[[ -f /path/file ]] is true for a regular file, [[ -d /path ]] for a directory, and [[ -e /path ]] for anything at that path. Negate with an exclamation mark: [[ ! -f config ]] && cp default config. Two traps: quote the variable, [[ -f "$file" ]], so paths with spaces work, and remember -f follows symlinks, so a link pointing at a deleted file tests false. In a script that must also run under plain sh, use [ -f file ] or test -f file instead.

### Can a bash function return a value?

Not the way other languages do. return only sets an exit code, a number from 0 to 255, and anything larger wraps around, so return 300 comes back as 44. To hand back data, echo it and capture the call: out=$(myfunc). That runs the function in a subshell, so any variable it sets is gone afterwards. When you need both a value and side effects, assign to a variable the caller already knows about, or take the name as an argument and use declare -n ref="$1" to write through it, which is a bash 4.3 feature. Checking a function with if myfunc; then uses its exit code, not its output.

### Should bash variables be uppercase?

Bash does not care, but the convention exists for a good reason. Uppercase is for environment variables and things you export, since that is the namespace PATH, HOME, EDITOR and every other system variable lives in. Lowercase is for variables local to your script, which keeps you from quietly overwriting something the system needs. Naming a loop counter PATH really will break the rest of the script. Bash also has read-only names such as UID, BASH_VERSION and RANDOM that fail to assign. Only letters, digits and underscores are allowed, and a name cannot start with a digit.

---
Source: https://sshworkbench.com/cheatsheets/bash
