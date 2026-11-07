# strace Examples

strace prints every system call a program makes, which is how you find the file it cannot open, the socket it cannot reach, or the spot where it hangs. This sheet covers attaching to a running process, filtering the syscalls you care about, and reading what comes back.

Last updated September 11, 2026

On this page

- [Attach to a Running Process](#attach-to-a-running-process)
- [Find a Missing File or Config](#find-a-missing-file-or-config)
- [Run a Command Under strace](#run-a-command-under-strace)
- [Filter Syscalls](#filter-syscalls)
- [Follow Forks and Threads](#follow-forks-and-threads)
- [Save Output to a File](#save-output-to-a-file)
- [Timestamps and Timing](#timestamps-and-timing)
- [Summary Mode](#summary-mode)
- [Full Strings](#full-strings)
- [Reading the Output](#reading-the-output)
- [Network Calls](#network-calls)
- [Common Errors](#common-errors)
- [strace vs ltrace](#strace-vs-ltrace)
- [Gotchas](#gotchas)

strace needs root or the same user that owns the process, and it slows the traced program down a lot, so filter early and detach when you are done.

## Attach to a Running Process

Ctrl+C detaches from a process you attached to; it keeps running.

| Command | What it does |
|----|----|
| sudo strace -p 1234 | Attach to PID 1234 and print its syscalls live |
| sudo strace -f -p 1234 | Follow its threads and child processes too |
| sudo strace -p \$(pgrep -n nginx) | Attach to the newest process matching a name |
| sudo strace -f -p \$(systemctl show -P MainPID nginx) | Attach to a systemd service by unit name |
| sudo strace -p 1234 -o /tmp/trace.log | Write to a file instead of the screen |
| sudo strace -p 1234 -e trace=network | Attach, but show only network calls |
| sudo strace -c -p 1234 | Count calls instead of printing them; Ctrl+C prints the table |
| sudo strace -tt -T -p 1234 | Add clock timestamps and per-call duration |
| sudo strace -p 1234 -p 5678 | Attach to several processes at once |

Find the PID first with [ps](https://sshworkbench.com/cheatsheets/ps), pgrep -a nginx, or pidof nginx.

## Find a Missing File or Config

The everyday use: a program starts, says nothing useful, and quits. Trace what it tried to open and look for ENOENT.

| Command | What it does |
|----|----|
| strace -e trace=openat ./app | Show only file opens |
| strace -e trace=file ./app | Every call that takes a filename (open, stat, access, unlink) |
| strace -f -e trace=file ./app 2\>&1 \| grep ENOENT | List the files it looked for and did not find |
| strace -f -e trace=file -e status=failed ./app | Same idea without the pipe (strace 5.2 and newer) |
| strace -e trace=openat -o open.log ./app | Save the opens to read later |
| sudo strace -f -e trace=file -p 1234 2\>&1 \| grep -v ENOENT | Files a running process actually reached |

What it looks like:

```
openat(AT_FDCWD, "/etc/myapp/config.yml", O_RDONLY) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/usr/local/etc/myapp/config.yml", O_RDONLY) = 3
```

Copy

The first path is the one it wanted and did not find, the second is the one it settled for. ENOENT on a path you expected to exist is the answer most of the time; EACCES means the file is there and the permissions are not. The same trick finds missing shared libraries, which show up as failed openat calls on .so files.

## Run a Command Under strace

| Command | What it does |
|----|----|
| strace ls | Run the command and print every syscall it makes |
| strace -f ./start.sh | Follow the children a shell script spawns |
| strace -o trace.log ./app --port 8080 | The program's own flags come after it, as usual |
| strace -e trace=openat,read,write ./app | Only the syscalls you name |
| strace -c ./app | Run to the end, then print a summary table |
| sudo strace -u www-data ./app | Run it as another user (needs root) |
| strace -E DEBUG=1 ./app | Set an environment variable for the traced run |
| strace -s 4096 ./app | Print long strings in full instead of cutting at 32 characters |

Ctrl+C here kills the program, unlike Ctrl+C on an attached process.

## Filter Syscalls

-e trace= takes syscall names, or a class that stands for a whole group. Filtering is also the cheapest way to cut the slowdown.

[TABLE]

## Follow Forks and Threads

Without -f, strace watches one process. A program that does its real work in a child or a worker thread looks idle.

[TABLE]

With -f, every line gains a \[pid 2412\] prefix so you can tell the processes apart. See [grep](https://sshworkbench.com/cheatsheets/grep) for sifting the files -ff leaves behind.

## Save Output to a File

strace writes to stderr, not stdout, so strace ./app \> out.txt saves the program's output and none of the trace.

[TABLE]

## Timestamps and Timing

[TABLE]

sudo strace -tt -T -p 1234 is the pair for "which call is the slow one". Read -T as time spent inside the kernel, and -r as the pause before the call, which is usually where the waiting really happened.

## Summary Mode

[TABLE]

```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 62.19    0.004312          14       298        12 openat
 18.02    0.001249           3       402           read
 11.44    0.000793           9        88         3 connect
```

Copy

The errors column is the one to read first: twelve failed openat calls points at a missing file, not a slow disk.

## Full Strings

strace cuts string arguments at 32 characters and marks the cut with ..., which is why the path or payload you wanted is half there.

| Command | What it does |
|----|----|
| strace -s 4096 ./app | Print up to 4096 characters per string |
| strace -v -s 4096 ./app | Also expand structures and environments instead of abbreviating |
| strace -xx -s 4096 ./app | Print non-printable bytes as hex |
| strace -e read=3 ./app | Hex and ASCII dump of everything read from fd 3 |
| strace -e write=1,2 ./app | Dump everything written to stdout and stderr |
| strace -y -p 1234 | Print the path behind every file descriptor number |
| strace -yy -p 1234 | Also print the address and protocol behind socket fds |

## Reading the Output

```
[pid  2412] openat(AT_FDCWD, "/etc/hosts", O_RDONLY|O_CLOEXEC) = 3
[pid  2412] read(3, "127.0.0.1 localhost\n", 4096) = 20
[pid  2412] connect(4, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("93.184.216.34")}, 16) = -1 EINPROGRESS (Operation now in progress)
[pid  2412] +++ exited with 0 +++
```

Copy

[TABLE]

The fd number is the thread to pull: find the openat or socket that returned it, and you know what every later read, write, and close on that number is really touching. -y prints the path next to the fd so you do not have to scroll back.

## Network Calls

| Command | What it does |
|----|----|
| sudo strace -f -e trace=%network -p 1234 | Every socket, connect, send, and receive |
| sudo strace -f -e trace=connect -yy -p 1234 | Outgoing connections with the resolved address |
| strace -f -e trace=%network -e status=failed ./app | Only the network calls that failed |
| strace -e trace=openat ./app 2\>&1 \| grep resolv.conf | Check whether it read the DNS config at all |
| strace -f -e trace=connect ./app 2\>&1 \| grep ":53" | Catch the DNS lookups themselves |
| sudo strace -e trace=bind,listen -p 1234 | Which address and port it tried to take |

ECONNREFUSED means nothing is listening, ETIMEDOUT means packets are going nowhere, and EADDRINUSE means something else already has the port. Use [lsof](https://sshworkbench.com/cheatsheets/lsof) to find the owner, and [tcpdump](https://sshworkbench.com/cheatsheets/tcpdump) when you need the packets rather than the calls.

## Common Errors

[TABLE]

A failed call is not automatically the bug. Programs probe paths on purpose, so a handful of ENOENT hits followed by a success is normal. The interesting one is the failure with nothing after it.

## strace vs ltrace

[TABLE]

Both drive the same ptrace machinery, so both stop the process on every event. For tracing you can leave running on a live server, use perf trace or bpftrace instead.

## Gotchas

- ptrace_scope
  blocks most attaches. On Ubuntu and most desktop distros
  kernel.yama.ptrace_scope
  is
  1
  , so you can only trace your own children.
  sudo strace -p
  gets around it;
  sudo sysctl kernel.yama.ptrace_scope=0
  lowers it until reboot, and a file in
  /etc/sysctl.d/
  makes that permanent.
- Containers drop the capability. Add
  --cap-add=SYS_PTRACE
  to
  docker run
  , or put
  SYS_PTRACE
  in the pod's
  securityContext.capabilities.add
  .
- The slowdown is real. Ten times slower is common on a syscall-heavy process, and timeouts elsewhere can fire while you watch. Narrow with
  -e
  , write to
  -o
  , detach quickly.
- The trace goes to stderr. Any pipe or redirect needs
  2\>&1
  , or use
  -o
  and skip the problem.
- strace is not installed on minimal images:
  sudo apt install strace
  ,
  sudo dnf install strace
  ,
  sudo apk add strace
  .
- Nothing on screen usually means the process is parked in
  epoll_wait
  ,
  accept
  , or
  futex
  waiting for work. Send it a request, or check [journalctl](https://sshworkbench.com/cheatsheets/journalctl) to see what it thinks it is doing.

### See processes without the flag soup

SSH Workbench shows live CPU, memory, and process lists for every server over plain SSH, with kill and restart as buttons instead of PIDs.

[Try free for 7 days](https://sshworkbench.com/#install)

## strace FAQ

### How do I read strace output?

Every line has the same shape: the syscall name, its arguments in parentheses, an equals sign, and the return value. openat(AT_FDCWD, "/etc/hosts", O_RDONLY) = 3 means the program opened /etc/hosts and got file descriptor 3 back, so every later read(3, ...) and close(3) on that fd is the same file. A return of -1 followed by a capitalised name is a failure, and that name is the errno: ENOENT is a missing file, EACCES is permissions. Flags are ORed together, which is why you see pipes in O_RDONLY\|O_CLOEXEC. Lines beginning with \[pid 2412\] appear once you add -f, --- SIGTERM --- is a signal arriving, and +++ exited with 1 +++ is the end. Read it backwards from the failure, not forwards from the top.

### Why does strace say ptrace: Operation not permitted?

Three things cause it. Most often the kernel's Yama policy is blocking you: on Ubuntu and most desktop distros kernel.yama.ptrace_scope is 1, which only lets you trace your own children. Run strace with sudo, or lower it for the session with sudo sysctl kernel.yama.ptrace_scope=0. Second, you are not root and not the user that owns the process, which ptrace never allows. Third, you are inside a container, where the SYS_PTRACE capability is dropped by default; start the container with --cap-add=SYS_PTRACE, or on Kubernetes set securityContext.capabilities.add: \["SYS_PTRACE"\]. A process already being traced by gdb or another strace also refuses a second tracer.

### Does strace slow the process down?

Yes, badly. Every traced syscall stops the process twice while strace inspects it, so a syscall-heavy workload can run ten to a hundred times slower under strace. A quiet process that mostly waits barely notices, but a busy web server or database will visibly stall, and timeouts elsewhere can start firing. Keep the window short, narrow the trace with -e trace=openat or -e trace=network so fewer calls stop the process, write to a file with -o instead of a slow terminal, and detach with Ctrl+C as soon as you have what you need. For anything you need to leave running on a production box, use perf trace or bpftrace instead, which do not use ptrace.

### Why does strace show nothing?

Usually the process is idle rather than broken. A server parked in accept, epoll_wait, futex, or poll is waiting for work and makes no syscalls until something arrives, so send it a request and watch the output appear. The other common cause is that the work happens somewhere you are not watching: add -f so strace follows threads and child processes, since without it strace only sees the process you named. If you piped the output to grep and got nothing, remember strace writes to stderr, so you need strace ./app 2\>&1 \| grep ENOENT or -o to a file. And a filter with a typo in the syscall name silently matches nothing.

### Is there a strace for macOS or Windows?

Not the same tool. macOS has dtruss (a DTrace script) and ktrace, but System Integrity Protection blocks tracing of most system binaries, so you can only trace your own unsigned programs, and only with sudo. A practical alternative there is sudo fs_usage -w -f filesys for file activity. On Windows, Sysinternals Process Monitor covers the same ground with a GUI: file, registry, and network operations per process, with filters. Real strace runs fine inside WSL2, but only against Linux processes in that environment, not against Windows executables.

---
Källa: https://sshworkbench.com/cheatsheets/strace
