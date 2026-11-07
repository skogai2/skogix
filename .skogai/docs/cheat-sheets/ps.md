# ps Command Examples

ps prints a snapshot of the processes running right now. This sheet covers ps aux and ps -ef, what each output column means, and how to filter, sort, and format the list.

Last updated September 11, 2026

On this page

- [ps aux](#ps-aux)
- [ps -ef](#ps--ef)
- [Flag Styles](#flag-styles)
- [Output Columns](#output-columns)
- [STAT Codes](#stat-codes)
- [Filter by User](#filter-by-user)
- [Filter by PID](#filter-by-pid)
- [Find by Name](#find-by-name)
- [Sort by Memory and CPU](#sort-by-memory-and-cpu)
- [Custom Format](#custom-format)
- [Threads](#threads)
- [Process Tree](#process-tree)
- [ps vs top](#ps-vs-top)
- [Gotchas](#gotchas)

## ps aux

The one most people type. BSD syntax, no leading dash: a means other users' processes, u adds the user-oriented columns, x adds processes with no controlling terminal (daemons).

| Command | What it does |
|----|----|
| ps aux | Every process on the machine, user-oriented format |
| ps aux \| less | Same, one page at a time |
| ps auxww | Same, with full command lines instead of truncated ones |
| ps ux | Only your own processes |
| ps ax | Every process, short format (no user or memory columns) |
| ps axo pid,user,%mem,args | Pick your own columns, BSD style |
| ps | Only processes attached to the current terminal |
| ps aux --sort=-%mem \| head -n 11 | The ten biggest memory users |
| ps aux \| grep -i nginx | The usual way people filter it (see [grep](https://sshworkbench.com/cheatsheets/grep)) |
| ps axjf | Every process as a tree, with PPID and process group |

## ps -ef

UNIX syntax, single dash: -e selects every process and -f is the full-format listing. It is the same process list as ps aux with a different set of columns, and it is the form you will see in older scripts and on AIX, Solaris and HP-UX.

[TABLE]

## Flag Styles

ps accepts three different option syntaxes, and this is the single most confusing thing about it. All three work at once, which is why ps aux and ps -ef both look correct and both are.

[TABLE]

The same letter can mean different things in different styles, so the dash is not decoration:

[TABLE]

Mixing a BSD option and a UNIX option in one command is where error: garbage option comes from. Pick one style per command.

## Output Columns

What ps aux prints, left to right:

[TABLE]

ps -ef prints a different set:

[TABLE]

A process with a command in square brackets, such as \[kworker/0:2\], is a kernel thread, not a program you installed.

## STAT Codes

The first letter is the state. Anything after it is a modifier.

[TABLE]

So Ssl is a sleeping, multi-threaded session leader, which is what a healthy daemon looks like. Z and a long run of D are the two worth chasing.

## Filter by User

[TABLE]

## Filter by PID

| Command | What it does |
|----|----|
| ps -p 1234 | One process by PID |
| ps -fp 1234 | Same, with PPID and the full command |
| ps -p 1234,5678 -o pid,ppid,rss,cmd | Several PIDs, chosen columns |
| ps -p 1234 -o args= | Just the command line, no header |
| ps -p 1234 -o etime=,etimes= | How long it has been running, formatted and in seconds |
| ps --ppid 1234 | The children of a process |
| ps -f --ppid 1 | Everything reparented to init or systemd |
| ps -p \$(pgrep -d, nginx) -o pid,rss,cmd | Every PID of a named process |
| ps -o ppid= -p 1234 | Just the parent PID, handy in scripts |

cat /proc/1234/cmdline \| tr '\0' ' ' gives the same command line when ps is not installed.

## Find by Name

[TABLE]

For a service you manage with systemd, systemctl status nginx shows the same PIDs plus the unit state and recent logs. See [systemctl](https://sshworkbench.com/cheatsheets/systemctl) and [journalctl](https://sshworkbench.com/cheatsheets/journalctl).

## Sort by Memory and CPU

--sort takes a column key. A leading - sorts descending, + or nothing sorts ascending.

| Command | What it does |
|----|----|
| ps aux --sort=-%mem \| head -n 11 | Top ten memory users (line 1 is the header) |
| ps aux --sort=-%cpu \| head -n 11 | Top ten by lifetime average CPU |
| ps -eo pid,user,rss,cmd --sort=-rss \| head | Same by real RSS, in a tighter format |
| ps -eo pid,etime,cmd --sort=-etime \| head | The longest-running processes |
| ps -eo pid,cmd --sort=start_time \| tail | The most recently started |
| ps aux --sort=-rss,+%cpu | Two keys, in order |

```
# Memory used per program name, biggest first
ps -eo comm,rss --no-headers | awk '{m[$1]+=$2} END {for (c in m) printf "%8.1f MB  %s\n", m[c]/1024, c}' | sort -rn | head
```

Copy

Remember that %CPU in ps is an average over the life of the process. A process that pinned a core for an hour last night still ranks high, and one spiking right now may not. For live CPU, use [top or htop](https://sshworkbench.com/cheatsheets/top-htop).

## Custom Format

-o (or -eo for every process) replaces the default columns with exactly the ones you ask for.

[TABLE]

Common keys: pid, ppid, pgid, sid, user, group, comm, args, %cpu, %mem, rss, vsz, stat, etime, etimes, time, lstart, nice, pri, tty, wchan, nlwp. ps L prints the whole list.

## Threads

[TABLE]

A thread's LWP or TID is the number top -H and htop show when you turn threads on, so you can match one to the other.

## Process Tree

| Command | What it does |
|----|----|
| ps -ef --forest | Full listing drawn as a tree |
| ps axjf | BSD version, with PPID, PGID and session |
| ps -f --forest -u www-data | One user's processes as a tree |
| ps -e --forest -o pid,ppid,user,cmd | Tree with your own columns |
| ps -ejH | Hierarchy by indentation instead of line drawing |
| pstree -p | The dedicated tool, with PIDs |
| pstree -aps 1234 | The ancestry of one PID, up to init |

## ps vs top

[TABLE]

Rule of thumb: ps answers "what is running and what is its PID", top answers "what is eating the machine right now". Full keys and columns are on the [top and htop sheet](https://sshworkbench.com/cheatsheets/top-htop).

## Gotchas

- ps aux
  and
  ps -ef
  are both right.
  ps -aux
  is not: it asks for a user named
  x
  , and only works because procps guesses what you meant and warns you.
- Mixing styles in one command gives
  error: garbage option
  .
  ps aux --sort=-%mem
  is fine because GNU long options combine with either style, but
  ps -aux f
  is not.
- %CPU
  is a lifetime average. Sorting by it finds yesterday's hog, not today's.
- Summing the
  RSS
  column overcounts, because shared libraries are charged in full to every process that maps them.
- A
  D
  state process ignores every signal including
  kill -9
  . It is stuck in the kernel, usually on disk or NFS, and only unblocks when the I/O finishes or the machine reboots.
- Output is truncated to terminal width. Add
  ww
  (
  ps auxww
  ,
  ps -efww
  ) before deciding a command line looks wrong.
- ps aux \| grep foo
  always matches its own grep. Use
  pgrep foo
  or
  ps aux \| grep \[f\]oo
  .
- docker ps
  is a different command with different flags. It lists containers, not processes;
  docker top
  is the one that lists processes inside a container. See the [docker sheet](https://sshworkbench.com/cheatsheets/docker).
- A minimal container image has no
  ps
  at all. Install
  procps
  , or run
  docker top
  from the host.
- To find which process owns a port, ps is the wrong tool. Use
  ss -tlnp
  or
  lsof -i :80
  , covered on the [netstat and ss sheet](https://sshworkbench.com/cheatsheets/netstat-ss).

### See processes without the flag soup

SSH Workbench shows live CPU, memory, and process lists for every server over plain SSH, with kill and restart as buttons instead of PIDs.

[Try free for 7 days](https://sshworkbench.com/#install)

## ps FAQ

### What is the difference between ps aux and ps -ef?

They list the same processes in different formats. ps aux is BSD syntax and gives you %CPU, %MEM, VSZ, RSS, STAT and START, which is what you want when you are hunting a memory or CPU hog. ps -ef is UNIX syntax and gives you PPID and STIME instead, which is what you want when you care about which process started which. Both truncate the command to your terminal width, so add ww to either one when the line matters. Use whichever you like; just do not write ps -aux, which asks for processes owned by a user named x.

### What do VSZ and RSS mean in ps output?

VSZ is virtual size: every byte the process has mapped, including shared libraries, files mapped into memory and memory it reserved but never touched. It is usually huge and almost never the number you want. RSS is resident set size: the physical RAM the process actually occupies right now, in kilobytes. RSS is the useful one, with one catch. Shared libraries count in full against every process that maps them, so adding up the RSS column gives a total larger than the memory in the machine. For a per-process figure that splits shared pages fairly, read /proc/PID/smaps_rollup or install smem.

### Why does ps cut off the end of the command?

ps truncates each line to the width of your terminal. Add w to widen it and ww for unlimited width: ps auxww or ps -efww. The GNU form is --width 200 or --cols 200. If you only need one process, ps -p 1234 -o args= prints the full command line with no header and no truncation. Piping into less -S also works, and lets you scroll sideways with the arrow keys.

### How do I find zombie or defunct processes with ps?

Zombies carry the state code Z and show as \<defunct\> in the command column. List them with ps -eo pid,ppid,stat,cmd \| awk '\$3 ~ /^Z/'. You cannot kill a zombie, because it is already dead: it is a finished process whose exit status the parent never collected. Look at the PPID column instead and deal with the parent, either by sending it SIGCHLD or by restarting it. A handful of short-lived zombies is normal; hundreds mean a buggy parent.

### Why is ps command not found inside a Docker container?

Slim base images ship without procps, the package that contains ps. Install it with apt-get update && apt-get install -y procps on Debian and Ubuntu images, apk add procps on Alpine, or microdnf install procps-ng on UBI. You often do not need to: docker top CONTAINER lists a container's processes from the host, and ps -ef on the host shows them too, with the host's PID numbers rather than the container's.

---
Källa: https://sshworkbench.com/cheatsheets/ps
