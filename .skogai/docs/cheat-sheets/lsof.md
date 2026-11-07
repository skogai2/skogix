# lsof Examples

lsof lists open files, and on Linux a socket, a directory and a mount point are all files, so it answers both 'what is using port 8080' and 'what is keeping this filesystem busy'. This sheet covers the filters worth remembering and how to read the columns that come back.

## Ports

The question is almost always "what is holding port 8080". -i takes a port on its own or with a protocol in front of it.

| Command | What it does |
|---|---|
| `sudo lsof -i :80` | Find process listening on or connected to port 80 |
| `sudo lsof -iTCP:443 -sTCP:LISTEN` | Find process strictly listening on HTTPS port 443 |
| `sudo lsof -i :22-25` | Inspect range of ports from 22 to 25 |
| `sudo lsof -i udp:53` | Inspect UDP port 53 (DNS) |

Free the port, then confirm it is free:

```bash
sudo lsof -i :8080                   # who has it
kill $(sudo lsof -ti :8080)          # ask them to stop
kill -9 $(sudo lsof -ti :8080)       # make them stop
```

Without sudo you see only your own processes, so a port held by root reads as free. For a plain list of listeners, ss -tlnp is faster; see the [netstat and ss sheet](https://sshworkbench.com/cheatsheets/netstat-ss).

## Files and Mounts

The other everyday job: something will not unmount, or a file will not delete.

| Command | What it does |
|---|---|
| `lsof /var/log/nginx/access.log` | List processes currently holding specified file open |
| `lsof +D /var/log/` | Recursively list all open files under directory |
| `lsof /mnt/storage` | Identify processes holding mountpoint busy (preventing unmount) |

lsof reads a path as a filesystem when it matches a mount point from mount, and as a single file otherwise. That is why lsof /mnt/data lists hundreds of rows and lsof /mnt/data/file.db lists one.

## Processes and Users

| Command | What it does |
|---|---|
| `lsof -p 1234` | List all open file descriptors belonging to PID 1234 |
| `lsof -u www-data` | List all files opened by user `www-data` |
| `lsof -c nginx` | List all files opened by processes starting with command name `nginx` |

## Deleted Files

The classic case: df says the disk is full, du says it is not. A process is holding a file that no longer has a name, and the space comes back only when the descriptor closes.

| Command | What it does |
|----|----|
| sudo lsof +L1 | Open files with no directory entry left, the ones eating the space |
| sudo lsof +L1 /var | Same, limited to one filesystem |
| sudo lsof -nP \| grep '(deleted)' | The [grep](https://sshworkbench.com/cheatsheets/grep) version, works on any lsof build |
| sudo lsof -p 1234 \| grep deleted | What one process is still holding |

```bash
sudo lsof +L1                    # find the holder: note its PID and FD
sudo systemctl restart rsyslog   # cleanest fix, restart the owner
: > /proc/1234/fd/7              # or empty the file in place, no restart
```

Deleting a log file that a service is writing to is what causes this. Truncate with : > file or hand it to logrotate instead.

## Network Connections

| Command | What it does |
|---|---|
| `lsof -i 4` | List all open IPv4 network sockets |
| `lsof -i 6` | List all open IPv6 network sockets |
| `lsof -i @192.168.1.50` | Filter connections involving specific remote IP address |

lsof names the process behind a connection; [tcpdump](https://sshworkbench.com/cheatsheets/tcpdump) shows what that connection is sending.

## Output Columns

Half of using lsof is reading what it printed.

```
COMMAND   PID  USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME
nginx    1234  root    6u  IPv4  28134      0t0    TCP *:80 (LISTEN)
nginx    1234  root   11w   REG  253,0   184320 264781 /var/log/nginx/access.log
sshd      902  root    3u  IPv6  21883      0t0    TCP 10.0.0.5:22->10.0.0.9:51544 (ESTABLISHED)
```

| Column | Meaning | Description |
|---|---|---|
| `COMMAND` | Process Name | Executable name of the process |
| `PID` | Process ID | Numeric PID of process |
| `USER` | User | User owning the process |
| `FD` | File Descriptor | `cwd` (working dir), `txt` (binary code), or numeric (`0u`, `1w`, `3r`) |
| `TYPE` | File Type | `REG` (regular file), `DIR` (directory), `CHR` (char device), `IPv4` |
| `NAME` | Target Name | Full file path, unix socket path, or IP connection string |

FD is the column people misread. It is either a number with a mode letter or one of these keywords:

| Column | Meaning | Description |
|---|---|---|
| `COMMAND` | Process Name | Executable name of the process |
| `PID` | Process ID | Numeric PID of process |
| `USER` | User | User owning the process |
| `FD` | File Descriptor | `cwd` (working dir), `txt` (binary code), or numeric (`0u`, `1w`, `3r`) |
| `TYPE` | File Type | `REG` (regular file), `DIR` (directory), `CHR` (char device), `IPv4` |
| `NAME` | Target Name | Full file path, unix socket path, or IP connection string |

## Output Flags

| Flag | Meaning | Purpose |
|---|---|---|
| `-t` | Terse | Output PIDs only (ideal for `kill $(lsof -t -i :80)`) |
| `-F` | Field Output | Format output for script parsers |
| `-n` | No Hostnames | Do not resolve IP addresses to hostnames (much faster) |
| `-P` | No Port Names | Do not resolve port numbers to service names |

-n -P together is worth making a habit. It removes both lookups and turns a command that takes seconds into one that returns straight away.

## Combining Filters

Filters of different kinds OR together by default, which catches almost everyone out. -a turns the whole line into AND.

| Option / Logic | Example | Meaning |
|---|---|---|
| Default (OR logic) | `lsof -u alice -c bash` | Files opened by user `alice` OR command `bash` |
| `-a` (AND logic) | `lsof -a -u alice -i` | Files opened by user `alice` AND that are network sockets |

-a applies to the entire command line. There is no way to AND one pair of options while leaving another pair as OR; run two commands instead.

## Gotchas

- Without sudo, lsof quietly shows only your own processes. An empty result is not proof that a port or file is free.
- lsof is not installed on minimal Debian, Ubuntu and RHEL images. sudo apt install lsof or sudo dnf install lsof.
- -i :8080 matches listeners and connections to that port. Add -sTCP:LISTEN when you want the server alone.
- There is no JSON output. -F is the parseable format: one field per line, each prefixed by a letter, and -F pcn keeps it to PID, command and name.
- warning: can't stat() lines are normal on machines with fuse or gvfs mounts. -w hides them and the results are unaffected.
- Inside a container, lsof sees that container's namespace only. Run it on the host to find who really owns a port.
- On macOS, lsof -i is the way to map a port to a process, because netstat there cannot show process names at all.

## lsof FAQ

### How do I find and kill the process using a port?

sudo lsof -i :8080 names it, and sudo lsof -ti :8080 prints the PID on its own, so kill -9 $(sudo lsof -ti :8080) clears the port in one line. Run it with sudo: without it you only see your own processes, and a port held by root or www-data looks free. Add -sTCP:LISTEN if you want the server and not every client connected to it. A multi-worker server has several PIDs on the same port, -t prints them all, and kill takes the whole list.

### What do the FD and TYPE columns in lsof output mean?

FD is the file descriptor: a number plus a mode letter, where r is read, w is write and u is both, with a trailing W or R when the process holds a lock. Some rows show a keyword instead of a number: cwd is the working directory, rtd the root directory, txt the executable itself, mem a memory-mapped library, DEL a mapped file that has been deleted. TYPE says what kind of file it is: REG a regular file, DIR a directory, CHR a terminal or device, FIFO a pipe, IPv4 and IPv6 sockets, unix a socket file.

### Why does lsof return nothing?

Usually permissions. lsof only shows files owned by processes you can see, so without sudo a port held by another user comes back empty rather than with an error. Run sudo lsof -i :8080. Other causes: the port really is free, so the connection attempt would be refused; you searched a path instead of a mount point, which matches only that exact file; or you are inside a container, where lsof sees the container's namespace and not the host. If the shell says command not found instead, lsof is not installed.

### Why is lsof so slow, or why does it hang?

By default lsof resolves every IP to a hostname and every port number to a service name, and it stats every mounted filesystem. Add -n and -P to skip both lookups and the same command usually returns instantly. If it freezes rather than crawls, a network mount is the cause: a hung NFS server blocks the stat call forever, and -b tells lsof to skip the calls that can block. +D on a large tree is slow for a different reason, it walks every directory below the path.

### df says the disk is full but du does not, how do I find the file?

A process still has a deleted file open, so the space is not released until it closes. sudo lsof +L1 lists open files with no directory entry left, and the SIZE column shows how much each is holding. The usual culprit is a log file someone removed instead of truncating while the service kept writing to it. Restart the owning service to release the space, or on Linux empty the file in place without a restart: : > /proc/PID/fd/7, using the PID and FD number from the lsof row.

---
Source: https://sshworkbench.com/cheatsheets/lsof
