# sed Examples

sed edits text as it streams through a pipe or over a file: replace, delete, insert, print. Every example here is paste-ready, and the macOS differences that break sed -i for Mac users get their own section.

Last updated September 11, 2026

On this page

- [Replace Text](#replace-text)
- [Edit Files In Place](#edit-files-in-place)
- [sed on macOS](#sed-on-macos)
- [Multiple Files](#multiple-files)
- [Delete Lines](#delete-lines)
- [Print Lines (-n and p)](#print-lines--n-and-p)
- [Insert and Append](#insert-and-append)
- [Regex and Capture Groups](#regex-and-capture-groups)
- [Multiple Commands](#multiple-commands)
- [Variables and Special Characters](#variables-and-special-characters)
- [Options](#options)
- [Command Letters](#command-letters)
- [sed on Windows](#sed-on-windows)
- [Gotchas](#gotchas)

## Replace Text

The substitute command is most of what sed gets used for. s/old/new/ replaces the first occurrence on each line; g makes it every occurrence.

[TABLE]

## Edit Files In Place

Without -i, sed prints the result and leaves the file alone. That is the safe way to test an expression first.

-i is the one flag that is not portable, and it is the single most common reason a sed command fails. GNU sed on Linux takes sed -i 's/a/b/' file. BSD sed on macOS reads that s/a/b/ as a backup filename extension and stops with invalid command code or undefined label; it needs an empty argument, sed -i '' 's/a/b/' file. Only -i.bak runs unchanged on both.

[TABLE]

## sed on macOS

macOS ships BSD sed, and the biggest difference is -i: BSD requires a backup extension argument, GNU does not. sed -i 's/a/b/' file on a Mac fails with "invalid command code" or "undefined label" because s/a/b/ gets read as the backup extension.

[TABLE]

Other BSD gaps to know: no I case-insensitive flag, and i\\a\\ insert text needs a real newline after the backslash. -E for extended regex works on both.

## Multiple Files

sed takes as many files as you give it, but -i rewrites every one of them. Run the command without -i on a single file first.

[TABLE]

Recursion is the caller's job: sed itself has no -r recursive flag (-r means extended regex). Filtering with grep -rl first also keeps the mtime of files that did not match.

## Delete Lines

[TABLE]

## Print Lines (-n and p)

-n turns off the default print-every-line behaviour, so p prints only what you select.

[TABLE]

## Insert and Append

i inserts before a line, a appends after it, c replaces it entirely.

| Command | What it does |
|----|----|
| sed '1i header line' file | Insert a line at the top (GNU syntax) |
| sed '\$a footer line' file | Append a line at the end |
| sed '/\\section\\/a key=value' conf | Add a line after each match |
| sed '/\\section\\/i \# added by script' conf | Add a line before each match |
| sed '/^listen/c listen 8080;' nginx.conf | Replace the whole matching line |
| sed '3a inserted after line 3' file | Append after a specific line number |

BSD/macOS sed wants a backslash and a literal newline after i\\ a\\ and c\\ the one-line GNU forms above fail there. Use gsed, or:

```
sed -i '' '1i\
header line
' file
```

Copy

## Regex and Capture Groups

sed's default dialect is basic regex (BRE): groups and +/? need backslashes. -E switches to extended regex and works on both GNU and BSD sed (-r is the older GNU spelling).

[TABLE]

sed has no \d or \s in any dialect: use \[0-9\] and \[\[:space:\]\]. .\* is greedy and there are no lazy quantifiers, so match "up to the next X" with \[^X\]\*.

## Multiple Commands

[TABLE]

sed works line by line, so a plain s/\n/ / never matches. The classic join-all-lines one-liner pulls the file into the buffer first (GNU sed):

```
sed ':a;N;$!ba;s/\n/ /g' file
```

Copy

For simple newline jobs, tr '\n' ' ' \< file or paste -sd' ' file is easier to read.

## Variables and Special Characters

[TABLE]

## Options

The shape is sed \[options\] 'script' file. Everything else is a command letter inside the script.

[TABLE]

## Command Letters

[TABLE]

l is the quickest way to see a stray carriage return or a tab that a pattern keeps missing.

## sed on Windows

Windows has no built-in sed. Git Bash and WSL both ship GNU sed, so Linux syntax works as written; sed: command not found means the shell is cmd or PowerShell rather than one of those.

[TABLE]

Carriage returns are the usual reason a pattern anchored with \$ matches nothing on a file that came from Windows.

## Gotchas

- sed -i
  needs
  -i ''
  on macOS and plain
  -i
  on Linux.
  -i.bak
  is the only spelling that works on both unchanged.
  invalid command code
  and
  undefined label
  on a Mac are almost always this.
- command a expects \\ followed by text
  is BSD sed refusing the one-line GNU
  a
  ,
  i
  and
  c
  forms. Add the backslash and a real newline, or use
  gsed
  .
- extra characters after command
  usually means the delimiter also appears inside your pattern or replacement, or the expression reached sed unquoted.
- No
  \d
  , no
  \s
  , no lazy
  .\*?
  in sed regex, in any version. Use
  \[0-9\]
  ,
  \[\[:space:\]\]
  , and
  \[^x\]\*
  .
- An unescaped
  &
  in the replacement inserts the whole match. This bites when the replacement is a shell variable containing
  &
  .
- Prefer
  -E
  over
  -r
  for extended regex: GNU sed takes both, BSD sed only
  -E
  .
- Single-quote sed expressions unless you need a variable expanded. Inside double quotes the shell eats backslashes and
  \$
  before sed sees them.
- grep answers "which lines", sed rewrites them, awk works per column. See the [grep cheat sheet](https://sshworkbench.com/cheatsheets/grep) and [awk cheat sheet](https://sshworkbench.com/cheatsheets/awk).

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## sed FAQ

### Why does sed -i not work on macOS?

macOS ships BSD sed, where -i requires a backup extension as an argument. GNU sed accepts sed -i 's/a/b/' file, but on a Mac that reads s/a/b/ as the backup extension and fails with an 'undefined label' or 'invalid command code' error. Write sed -i '' 's/a/b/' file on macOS (empty string means no backup). The form that works on both is sed -i.bak 's/a/b/' file, deleting the .bak after. Or brew install gnu-sed and use gsed with the Linux syntax.

### Why is my sed command not replacing text in the file?

Usually the file was never written. Without -i, sed prints the result to the terminal and leaves the file alone, so check that flag first; on macOS it has to be -i '' or the expression is eaten as a backup extension. If the command runs clean but matches nothing, the pattern is the problem: . \* \[ \] and the delimiter itself are regex, so a literal dot or slash needs escaping. A file saved on Windows ends every line with a carriage return, which is why patterns anchored with \$ silently fail; run sed -i 's/\r\$//' file first. One more: sed -i writes a temp file and renames it over the original, so an editor that still has the old version open can save it straight back over your change.

### How do I use a variable in a sed command?

Switch to double quotes so the shell expands it: sed "s/localhost/\$HOST/g" config. Two things break this: a slash inside the variable ends the pattern early, so use another delimiter (sed "s\|/var/www\|\$DOCROOT\|g"), and an & or \\ in the variable is interpreted by sed itself. For variables you control, that is fine; for arbitrary input, escape it first or reach for awk -v, which passes variables without re-parsing them.

### How do I replace a string that contains slashes?

Use a different delimiter; sed accepts almost any character after the s. sed 's\|/var/www\|/srv/http\|g' and sed 's#http://#https://#g' both work with no escaping. The alternative is escaping every slash (s//var/www/... ), which is unreadable. Regex specials like . \* \[ \] still need a backslash regardless of delimiter, since only the delimiter changes.

### How do I replace a string in multiple files at once?

Glob when the files are in one directory: sed -i 's/old/new/g' \*.conf. Across a tree, let grep find the files and xargs feed them to sed: grep -rl 'old' src/ \| xargs sed -i 's/old/new/g'. This touches only files that actually match, which keeps timestamps honest. On macOS add the empty backup argument: xargs sed -i '' 's/old/new/g'. Test the expression on one file before running it over hundreds.

---
Källa: https://sshworkbench.com/cheatsheets/sed
