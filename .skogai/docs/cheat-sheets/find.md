# find Command in Linux

find walks a directory tree and matches files by name, type, size, age, owner, or permissions, then prints them or runs a command on them. This find command cheat sheet covers the tests and actions that come up in real work, with copy-paste examples.

## Basic Syntax

find <where> <tests> <action>. Tests combine left to right; the default action is -print. Always quote glob patterns so the shell does not expand them first.

| Command | What it does |
|----|----|
| find . | List everything under the current directory, recursively |
| find /var/log -name "*.log" | Files named *.log under /var/log |
| find . -iname "readme*" | Case-insensitive name match |
| find . -type f -name "*.conf" | Combine tests: files only, matching name |
| find /etc /opt -name "*.conf" | Search several trees at once |
| find . -name "*.py" 2>/dev/null | Hide Permission denied noise |

## Find by Name

| Command | What it does |
|---|---|
| `find . -name "*.log"` | Case-sensitive search for files matching wildcard pattern |
| `find . -iname "*.LOG"` | Case-insensitive search for files |
| `find /var/log -name "*.gz"` | Search inside specific directory tree |
| `find . -not -name "*.tmp"` | Negated match: find files not ending in `.tmp` |

The last row is the mistake everyone makes once. Unquoted, *.log becomes whatever matches in the current directory, so -name gets a real file name (or an error about too many arguments) instead of a pattern. Quote it: -name "*.log".

## Find by Type

| Type Code | Meaning | Command Example |
|---|---|---|
| `f` | Regular file | `find . -type f` |
| `d` | Directory | `find . -type d` |
| `l` | Symbolic link | `find . -type l` |
| `s` | Socket | `find /var/run -type s` |

## Excluding Directories

| Command | What it does |
|----|----|
| find . -name "*.js" -not -path "*/node_modules/*" | Filter results (still descends, simple) |
| find . -name node_modules -prune -o -name "*.js" -print | Skip the directory entirely (fast) |
| find . \\ -name node_modules -o -name .git \\ -prune -o -type f -print | Prune several at once |
| find . -maxdepth 2 -name "*.js" | Or just do not go deep |

With -prune, keep the -print at the end or the pruned directories themselves show up in the output.

## Find by Time

find counts age in whole 24-hour blocks: -mtime -7 is "modified within 7 days", -mtime +7 is "older than 7 days" (effectively 8 days and up), and -mtime 7 is "exactly 7 days old", which is rarely what you want.

| Command                      | What it does                                 |
|------------------------------|----------------------------------------------|
| find . -mtime -1             | Modified in the last 24 hours                |
| find . -mtime +30            | Older than 30 days                           |
| find . -mmin -60             | Modified in the last hour                    |
| find . -mmin +15             | Untouched for more than 15 minutes           |
| find . -newer ref.txt        | Modified more recently than ref.txt          |
| find . -newermt "2026-09-01" | Modified since a date                        |
| find . -daystart -mtime 0    | Modified today, counting from midnight (GNU) |

## Find by Size

Always give a unit: without one, the number means 512-byte blocks.

| Command                    | What it does       |
|----------------------------|--------------------|
| find . -size +100M         | Larger than 100 MB |
| find / -size +1G           | Larger than 1 GB   |
| find . -size -10k          | Smaller than 10 KB |
| find . -size +1M -size -5M | Between 1 and 5 MB |
| find . -type f -size 0     | Zero-byte files    |

## Running Commands with -exec

{} stands for the matched file. \\ runs the command once per file; + batches many files per run and is much faster.

| Command | What it does |
|----|----|
| find . -name "*.log" -exec gzip {} \\ | One command per file |
| find . -type f -exec chmod 644 {} + | Batched: one command, many files |
| find . -name "*.bak" -ok rm {} \\ | Ask before each one |
| find . -name "*.py" -exec grep -l "TODO" {} + | Search inside the matches |
| find . -name "*.jpg" -execdir mogrify -resize 50% {} \\ | Run in each file's own directory |
| find . -type f -exec ls -lh {} + \| sort -k5 -rh | Feed the results to another pipeline |

\+ requires {} once, at the end. If the command needs the name twice (mv {} {}.bak), use \\.

## Search File Contents

find only ever matches metadata. When the match has to be inside the file, that is [grep](https://sshworkbench.com/cheatsheets/grep); find's job is narrowing the set grep has to read.

| Command | What it does |
|----|----|
| grep -rn "timeout" /var/log | grep already recurses, so no find needed here |
| find . -name "*.py" -exec grep -n "TODO" {} + | Content search inside a name-filtered set |
| find . -name "*.conf" -exec grep -l "listen" {} + | Print only the names of files that match |
| find . -type f -print0 \| xargs -0 grep -l "text" | Same, safe with spaces in names |
| find . -mtime -1 -type f -exec grep -H "error" {} + | Only search what changed today |
| find . -type f -exec grep -Iq . {} \\ -print | List text files, skip binaries |

## Deleting Files

Order matters: -delete acts on everything matched so far, so it goes last. find . -delete -name "*.tmp" deletes everything under . because the tests come too late.

| Command | What it does |
|----|----|
| find . -name "*.tmp" -print | Dry run first: see exactly what will go |
| find . -name "*.tmp" -delete | Then swap -print for -delete |
| find /var/log/app -name "*.log" -mtime +30 -delete | Cleanup older than 30 days |
| find . -type d -empty -delete | Remove empty directories |
| find . -name "*.tmp" -exec rm -v {} + | Alternative with visible output |

-delete implies depth-first order and refuses non-empty directories, so it cannot take out a whole tree by accident the way rm -rf can.

## Pairing with xargs

-print0 and -0 pass names separated by NUL bytes, so spaces and newlines in file names cannot break the pipeline.

| Command | What it does |
|----|----|
| find . -type f -print0 \| xargs -0 grep -l "TODO" | Content search over the matched set |
| find . -name "*.log" -print0 \| xargs -0 rm | Delete via xargs |
| find . -name "*.png" -print0 \| xargs -0 -I{} cp {} /backup/ | Place each name mid-command |
| find . -name "*.css" -print0 \| xargs -0 -P4 gzip -k | Four jobs in parallel |
| find . -type f \| wc -l | Count matches (fine without -print0) |

-exec ... + covers most of what xargs does; xargs earns its keep for -P parallelism and mid-command -I{} substitution.

## Permissions and Ownership

Modes pair naturally with the [chmod cheat sheet](https://sshworkbench.com/cheatsheets/chmod) and the [chmod calculator](https://sshworkbench.com/tools/chmod-calculator).

| Command | What it does |
|----|----|
| find . -perm 644 | Mode is exactly 644 |
| find . -perm -u+w | Owner-writable, whatever else is set |
| find . -perm /o+w | World-writable (audit) |
| find / -perm -4000 -type f | All setuid binaries (audit) |
| find . -user alice | Owned by alice |
| find . -group www-data | Group www-data |
| find / -nouser | Orphaned files (deleted owner) |
| find . -type f -not -perm 644 -exec chmod 644 {} + | Fix stragglers |

## Depth and Filesystems

GNU find wants these before the other tests.

| Command | What it does |
|----|----|
| find . -maxdepth 1 -name "*.md" | This directory only, no recursion |
| find . -maxdepth 2 -type d | Two levels down at most |
| find . -mindepth 1 | Skip the starting directory itself |
| find / -xdev -name "*.log" | Stay on one filesystem (skip mounts) |
| find -L . -type l | Follow symlinks; this spelling finds broken ones |

## Permission Denied Errors

Those messages go to stderr, so they never reach a pipe or a redirected results file. They only clutter the screen.

| Command | What it does |
|----|----|
| find / -name "*.conf" 2>/dev/null | Discard every error, including the real ones |
| find / -name "*.conf" 2>errors.txt | Keep the errors, just not on screen |
| find / -readable -name "*.conf" | Skip unreadable files as a test (GNU) |
| find . ! -readable -prune -o -print | Do not even descend into unreadable directories |
| sudo find / -name "*.conf" | Read everything, so there is nothing to hide |
| find /etc /home -name "*.conf" | Narrow the search instead of silencing it |

find still exits with status 1 after a permission error, so find ... 2>/dev/null && echo done prints nothing even though the output looked fine.

## Output Format and Sorting

-printf is GNU only. On macOS use the ls or stat variants instead.

| Command | What it does |
|----|----|
| find . -type f -printf "%T@ %p\n" \| sort -rn \| head | Newest files first |
| find . -type f -printf "%TY-%Tm-%Td %p\n" | A readable date next to each path |
| find . -type f -printf "%s %p\n" \| sort -rn \| head | Biggest files first, in bytes |
| find . -printf "%f\n" | Base name only, no directory part |
| find . -type f -exec ls -lht {} + \| head | Sort by time without -printf (one batch) |
| find . -type f \| wc -l | Count the matches |

## Find Where a Command Lives

Looking for an executable is a different job. The shell already knows the answer, so asking find is the slow way round.

| Command | What it does |
|----|----|
| command -v python3 | Path the shell would actually run (POSIX, built in) |
| type -a python3 | Every candidate: alias, function, and each binary on PATH |
| which python3 | The familiar one, but blind to aliases and functions |
| whereis python3 | Binary, source, and man page locations |
| dpkg -S $(which nginx) | Which Debian/Ubuntu package installed it |
| rpm -qf $(which nginx) | Same on RHEL, Fedora and friends |
| find / -name "python3" -type f 2>/dev/null | Last resort when it is not on PATH |

## find vs locate vs grep vs fd

| Tool | Search Target | Search Mechanism | Speed |
|---|---|---|---|
| `find` | Filename & metadata | Real-time filesystem tree walk | Thorough / IO bound |
| `locate` | Filename | Pre-built database index (`updatedb`) | Instantaneous (can be stale) |
| `grep` | File contents | Scans text bytes inside files | Dependent on file size |
| `fd` | Filename | Parallelized Rust tree walk (ignores `.gitignore`) | Ultra fast |

## Real Recipes

| Command | What it does |
|----|----|
| find / -xdev -type f -size +100M -exec du -h {} + 2>/dev/null \| sort -rh \| head -20 | 20 biggest files on the disk |
| find . -type f -mtime -1 | What changed in the last 24 hours |
| find /var/log/app -name "*.log" -mtime +30 -delete | Log cleanup (dry-run with -print first) |
| find . -type f -newermt "2026-09-01" ! -newermt "2026-09-05" | Changed within a date range |
| find /var/www -type d -exec chmod 755 {} + | Web dirs to 755 (then files to 644 with -type f) |
| find . -name "*.orig" -o -name "*.rej" -o -name "*~" | Leftover editor and patch junk |
| find . -maxdepth 1 -type d -exec du -sh {} + \| sort -rh | Which subdirectory is eating the space |

## Gotchas

- Unquoted patterns break silently: find . -name *.log works until the shell expands the glob in the current directory first. Always quote: -name "*.log".
- -mtime +1 does not mean "older than yesterday": ages round down to whole days, so it matches 2 days and older.
- Test order is left to right: put cheap, selective tests ( -name, -type) before expensive ones, and -delete absolutely last.
- macOS ships BSD find: -daystart and -printf are missing, and it wants a path argument ( find . -name x, not find -name x); brew install findutils gets GNU find as gfind.
- find output is not safe for shell loops when names contain spaces; use -print0 \| xargs -0 or -exec.
- Searching / includes /proc and network mounts; add -xdev or start from a narrower directory.
- When df says the disk is full but find cannot account for the space, a deleted file is still held open by a process. That is an [lsof](https://sshworkbench.com/cheatsheets/lsof) job, not a find one.

## find FAQ

### Why does the find command say Permission denied, and how do I hide it?

Those lines come from directories your user cannot read, usually under /proc, /run, /root and other people's home directories. They go to stderr, not stdout, so they never contaminate a pipe or a file of results, only your screen. 2>/dev/null throws all of stderr away, including errors you would want to see, so 2>errors.txt is the safer habit when the search matters. GNU find also has -readable, a test that skips unreadable files instead of complaining about them. One thing no redirect changes: find still exits with status 1 after a permission error, so a chain like find ... && echo done stays silent even when the output looks clean.

### What is the difference between -exec with \\ and with +?

With ; find runs the command once per matched file: chmod 644 a, then chmod 644 b, and so on. With + it appends as many file names as fit onto one command line, like xargs: chmod 644 a b c. The + form is far faster over thousands of files because it starts a handful of processes instead of thousands. Use ; only when the command takes a single file, or when {} appears more than once or not at the end, which + does not allow. The semicolon is escaped because the shell would otherwise treat it as the end of the command. xargs is the third option and behaves like +, but it earns its place for -P parallelism and for -I{} when the file name has to sit in the middle of the command rather than at the end.

### How do I find files containing a specific string in Linux?

That is grep's job, not find's: grep -rn "connection timeout" /var/log searches file contents recursively and prints matching lines with file and line number. Combine the two when you want content matching inside a name-filtered set: find . -name "*.py" -exec grep -n "TODO" {} + searches only Python files, and adding -l to grep prints just the file names. For trees with binary files or odd names, the safe pairing is find . -type f -print0 \| xargs -0 grep -l "text". find alone only ever matches file metadata: name, size, age, type, permissions.

### How do I find where a command is located in Linux?

Not with find. The shell already knows, so ask it: command -v python3 prints the path it would run, type -a python3 lists every candidate including aliases and shell functions, and whereis python3 adds the source and man page. which is the familiar one but it is a separate program that knows nothing about your aliases or functions, which is why the same name can behave differently from what it reports. If a command you just installed is still not found, run hash -r to clear the shell's cached lookup table before blaming the package. Reach for find / -name only when the file is genuinely off PATH.

### Is the find command recursive by default?

Yes. find . descends into every subdirectory with no flag needed, which is the opposite of ls and grep. You limit it rather than enable it: -maxdepth 1 searches only the directory itself, -maxdepth 2 goes one level further, and -mindepth 1 excludes the starting directory from the results, useful when acting on a directory's contents but not the directory. GNU find wants these depth options before tests like -name and warns otherwise. If a search is slow because it crosses into other filesystems like network mounts, -xdev keeps it on one filesystem.

---
Source: https://sshworkbench.com/cheatsheets/find
