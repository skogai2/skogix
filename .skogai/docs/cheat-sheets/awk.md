# awk Command Examples

awk splits every line into fields and runs your code on the lines you select, which makes it the tool for columns: print them, filter on them, do math on them. Every row on this sheet is a real example you can paste into a shell.

Last updated September 11, 2026

On this page

- [Print Columns](#print-columns)
- [Column Ranges](#column-ranges)
- [Field Separators](#field-separators)
- [NR and NF](#nr-and-nf)
- [Patterns and Conditions](#patterns-and-conditions)
- [Loops and Control Flow](#loops-and-control-flow)
- [BEGIN and END](#begin-and-end)
- [printf](#printf)
- [Quoting and Output](#quoting-and-output)
- [Arrays and Counting](#arrays-and-counting)
- [String Functions](#string-functions)
- [Variables](#variables)
- [Shell Commands from awk](#shell-commands-from-awk)
- [Scripts and Recipes](#scripts-and-recipes)
- [Gotchas](#gotchas)

## Print Columns

Fields split on whitespace by default. \$1 is the first field, \$NF the last, \$0 the whole line.

| Command                               | What it does                      |
|---------------------------------------|-----------------------------------|
| awk '{print \$1}' access.log          | First column of every line        |
| awk '{print \$1, \$3}' file           | Two columns, separated by a space |
| awk '{print \$NF}' file               | Last column                       |
| awk '{print \$(NF-1)}' file           | Second-to-last column             |
| awk '{print \$2 " uses " \$1}' du.txt | Mix fields with literal text      |
| ps aux \| awk '{print \$2, \$11}'     | PID and command from ps           |
| ls -l \| awk '{print \$5, \$9}'       | Size and name from ls             |
| awk '{print NR": "\$0}' file          | Number every line                 |

## Column Ranges

Printing everything except one column is the awkward case, because awk has no slice syntax.

| Command | What it does |
|----|----|
| awk '{print \$2, \$3, \$4}' file | A fixed range of columns |
| awk '{\$1=""; print}' file | All but the first field (leaves a leading space) |
| awk '{\$1=""; sub(/^ /, ""); print}' file | All but the first field, leading space trimmed |
| awk '{\$NF=""; print}' file | All but the last field |
| awk 'NF--' file | Drop the last field (gawk and mawk) |
| awk '{print substr(\$0, index(\$0, \$3))}' file | Field 3 to end of line, original spacing kept |

Assigning to a field rebuilds \$0 with OFS, so \$1="" flattens any column padding the file had. The substr/index form avoids that, at the cost of matching the wrong spot if that text also appears earlier in the line. For an arbitrary start column, loop:

```
awk '{for (i = 3; i <= NF; i++) printf "%s%s", $i, (i < NF ? OFS : ORS)}' file
```

Copy

## Field Separators

-F sets the input separator; OFS is what goes between fields on output.

[TABLE]

## NR and NF

NR is the current line number, NF the number of fields on the line. Both double as filters.

| Command | What it does |
|----|----|
| awk 'NR == 5' file | Print line 5 only |
| awk 'NR \> 1' data.csv | Skip the header line |
| awk 'NR \>= 10 && NR \<= 20' file | A line range |
| awk 'NR % 2 == 0' file | Every second line |
| awk 'END {print NR}' file | Count lines, like wc -l |
| awk '{print NF}' file | How many fields each line has |
| awk 'NF' file | Drop blank lines (0 fields is false) |
| awk 'NF == 7' file | Only lines with exactly 7 fields (catch bad CSV rows) |
| awk 'FNR == 1 {print FILENAME}' \*.log | FNR resets per file; print each file's name once |

## Patterns and Conditions

The shape is pattern {action}: the action runs on lines where the pattern holds. Either half can be omitted.

| Command | What it does |
|----|----|
| awk '/error/' app.log | Lines matching a regex (like grep) |
| awk '/error/ {print \$2}' app.log | Column 2 of matching lines |
| awk '!/debug/' app.log | Lines NOT matching |
| awk '\$1 == "root"' ps.txt | Exact string match on a field |
| awk '\$3 \> 100' data.txt | Numeric comparison on a field |
| awk '\$2 ~ /^dev/' file | Regex match on one field only |
| awk '\$2 !~ /^dev/' file | Field does not match |
| awk '\$1 == "GET" && \$3 \> 1000' access.log | Combine with && and \|\| |
| awk '/BEGIN/,/END/' file | Range: from one match to the next |
| df -h \| awk 'NR \> 1 {print \$5, \$6}' | Disk usage percent per mount |

if/else lives inside the action:

```
awk '{if ($3 > 100) print $1 " high"; else print $1 " ok"}' data.txt
awk '{print $1, ($3 > 100 ? "high" : "ok")}' data.txt
```

Copy

## Loops and Control Flow

| Command | What it does |
|----|----|
| awk '{for (i = 1; i \<= NF; i++) print \$i}' file | One field per line |
| awk 'BEGIN {for (i = 1; i \<= 5; i++) print i}' | Loop with no input at all |
| awk '{i = 1; while (i \<= NF) {print \$i; i++}}' file | Same loop, while form |
| awk '/^#/ {next} {print}' nginx.conf | Skip a line and read the next one |
| awk '/error/ {print; exit}' app.log | Stop at the first hit (fast on huge files) |
| awk 'NR \> 1000 {exit} {print}' huge.log | Bail out early instead of reading the rest |
| awk '{c++} END {exit c \> 0 ? 0 : 1}' file | Set the shell exit status from awk |

next skips the remaining rules for that line; exit jumps straight to END, so an END block still runs after it.

## BEGIN and END

BEGIN runs before the first line, END after the last: headers, totals, averages.

[TABLE]

## printf

printf formats output with C-style specifiers and adds no newline unless you write \n.

[TABLE]

print on a number over about 16 digits falls back to OFMT and prints 1e+18; %.0f or %d keeps the digits.

## Quoting and Output

| Command | What it does |
|----|----|
| awk '{printf "%s ", \$1} END {print ""}' file | Everything on one line, no newline per record |
| awk '{print "\\" \$1 "\\"}' file | Wrap a field in double quotes |
| awk -v q='"' '{print q \$1 q}' file | Same thing without escaping |
| awk '{print \$1 "\t" \$2}' file | Put a literal tab between fields |
| awk '{sub(/\r\$/, ""); print}' file | Strip Windows carriage returns |
| awk '{print \$2 \> "out.txt"}' file | Write to a file from inside awk |
| awk '{print \$2 \>\> "out.txt"}' file | Append instead of overwriting |
| awk '{print \> \$1".txt"}' file | Split input into one file per column-1 value |

\> inside the program is awk's redirect, not the shell's, so it needs no quoting beyond the single quotes already around the program. awk keeps every file it writes open, so splitting into thousands of files needs close(\$1".txt").

## Arrays and Counting

awk arrays are string-keyed maps, which makes counting and grouping one-liners.

| Command | What it does |
|----|----|
| awk '{count\[\$1\]++} END {for (k in count) print k, count\[k\]}' access.log | Count occurrences of each value in column 1 |
| awk '!seen\[\$0\]++' file | Remove duplicate lines, order preserved (uniq without sort) |
| awk '!seen\[\$1\]++' file | First line per distinct column-1 value |
| awk '{s\[\$1\] += \$2} END {for (k in s) print k, s\[k\]}' sales.txt | Sum column 2 per key in column 1 |
| awk '{count\[\$1\]++} END {for (k in count) if (count\[k\] \> 1) print k}' file | Keys that appear more than once |

The count-and-sort pipeline for "top talkers" in a log (see the [grep cheat sheet](https://sshworkbench.com/cheatsheets/grep) for the pure-grep half):

```
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
```

Copy

## String Functions

[TABLE]

sub and gsub modify in place and return the replacement count. For pure stream find-and-replace, [sed](https://sshworkbench.com/cheatsheets/sed) is usually the shorter tool.

## Variables

| Command | What it does |
|----|----|
| awk -v n=10 'NR \<= n' file | Pass a value in with -v |
| awk -v user="\$USER" '\$1 == user' ps.txt | Pass a shell variable in safely |
| awk -v pat="\$1" '\$0 ~ pat' file | Match against a variable (in a script) |
| awk '{print ENVIRON\["HOME"\]}' file | Read environment variables directly |
| awk -v ORS=', ' '{print \$1}' file | Output record separator: join lines with commas |
| awk 'BEGIN {RS=""} {print \$1}' file | Paragraph mode: records split on blank lines |

## Shell Commands from awk

awk can shell out mid-program, which covers the jobs a pipeline alone cannot.

| Command | What it does |
|----|----|
| awk '{system("mkdir -p " \$1)}' dirs.txt | Run a shell command once per line |
| awk 'BEGIN {"date +%F" \| getline d; print d}' | Capture a command's output into a variable |
| awk '{print \$1 \| "sort -u"}' file | Pipe awk's own output into a command |
| awk 'BEGIN {while (("ls -1" \| getline f) \> 0) print f}' | Read a command's output line by line |
| ps aux \| awk '/\[n\]ginx/ {print \$2}' \| xargs kill | Find PIDs and kill them |

A command stays open after the first read, so running it again in the same program returns nothing until you close("date +%F").

## Scripts and Recipes

Past one line, put the program in a file and run it with -f, or give it a shebang.

```
awk -f report.awk access.log
```

Copy

```
#!/usr/bin/awk -f
BEGIN { FS = ","; print "user,total" }
NR > 1 { total[$1] += $3 }
END { for (u in total) print u "," total[u] }
```

Copy

Everyday pipelines:

[TABLE]

## Gotchas

- Single-quote the program. In double quotes the shell expands
  \$1
  before awk runs, which silently breaks the script.
- awk: command not found
  means no awk is installed, which happens on slim containers:
  apt install gawk
  or
  apk add gawk
  . A
  syntax error at source line 1
  almost always means the shell ate part of the program, so check the quoting before the logic.
- Not all awks are equal: Linux usually has gawk or mawk, macOS ships an older BSD awk.
  gensub()
  ,
  length(array)
  , and
  \d
  -style classes are gawk extras; everything on this sheet sticks to the portable core.
- Comparisons are type-sensitive:
  \$1 \> 5
  compares numbers, but if the field has stray characters awk may compare strings. Force a number with
  \$1+0
  .
- Assigning to any field (even
  \$1=\$1
  ) rebuilds
  \$0
  with OFS, which rewrites the separators on output. Sometimes that is exactly what you want; sometimes it is the bug.
- Uninitialized variables are
  ""
  and 0 at the same time, so
  sum += \$1
  needs no setup, and a missing field prints as empty rather than erroring.
- grep selects lines and sed rewrites them; see the [grep cheat sheet](https://sshworkbench.com/cheatsheets/grep) and [sed cheat sheet](https://sshworkbench.com/cheatsheets/sed) for the other two thirds of the toolkit.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## awk FAQ

### What does awk stand for?

The initials of its three authors: Alfred Aho, Peter Weinberger, and Brian Kernighan, who wrote it at Bell Labs in 1977. It is said like the bird, not spelled out. The name matters in practice because `awk` on your machine is usually a link to someone else's rewrite: gawk on most Linux distributions, mawk on Debian and Ubuntu by default, and the original one-true-awk on macOS. That is why a gawk-only function such as `gensub()` works on your server and fails on your laptop.

### How does the awk command work?

It reads input one record (a line by default) at a time, splits that record into fields on `FS`, then tests every pattern in your program against it and runs the action of each one that matches. `BEGIN` fires before the first read, `END` after the last. That loop explains the shorthands: `NR` counts records for free, a pattern with no action gets the default `{print}`, and an action with no pattern runs on every line. It also explains why awk needs no loop of its own for most jobs.

### What is the difference between cut and awk?

`cut` splits on one literal character and never collapses repeated ones, so `cut -d' ' -f2` falls apart on `ls -l` or `ps` output where the columns are padded with variable spacing. awk's default separator is any run of whitespace, so `awk '{print $2}'` just works. `cut` also emits fields in file order however you list them, while awk prints them in the order you write. `cut` stays faster on huge single-delimiter files, which is the one place it still wins.

### How do I sort awk output?

awk has no output ordering of its own. `for (k in arr)` walks keys in an order you cannot predict, which is why counting one-liners come out shuffled. Pipe the result to `sort` instead: `awk '{c[$1]++} END {for (k in c) print c[k], k}' log | sort -rn`. gawk can sort in-process with `PROCINFO["sorted_in"] = "@val_num_desc"` or `asort()`, but neither exists in mawk or the BSD awk on macOS, so the pipe stays the portable answer.

### How do I use awk in a shell script?

Single-quote the program so the shell leaves `$1` alone, and hand shell values in with `-v` rather than splicing them into the program text, which breaks the first time a value contains a quote. Anything after the program is treated as a filename, not an argument, which is the usual surprise. Past a few lines, move the program into its own `.awk` file and run `awk -f report.awk data.txt`, or give the file a `#!/usr/bin/awk -f` shebang and make it executable.

---
Källa: https://sshworkbench.com/cheatsheets/awk
