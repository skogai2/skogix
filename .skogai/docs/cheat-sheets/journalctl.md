# journalctl Commands

journalctl reads the systemd journal, where every service on a modern Linux box writes its logs. This sheet covers the journalctl commands for filtering by service, time and priority, following live output, exporting to a file, and keeping the journal's disk usage in check.

Any user can read their own logs; reading the full system journal needs sudo or membership in the systemd-journal or adm group. Filters combine, so journalctl -u nginx -p err --since today -f is one valid command.

## Service Logs

| Command | What it does |
|---|---|
| `journalctl -u nginx` | View all journal logs for `nginx.service` |
| `journalctl -u nginx -u php-fpm` | Interleave logs from multiple services chronologically |
| `journalctl _PID=1234` | Filter logs by process ID |

-u shows nothing for a misspelled unit name rather than erroring; confirm the name with systemctl list-units --type=service from the [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl).

## Follow and Tail

| Command | What it does |
|---|---|
| `journalctl -f` | Tail system logs in real time (`Ctrl+C` to exit) |
| `journalctl -u nginx -f` | Tail logs of specific service |
| `journalctl -n 100` | Show only the last 100 lines |
| `journalctl -u nginx -n 50 -f` | Show last 50 lines and continue following new entries |

## Time Ranges

--since and --until take human phrases and absolute stamps, and stack with every other filter.

| Command | What it does |
|---|---|
| `journalctl --since "1 hour ago"` | Show logs from the past hour |
| `journalctl --since "today"` | Show logs generated since 00:00:00 today |
| `journalctl --since "2026-11-01 12:00" --until "2026-11-01 14:00"` | Filter between exact timestamps |
| `journalctl -b` | Show logs from current system boot |
| `journalctl -b -1` | Show logs from previous system boot |

## Boots

Crash forensics live here: -b limits output to one boot, counted backwards from the current one.

| Command | What it does |
|----|----|
| journalctl -b | Only the current boot |
| journalctl -b -1 | The previous boot, the one that crashed or was rebooted away |
| journalctl --list-boots | Every boot the journal knows, with index and time span |
| journalctl -b -1 -e | End of the previous boot, the last thing logged before it went down |
| journalctl -b -1 -p err | Everything at error level or worse from the previous boot |
| journalctl -b -1 -k | Kernel messages from the previous boot (OOM kills, panics, disk errors) |

After an unexplained reboot, this sequence usually finds the cause:

```
journalctl --list-boots
journalctl -b -1 -e
journalctl -b -1 -p err -o short-iso
journalctl -b -1 -k -g "oom|panic|error"
```

If --list-boots shows only one boot, the journal is volatile and pre-reboot logs are gone; see the persistence setup under Disk Usage below.

## Priority

| Priority Level | Numeric | Example Flag | Description |
|---|---|---|---|
| `emerg` | 0 | `-p 0` | System is unusable |
| `alert` | 1 | `-p 1` | Action must be taken immediately |
| `crit` | 2 | `-p 2` | Critical conditions |
| `err` | 3 | `-p err` | Error conditions |
| `warning` | 4 | `-p warning` | Warning conditions |
| `notice` | 5 | `-p notice` | Normal but significant conditions |
| `info` | 6 | `-p info` | Informational messages |
| `debug` | 7 | `-p debug` | Debug-level messages |

| Level | Name    | Typical meaning      |
|-------|---------|----------------------|
| 0     | emerg   | System is unusable   |
| 1     | alert   | Act immediately      |
| 2     | crit    | Critical condition   |
| 3     | err     | Error                |
| 4     | warning | Something to look at |
| 5     | notice  | Normal but notable   |
| 6     | info    | Routine              |
| 7     | debug   | Debug detail         |

-p err means 0 through 3, not just 3: a priority flag always includes everything worse than the level named.

## Search and Filter

| Command | What it does |
|---|---|
| `journalctl -g "pattern"` | Search log messages matching regular expression |
| `journalctl _UID=1000` | Filter logs by system user ID |
| `journalctl /usr/bin/sudo` | Filter logs by executable path |
| `journalctl -k` | Display kernel messages only (`dmesg` equivalent) |

Field filters like \_PID= combine with -u, -b and time flags like any other filter. journalctl -o verbose -n 5 shows every field a journal entry carries, which is how you discover what to filter on.

## Auth and Logins

The SSH unit is ssh on Debian and Ubuntu, sshd on RHEL and its relatives.

| Command | What it does |
|---|---|
| `journalctl -u ssh` | View SSH server authentication and session logs (Debian/Ubuntu) |
| `journalctl -u sshd` | View SSH server logs on RHEL/Fedora/Arch |
| `journalctl _COMM=sshd` | Filter specifically by sshd command name |

A busy public host logs thousands of failed SSH attempts a day, which is noise rather than a break-in. Look for an Accepted line from an IP you do not recognise.

## User Services

--user reads the journal of your own systemd user manager. Without it you get the system journal, where user units do not appear.

| Command | What it does |
|----|----|
| journalctl --user | Everything your own user services logged, no sudo needed |
| journalctl --user -u syncthing | One user unit |
| journalctl --user -u syncthing -f | Follow a user unit live |
| journalctl --user -b -p err | Errors from your user services this boot |
| sudo journalctl \_UID=1000 \_SYSTEMD_USER_UNIT=app.service | Another user's user unit, read as root |
| journalctl \_UID=1000 --since today | Everything one user's processes logged today |

sudo journalctl --user shows root's user journal, not yours, which is a common five-minute detour.

## Output Formats

| Format Flag | Output Description |
|---|---|
| `-o short` | Default format (timestamp, hostname, unit, message) |
| `-o short-iso` | ISO-8601 timestamps (`YYYY-MM-DDTHH:MM:SS`) |
| `-o json` | One JSON object per log entry |
| `-o json-pretty` | Pretty-printed multiline JSON |
| `-o cat` | Message text only (strips timestamps and hostnames) |

Cursors give a script an exact resume point, so a cron job can process only what arrived since its last run without overlaps or gaps.

## Pager and Wrapping

Output goes through less, started with SYSTEMD_LESS=FRSXMK. The S in there chops long lines at the terminal width, which is why lines look cut off.

| Flag | Description |
|---|---|
| `--no-pager` | Pipe output directly to terminal without invoking `less` |
| `-e` | Jump immediately to end of log in pager |
| `--no-tail` | Show all lines regardless of buffer limits |

Set SYSTEMD_PAGER=cat in your shell profile to skip the pager permanently. -f never uses the pager, so Ctrl+C is what ends a follow.

## Export to a File

The pager is skipped automatically when output is not a terminal, so a plain redirect needs no --no-pager.

| Command | What it does |
|---|---|
| `journalctl -u nginx > nginx.log` | Dump service logs to text file |
| `journalctl --disk-usage` | Check current disk space used by journal archives |
| `sudo journalctl --vacuum-size=500M` | Reduce journal archive storage to maximum of 500 MB |
| `sudo journalctl --vacuum-time=7d` | Delete journal files older than 7 days |

## Disk Usage and Vacuum

| Command | What it does |
|----|----|
| journalctl --disk-usage | Total space the journal takes on disk |
| sudo journalctl --vacuum-size=500M | Delete oldest archived files until under 500 MB |
| sudo journalctl --vacuum-time=2weeks | Delete everything older than two weeks |
| sudo journalctl --vacuum-files=5 | Keep only the five newest journal files |
| sudo journalctl --rotate | Archive the active file so vacuum can reach it |
| journalctl --verify | Check journal files for corruption |

Vacuum only removes archived files, so --rotate first when you need space back now. To cap size permanently and keep logs across reboots, set both in /etc/systemd/journald.conf:

```
[Journal]
Storage=persistent
SystemMaxUse=500M
```

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
```

The edge case that bites: the default Storage=auto persists only if /var/log/journal already exists. Debian and Ubuntu ship the directory, so their logs survive reboots; RHEL and CentOS generally do not, so every boot starts the journal empty and journalctl -b -1 has nothing to show until you create it.

## Gotchas

- Empty output from journalctl -u name usually means a misspelled or different unit name, not missing logs. systemctl list-units --type=service settles it.
- journalctl -b -1 erroring with no persistent journal means the logs you want are already gone. Set up persistence today, before the crash you will want to debug.
- -p err shows err and everything worse, and it filters on the priority the service declared. Apps that write plain text to stdout log everything at info, so their errors do not surface under -p err; use -g for those.
- Timestamps print in the machine's local timezone. On servers set to UTC that is what you expect; on anything else, --utc avoids an hour of confusion during incident timelines.
- -g needs systemd 239 or newer. Older hosts (CentOS 7 and friends) pipe to grep instead.
- There is no exclude flag. journalctl matches are positive only, so to drop one noisy unit you either name the units you do want with repeated -u, or pipe through grep -v.
- Searching with -g reads every entry, while -u and other field matches use the journal index. Narrow by boot or time first and the same search finishes far quicker.
- Without sudo you see your own logs only, and journalctl says so in a hint at the top that is easy to scroll past. Add yourself to systemd-journal for read access without sudo.
- The journal and a service's own log files are separate worlds. nginx access logs live in /var/log/nginx/, not the journal; the journal has stdout, stderr and what systemd itself says about the unit. Unit state is the same split: systemctl --failed lists what is broken, journalctl only shows what it logged. The [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl) covers the service side.

## journalctl FAQ

### Where does journalctl store its logs?

In binary files under /var/log/journal/<machine-id>/ when the journal is persistent, and in /run/log/journal/ when it is not, which is memory and disappears at every reboot. The files are not text, so cat, tail and grep on them give you nothing useful; journalctl is the reader. Each user's services get their own user-1000.journal alongside system.journal in the same directory. You can also point journalctl at files it did not open itself: journalctl --file /var/log/journal/*/system.journal reads specific files, and journalctl -D /mnt/old/var/log/journal reads a whole journal directory from a mounted disk or a rescue boot, which is how you read the logs of a machine that no longer starts.

### How do I exit journalctl?

Press q. journalctl pipes output through less, so the prompt does not come back until the pager exits, and Ctrl+C there usually does nothing visible. Inside the pager, g jumps to the start, G to the end, /word searches forward and n repeats it. A live follow is the exception: -f skips the pager, so Ctrl+C is what stops it. To avoid the pager entirely, add --no-pager, or set SYSTEMD_PAGER=cat in your shell profile to make every journalctl run print straight to the terminal.

### Why is journalctl so slow?

Usually because the filter cannot use the journal's index. Field matches like -u, \_PID= and \_COMM= are indexed and stay quick on a large journal, while -g and a pipe into grep read every entry, and -r or -e have to walk to the far end before printing anything. Narrow first and search second: journalctl -b --since "1 hour ago" -g timeout finishes in a fraction of the time journalctl -g timeout takes. Check the size with journalctl --disk-usage, since a journal that has grown to several GB is worth vacuuming, and run journalctl --verify to rule out the corrupt files that make reads crawl.

### Do I need sudo to run journalctl?

Only for other people's logs. Any user can read their own messages and their own user services; the full system journal needs root or membership in systemd-journal, and most distributions also give the adm and wheel groups read access through an ACL on /var/log/journal. sudo usermod -aG adm alice fixes it for good, but group changes only apply to a new login session, so log out and back in before deciding it failed. Two traps: journalctl prints a single-line hint when it is hiding entries from you and it scrolls past easily, and sudo journalctl --user shows root's user journal rather than yours.

### How do I clear journalctl logs?

Vacuum it, do not delete it. Run sudo journalctl --rotate to archive the file currently being written, then sudo journalctl --vacuum-size=500M or sudo journalctl --vacuum-time=2weeks to remove the oldest archived files until the limit is met; it prints every file it deletes. Skipping the rotate step is why a vacuum often frees far less than expected, because the active file is never touched. Sizes take K, M and G suffixes. There is no way to clear the lines of a single service. To stop the journal growing back, set SystemMaxUse=500M in /etc/systemd/journald.conf; the default is 10% of the filesystem, capped at 4G.

---
Source: https://sshworkbench.com/cheatsheets/journalctl
