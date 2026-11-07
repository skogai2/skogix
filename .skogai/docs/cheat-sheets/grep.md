# grep Command Examples

grep prints the lines that match a pattern, from files or from whatever you pipe into it. The examples here cover the everyday flags, recursive search, regex, logs and processes, compressed files, and what to use instead on Windows.

## Syntax

Options can come before or after the pattern. With more than one file, grep prefixes every output line with the file name.

```bash
grep [options] PATTERN [file ...]
```

| Exit code | Meaning                                                   |
|-----------|-----------------------------------------------------------|
| 0         | At least one line matched                                 |
| 1         | Nothing matched                                           |
| 2         | An error: missing file, unreadable directory, bad pattern |

## The Basics

| Command | What it does |
|---|---|
| `grep "pattern" file` | Search file for lines containing pattern |
| `grep -i "pattern" file` | Case-insensitive search |
| `grep -v "pattern" file` | Invert match: print lines that do NOT match pattern |
| `grep -r "pattern" dir/` | Search recursively through directory |
| `grep -n "pattern" file` | Prefix each matching line with its line number |
| `grep -c "pattern" file` | Output count of matching lines only |
| `grep -l "pattern" *` | List only names of files that contain matches |
| `grep -w "word" file` | Match whole words only |

## Recursive Search

--exclude-dir matches each directory's basename, not its path, so one name skips it everywhere in the tree.

| Command | What it does |
|----|----|
| grep -r "api_key" . | Search every file under the current directory |
| grep -rn "api_key" src/ | Recursive with file name and line number |
| grep -ri "todo" . | Recursive, case insensitive |
| grep -rl "old_name" . | Just the file names (feeds nicely into xargs) |
| grep -r "text" . --include="*.py" | Only search .py files |
| grep -r "text" . --exclude="*.min.js" | Skip minified files |
| grep -r "text" . --exclude-dir=node_modules | Skip a directory |
| grep -r "text" . --exclude-dir={.git,node_modules,dist} | Skip several directories |
| grep -R "text" . | Like -r, but also follows symlinks |

## Multiple Patterns

| Command | What it does |
|----|----|
| grep -e "error" -e "warn" app.log | OR: match either pattern |
| grep -E "error\|warn\|fatal" app.log | OR with extended regex |
| grep -f patterns.txt app.log | Read patterns from a file, one per line |
| grep "error" app.log \| grep "nginx" | AND: lines containing both |
| grep "error" app.log \| grep -v "timeout" | Match one, exclude another |
| grep -v -e "debug" -e "trace" app.log | Exclude several patterns |
| grep -c -e "GET" -e "POST" access.log | Count lines matching either |
| grep -Fxf old.txt new.txt | Lines that appear in both files |
| grep -Fxvf old.txt new.txt | Lines in new.txt that are not in old.txt |

## Counting Matches

| Command | What it does |
|----|----|
| grep -c "error" app.log | Count matching lines |
| grep -o "error" app.log \| wc -l | Count occurrences, including several per line |
| grep -vc "debug" app.log | Count the lines that do not match |
| grep -rc "TODO" src/ | Per-file counts across a tree |
| grep -rc "TODO" src/ \| grep -v ":0$" | Same, hiding files with no matches |
| grep -oE "[0-9.]+" ips.txt \| sort \| uniq -c \| sort -rn | Rank the distinct matches by frequency |

-c counts lines, not matches: a line with three hits still counts as one. Use -o piped into wc -l when you need the real total.

## Regex

grep's default dialect is basic regex (BRE). Add -E for extended regex (ERE), where +, ?, \|, () and {} work without backslashes. -E works on every grep, including macOS.

| Pattern / Flag | Syntax Example | Description |
|---|---|---|
| Extended Regex | `grep -E "foo\|bar"` | Enable ERE (supports `\|`, `+`, `?`, `()`) |
| Perl Regex | `grep -P "\d{3}-\d{2}"` | Enable PCRE (supports `\d`, `\w`, `\s`) |
| Line Start | `grep "^Error"` | Match only at the beginning of a line |
| Line End | `grep "failed$"` | Match only at the end of a line |
| Any Character | `grep "c.t"` | Match any single character |
| Character Class | `grep "[0-9]"` | Match any digit character in bracket |

With -E:

| Pattern | Matches |
|----|----|
| -E "go+gle" | One or more: gogle, google, gooogle |
| -E "colou?r" | Optional: color and colour |
| -E "error\|warn" | Alternation |
| -E "(ab)+" | Grouping: ab, abab |
| -E "[0-9]{1,3}\\[0-9]{1,3}" | Repetition counts (start of an IP address) |

grep -P unlocks Perl regex (\d, \s, lookaheads) but only exists in GNU grep. The grep on macOS and BSD does not have it: use -E with POSIX classes, or brew install grep and call ggrep.

## Context Lines

| Command                      | What it does                     |
|------------------------------|----------------------------------|
| grep -A 3 "error" app.log    | Show 3 lines After each match    |
| grep -B 3 "error" app.log    | Show 3 lines Before each match   |
| grep -C 3 "error" app.log    | 3 lines of Context on both sides |
| grep -n -C 2 "panic" app.log | Context plus line numbers        |

Groups of matches are separated by a -- line. Nearby matches merge into one block.

## Pipes and xargs

grep is at its best at the end of a pipe. See the [awk cheat sheet](https://sshworkbench.com/cheatsheets/awk) for what usually comes after it.

| Command | What it does |
|---|---|
| `ps aux \| grep nginx` | Pipe command output into grep |
| `grep -rl "old_api" . \| xargs sed -i 's/old_api/new_api/g'` | Find files and pass to sed |
| `grep -rlZ "pattern" . \| xargs -0 rm` | Safely handle filenames with spaces using null delimiter |

## Searching Logs

| Command | What it does |
|---|---|
| `zgrep "500 Internal" /var/log/nginx/access.log*.gz` | Search directly inside gzipped log files |
| `grep -C 3 "NullPointerException" app.log` | Print 3 lines of context around each match |
| `grep -A 5 "Exception" app.log` | Print 5 lines after each match |
| `grep -B 2 "Error" app.log` | Print 2 lines before each match |

For a real range between two timestamps, awk '/08:15:00/,/09:30:00/' app.log is the better tool. See the [awk cheat sheet](https://sshworkbench.com/cheatsheets/awk).

## Compressed Files

| Command | What it does |
|----|----|
| zgrep "error" app.log.1.gz | Search a gzipped file without unpacking it |
| zgrep -i "error" /var/log/syslog* | Rotated logs, plain and gzipped in one pass |
| zgrep -c "error" app.log.1.gz | Count inside a compressed file |
| zcat app.log.1.gz \| grep "error" | The same thing by hand |
| bzgrep "error" app.log.bz2 | bzip2 archives |
| xzgrep "error" app.log.xz | xz archives |
| tar -xzOf logs.tar.gz \| grep "error" | Stream a tarball's contents through grep (see [tar](https://sshworkbench.com/cheatsheets/tar)) |
| unzip -p archive.zip \| grep "error" | Search the text inside a zip |

zgrep takes the same flags as grep, so -r, -i and -n all carry over.

## grep on Windows

Windows has no grep built in, but both shells have an equivalent.

| Tool / Command | Equivalent Grep Flag |
|---|---|
| `findstr /I "pattern" file` | Case-insensitive (`grep -i`) |
| `findstr /R "^Error" file` | Regex search (`grep -E`) |
| `findstr /S /M "word" *.*` | Recursive file list (`grep -rl`) |
| `Select-String -Pattern "regex" file` | PowerShell native cmdlet |

Git Bash and WSL both ship genuine GNU grep, so grep -rn "text" . works there unchanged.

## Alternatives to grep

grep is on every machine you will ever log into. These are faster in a large source tree, but you have to install them first.

| Tool | Command | Description |
|---|---|---|
| `ripgrep` | `rg "pattern"` | Extremely fast Rust-based tool that respects `.gitignore` |
| `ag` | `ag "pattern"` | The Silver Searcher (fast C-based grep replacement) |
| `ack` | `ack "pattern"` | Perl-based grep replacement for codebases |

## Gotchas

- -P is GNU-only. On macOS, grep -P '\d+' fails with "invalid option"; use grep -E '[0-9]+' or install GNU grep ( brew install grep, then ggrep).
- Always quote the pattern. Unquoted, the shell expands * and? against your files before grep ever sees them.
- grep exits 1 when nothing matches. In a script with set -e that kills the script; append \|\| true when no-match is fine.
- In basic regex, \+ and? are literal characters. grep "go+gle" matches the literal text go+gle; you want -E.
- "Binary file matches" means the file has non-text bytes. grep -a forces it to be treated as text, and -I skips binary files entirely during a recursive search.
- grep "error" with no file name is not hung, it is waiting on standard input. Ctrl+C out, then give it a file or a pipe.
- A file written on Windows ends each line with a carriage return, so grep "error$" finds nothing. Run dos2unix on it first.
- cat app.log \\ grep "error" works, but grep "error" app.log is one process instead of two and lets grep print the file name.
- grep finds lines, [sed](https://sshworkbench.com/cheatsheets/sed) edits them, and [awk](https://sshworkbench.com/cheatsheets/awk) works on columns. The three cover most text jobs between them.

## grep FAQ

### Why is the grep command called grep?

It is the name of a command in the old Unix line editor ed: g/re/p, which reads as "globally search for a regular expression and print the matching lines". Ken Thompson split that out into a standalone program in the early 1970s and the name stuck, first as a command and then as a verb. The behavior still matches the name, which is why grep prints whole lines by default and needs -o to print only the matched text.

### Is the grep command case sensitive?

Yes, by default. -i turns that off for the whole pattern, so grep -i error also matches Error and ERROR. When you only want part of the pattern relaxed, use a character class instead: grep -E "[Ee]rror: [0-9]+" keeps the digits strict. Case folding also follows your locale, so LC_ALL=C grep -i runs faster on large files but stops folding accented characters.

### Can the grep command be used with glob characters?

Not in the pattern. grep patterns are regular expressions, so * means "zero or more of the previous character" and ? is a literal question mark in the default dialect. The glob equivalent of * is .* in regex. Globs do work in the file list (grep error *.log, expanded by the shell before grep runs) and in --include and --exclude, which match shell-style globs against file names.

### Why is my grep command not working?

Four usual causes. The pattern was unquoted and the shell expanded it first. The pattern uses + or ?, which are literal characters until you add -E. The file came from Windows, so every line ends in a carriage return and anchors like error$ never match until you run dos2unix on it. Or the file is binary, so grep only prints "Binary file matches" until you add -a. "grep: command not found" is a different problem: the shell cannot find grep at all, which on Windows means you are not in Git Bash or WSL.

### Does Windows have a grep command?

There is no grep binary. cmd has findstr (findstr /S /I "error" *.log is roughly grep -ri), which works but has a narrow regex dialect; use /C:"two words" when the pattern contains spaces, since findstr otherwise treats each word as a separate pattern. PowerShell's Select-String is much closer to grep and takes full .NET regex, but it returns match objects, so pipe it through ForEach-Object Line when a script wants plain text. Git for Windows and WSL both ship genuine GNU grep.

---
Source: https://sshworkbench.com/cheatsheets/grep
