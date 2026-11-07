# htop Commands

top ships with every Linux distro and htop is the friendlier version you install yourself. This sheet covers both: what each column, colour and load average number means, the keys that sort and filter the list, killing a process from the screen, and running top in batch mode from a script.

Last updated September 11, 2026

On this page

- [top Basics](#top-basics)
- [Reading top Output](#reading-top-output)
- [Load Average](#load-average)
- [Sorting in top](#sorting-in-top)
- [Watching One Process](#watching-one-process)
- [Per-Core CPU](#per-core-cpu)
- [Batch Mode](#batch-mode)
- [Refresh Rate](#refresh-rate)
- [htop Keyboard Shortcuts](#htop-keyboard-shortcuts)
- [htop Colours](#htop-colours)
- [Filter and Search](#filter-and-search)
- [Tree View](#tree-view)
- [Kill and Renice](#kill-and-renice)
- [htop Options](#htop-options)
- [Installing htop](#installing-htop)
- [top vs htop](#top-vs-htop)
- [Gotchas](#gotchas)

## top Basics

top is installed everywhere and needs no arguments. Press q to leave it.

[TABLE]

Keys while it is running:

[TABLE]

## Reading top Output

Five header lines describe the machine, then the table describes the processes.

```
top - 14:02:31 up 12 days,  3:14,  2 users,  load average: 0.52, 0.58, 0.59
Tasks: 213 total,   1 running, 212 sleeping,   0 stopped,   0 zombie
%Cpu(s):  3.1 us,  1.2 sy,  0.0 ni, 95.4 id,  0.3 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   7936.4 total,    412.8 free,   3120.6 used,   4403.0 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   4411.2 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 1421 www-data  20   0  412536  58204  32120 S   2.3   0.7   1:12.44 nginx
```

Copy

[TABLE]

A one-off snapshot of the same columns comes from [ps](https://sshworkbench.com/cheatsheets/ps).

## Load Average

Three counts of processes running or waiting, averaged over 1, 5 and 15 minutes. Not a percentage.

[TABLE]

Linux counts processes in uninterruptible sleep as load, so a hung NFS mount or a dying disk can show load 15 with the CPU idle. When the numbers look wrong, read wa and the D states first.

## Sorting in top

[TABLE]

From the command line: top -o %MEM, top -o TIME+, or top -o -%CPU to sort smallest first.

## Watching One Process

[TABLE]

## Per-Core CPU

In the default Irix mode %CPU is a share of a single core, so a threaded process on a 16 core box can legitimately read 1600.

[TABLE]

htop draws one bar per core with no key to press, which is the usual reason people install it.

## Batch Mode

-b turns off the interactive screen and prints plain text. It is the only way to pipe or redirect top, and htop has no equivalent.

[TABLE]

```
# Top five memory users as plain lines, for a cron report
top -b -n 1 -o %MEM -w 512 | sed -n '8,12p'

# CPU for one process, sampled properly
top -b -n 2 -d 1 -p 1234 | tail -1
```

Copy

The first sample of %CPU is measured since boot, so a single -n 1 run understates a busy process. Ask for two iterations and read the last. For a one-shot list without any of this, ps aux --sort=-%mem \| head is simpler ([ps](https://sshworkbench.com/cheatsheets/ps)).

## Refresh Rate

[TABLE]

A slower refresh is worth setting on a busy server: top itself shows up in its own list, and a half-second delay on a few thousand processes is real work.

## htop Keyboard Shortcuts

Function keys do everything, and the letter next to them works when a terminal or SSH client swallows F-keys.

[TABLE]

## htop Colours

Every meter is stacked, so each colour is a different kind of use rather than a different process.

| Colour  | Meter  | What it counts                                           |
|---------|--------|----------------------------------------------------------|
| Green   | CPU    | Normal user processes                                    |
| Red     | CPU    | Kernel time: system calls, drivers, interrupts           |
| Blue    | CPU    | Low priority work, meaning a positive nice value         |
| Cyan    | CPU    | Virtualisation: steal and guest time                     |
| Green   | Memory | Memory processes are actually using                      |
| Blue    | Memory | Buffers                                                  |
| Magenta | Memory | Shared memory                                            |
| Yellow  | Memory | Disk cache, returned to programs as soon as they need it |
| Red     | Swap   | Swap in use. Any sustained figure here is worth chasing  |

In the process list, a green name is a userland thread (H toggles them) and a red one is a kernel thread (K). Memory figures above a gigabyte are shaded differently, so a loud RES value only means it is large. F1 prints the legend for your build, F2 \> Colors changes the theme, and htop -C turns colour off for a terminal that renders it badly.

## Filter and Search

Search moves the cursor and keeps the whole list. Filter hides everything else and keeps updating.

[TABLE]

## Tree View

[TABLE]

## Kill and Renice

[TABLE]

A process in D state ignores SIGKILL because it is inside a kernel call, usually waiting on storage; fix the IO, or reboot. A service that comes straight back was restarted by systemd, so stop the unit instead ([systemctl](https://sshworkbench.com/cheatsheets/systemctl)).

## htop Options

| Option              | What it does                                  |
|---------------------|-----------------------------------------------|
| htop -u deploy      | Only this user                                |
| htop -p 1,2,3       | Only these PIDs                               |
| htop -d 15          | Update every 1.5 seconds (tenths of a second) |
| htop -t             | Tree view                                     |
| htop -s PERCENT_MEM | Sort by a column                              |
| htop -F nginx       | Start with a filter                           |
| htop -C             | No colour                                     |
| htop -M             | Ignore the mouse                              |
| htop --readonly     | Disable kill and renice                       |
| htop -V             | Version                                       |
| htop -h             | Every option                                  |

Settings are written to ~/.config/htop/htoprc when you quit, and overwritten there each time, so editing the file while htop is open achieves nothing.

```
rm ~/.config/htop/htoprc   # go back to the default layout
```

Copy

## Installing htop

| System | Command |
|----|----|
| Debian, Ubuntu | sudo apt install htop |
| Fedora, RHEL 8+, Rocky, Alma | sudo dnf install htop |
| CentOS 7 | sudo yum install epel-release && sudo yum install htop |
| Arch | sudo pacman -S htop |
| Alpine | sudo apk add htop |
| openSUSE | sudo zypper install htop |
| macOS | brew install htop |
| FreeBSD | sudo pkg install htop |

Inside a slim container image, run the package index update first (apt update), and expect no htop at all in a distroless image. On RHEL 7 and older clones htop lives in EPEL, not the base repos.

## top vs htop

[TABLE]

Both read /proc, so the numbers agree. For containers, docker stats is the equivalent view ([Docker](https://sshworkbench.com/cheatsheets/docker)).

## Gotchas

- top -b -n 1
  reports almost no CPU for a busy process, because the first sample is averaged since boot. Ask for
  -n 2
  and read the last block.
- top -d
  is seconds,
  htop -d
  is tenths of a second.
  htop -d 5
  redraws twice a second and eats CPU doing it.
- Load average counts processes stuck in uninterruptible sleep, so storage trouble shows up as load with an idle CPU. Read
  wa
  and the
  D
  column before blaming the CPU.
- Adding up
  RES
  gives a figure larger than your RAM, because shared libraries are counted in every process that maps them. Trust
  avail Mem
  , not
  free
  .
- htop: error opening terminal: xterm-256color
  means your local terminal sent a
  TERM
  value the server has no terminfo entry for. Run
  TERM=xterm htop
  , or install the
  ncurses-term
  package on the server.
- Killing a service from htop usually just restarts it, because systemd is watching. Stop the unit with [systemctl](https://sshworkbench.com/cheatsheets/systemctl), and read [journalctl](https://sshworkbench.com/cheatsheets/journalctl) to find out why it was eating the CPU.

### See processes without the flag soup

SSH Workbench shows live CPU, memory, and process lists for every server over plain SSH, with kill and restart as buttons instead of PIDs.

[Try free for 7 days](https://sshworkbench.com/#install)

## htop FAQ

### What is the difference between top and htop?

They read the same numbers out of /proc, so neither is more accurate than the other. top is part of procps-ng and is already on the server; it takes keystrokes, and with -b it prints plain text you can pipe into a script. htop is a separate install with a colour meter for every core, mouse support, incremental search and filter, a tree view, and a kill menu that works on several tagged processes at once. It has no batch mode, so nothing about htop is scriptable. Use htop when you are looking at the box yourself, top when a cron job or a monitoring check is doing the looking.

### What do the colours in htop mean?

Each meter across the top is stacked, so every colour is a different kind of use, not a different process. In the CPU bars green is normal user processes, red is kernel time, blue is low priority work that has been reniced, and cyan is virtualisation (steal and guest time). In the memory bar green is memory processes are actually using, blue is buffers, magenta is shared memory and yellow is disk cache. Yellow is not a problem: the kernel hands cache back the moment something needs it. In the process list below, a green name is a userland thread and a red one is a kernel thread. Start htop with -C to drop colour entirely.

### What does load average mean in top?

The three numbers on the first line are the average number of processes running or waiting to run over the last 1, 5 and 15 minutes. They are counts, not percentages, so compare them to your core count from nproc: 4.00 on four cores means fully used with nothing queued, and 12.00 on four cores means three deep in the queue. Read them left to right for direction, since 8.0, 4.0, 1.0 is a problem building and 1.0, 4.0, 8.0 is one already passing. Linux also counts processes stuck in uninterruptible sleep, so a dead NFS mount or a failing disk can push load into double figures while the CPU sits 95% idle. Check the wa figure when that happens.

### What is the difference between VIRT, RES and SHR in top?

VIRT is everything the process has mapped, including memory it reserved and never touched and files it mapped but never read. A JVM or a Go binary routinely shows tens of gigabytes of VIRT on a machine with 8 GB of RAM, which is normal and means nothing. RES is the physical RAM the process is really holding, and it is the number to read. SHR is the part of RES shared with other processes, mostly libraries, so adding up RES across a process list counts the same shared pages several times and comes out higher than your total memory. For what is genuinely free, use the avail Mem figure at the end of the swap line rather than free.

### How do I sort htop by memory?

Press Shift+M for memory, Shift+P for CPU, Shift+T for time, or F6 to pick any column from a list. With the mouse on, clicking a column header sorts by it, and pressing I inverts the order. To start that way, run htop -s PERCENT_MEM (column names are the ones in F2 \> Columns). htop writes its settings to ~/.config/htop/htoprc when you quit, so the sort you left it on is the one you get next time; delete that file to go back to defaults. In top the same keys work, or start it with top -o %MEM, and press Shift+W to save the layout to ~/.toprc.

---
Källa: https://sshworkbench.com/cheatsheets/top-htop
