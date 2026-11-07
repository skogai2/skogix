# netstat Commands

netstat is still the fastest way to find out what is holding a port on Windows, while Linux has replaced it with ss and often does not install it at all. This sheet covers the Windows commands, the ss equivalent of every common netstat flag, and the filters, states, and output columns that go with them.

## What Is Using a Port

The most common reason either command gets run. Find the PID that owns the port, then name it.

| Command | What it does |
|---|---|
| `sudo ss -tulpn \| grep :80` | Modern, fast socket inspection showing process using port 80 |
| `sudo lsof -i :80` | List process name and PID listening on port 80 |
| `sudo fuser 80/tcp` | Show PID of process using port 80 |
| `sudo netstat -tulpn \| grep :80` | Legacy netstat command |

PowerShell does it in one step, no findstr and no second command:

```
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080 -State Listen).OwningProcess
```

For open files, sockets, and deleted-file handles beyond ports, see the [lsof cheat sheet](https://sshworkbench.com/cheatsheets/lsof).

## Windows netstat

netstat is not deprecated on Windows. Run these in Command Prompt or PowerShell; findstr is the Windows grep, and -b needs an elevated prompt.

| Command | Shell | Purpose |
|---|---|---|
| `netstat -ano \| findstr :80` | CMD / PowerShell | Find PID of process listening on port 80 on Windows |
| `Get-NetTCPConnection -LocalPort 80` | PowerShell | Native PowerShell cmdlet returning connection details |

## netstat to ss Mapping

netstat is deprecated on Linux; ss is the replacement and takes the same flag letters for the common cases. The last two rows moved to ip instead.

| netstat        | ss / ip    | What it shows                               |
|----------------|------------|---------------------------------------------|
| netstat -tlnp  | ss -tlnp   | Listening TCP ports with the owning process |
| netstat -ulnp  | ss -ulnp   | Listening UDP ports with the owning process |
| netstat -tunlp | ss -tunlp  | Both, one table                             |
| netstat -a     | ss -a      | All sockets, listening and connected        |
| netstat -tn    | ss -tn     | Current TCP connections, numeric            |
| netstat -s     | ss -s      | Summary statistics by protocol              |
| netstat -r     | ip route   | Routing table                               |
| netstat -i     | ip -s link | Interfaces with packet and error counters   |

The letters mean: t TCP, u UDP, l listening only, n numeric (skip DNS, always worth it), p process info (needs sudo for other users' processes), a all.

## Listening Ports

| Command | What it does |
|----|----|
| sudo ss -tlnp | Every listening TCP port and who owns it |
| sudo ss -tlnp \| grep :80 | Is something on port 80 |
| sudo ss -tlnp 'sport = :80' | Same, filtered by ss itself |
| sudo ss -tulnp | TCP and UDP listeners together |
| ss -tln state listening | Listening sockets without process info (no sudo needed) |
| sudo ss -tlnp \| grep sshd | Which port is sshd actually on |

If a port shows a listener bound to 127.0.0.1, it only accepts local connections; 0.0.0.0 or * means all interfaces. To test a port from the outside instead, use the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker).

## Established Connections

| Command | What it does |
|----|----|
| ss -tn | All current TCP connections |
| ss -tn state established | Only live connections |
| sudo ss -tnp state established | Live connections with the owning process |
| ss -tn state established '( dport = :443 )' | Outbound HTTPS connections |
| ss -tn 'dst 10.0.0.5' | Connections to one host |
| ss -tan state time-wait \| wc -l | How many sockets in TIME_WAIT |

Recipes:

```bash
# Who is connected to my web server right now, by IP:
ss -tn state established '( sport = :443 or sport = :80 )'

# Count connections by state (spot SYN floods and CLOSE_WAIT leaks):
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn

# Count established connections per client IP:
ss -tn state established | awk 'NR>1 {split($5,a,":"); print a[1]}' | sort | uniq -c | sort -rn
```

## Connection States

The State column is the TCP state machine. UDP rows have no state, which is why they look empty.

| State | What it means | When it matters |
|----|----|----|
| LISTEN | Server socket waiting for clients | Missing means nothing is bound to that port |
| ESTABLISHED | Handshake done, data can flow | One row per live connection |
| SYN_SENT | You asked to connect, nothing answered | Firewall dropping packets, or wrong host |
| SYN_RECV | Handshake half-finished on your side | Thousands of these is a SYN flood |
| TIME_WAIT | You closed it, kernel holds it ~60s | Normal in bulk; only hurts clients out of ports |
| CLOSE_WAIT | Peer closed, your app never did | Piles up only because of a bug in your program |
| FIN_WAIT_2 | You closed, peer never finished closing | Usually the peer crashed or was firewalled off |
| LAST_ACK | Waiting for the final ack before release | Transient; stuck ones mean a dead peer |

| Command | What it does |
|----|----|
| ss -s | Totals by state and protocol, one screen |
| ss -tan state close-wait | Every leaked socket, with the local port |
| netstat -ano \| find /c "TIME_WAIT" | Count TIME_WAIT sockets on Windows |
| netstat -ano \| findstr SYN_SENT | Connection attempts nothing is answering on Windows |

## ss Filters

ss filters sockets itself, no grep needed. Quote the expression, and put spaces around the parentheses and operators.

| Filter Syntax | Description |
|---|---|
| `ss -t state established` | List active established TCP connections |
| `ss -t state listening` | List listening TCP sockets only |
| `ss sport = :443` | Filter by local source port 443 |
| `ss dport = :22` | Filter by remote destination port 22 |
| `ss dst 192.168.1.0/24` | Filter by destination IP subnet |

## Routing Table and Stats

The parts of netstat that ss does not cover, and their modern forms.

| Command | Purpose |
|---|---|
| `ss -s` | Display summary socket statistics (TCP, UDP, RAW, established) |
| `ip route` | Display kernel routing table (modern replacement for `netstat -r`) |
| `ip -s link` | Show network interface packet statistics and errors |

## macOS netstat

macOS ships a BSD netstat with different flags, and no -p for processes (-p selects a protocol instead). Use lsof for the process view.

| macOS Command | Purpose |
|---|---|
| `netstat -anv -p tcp` | View TCP sockets with PIDs on macOS |
| `lsof -nP -iTCP:80 -sTCP:LISTEN` | Recommended method to inspect listening port 80 on macOS |

## netstat Flags

Two combinations cover most of it: netstat -tulpn on Linux, netstat -abno on Windows. The same letter often means something different on each.

| Flag | Meaning | Description |
|---|---|---|
| `-t` | TCP | Show TCP sockets |
| `-u` | UDP | Show UDP sockets |
| `-l` | Listening | Show listening sockets only |
| `-p` | Process | Show process PID and program name (requires root/sudo) |
| `-n` | Numeric | Show raw IP addresses and ports instead of resolving names |
| `-a` | All | Show both listening and established sockets |

## Reading the Output

Both tools print the same columns, in the same order, on every platform.

| Output Column | Meaning | Description |
|---|---|---|
| `Netid` | Protocol | Socket protocol (`tcp`, `udp`, `u_str`) |
| `State` | Socket State | `LISTEN`, `ESTAB`, `TIME-WAIT`, `CLOSE-WAIT` |
| `Recv-Q` / `Send-Q` | Queue Size | Bytes waiting in receive / send network buffers |
| `Local Address:Port` | Local Bind | Local IP and port bound by socket (`0.0.0.0:*` means all) |
| `Peer Address:Port` | Remote Host | Remote address and port |
| `Process` | Owner | Process name, PID, and file descriptor number |

## Install netstat

Only worth doing when a script insists on it; ss is already installed everywhere.

| Command | Distro |
|----|----|
| sudo apt install net-tools | Debian, Ubuntu ([apt cheat sheet](https://sshworkbench.com/cheatsheets/apt)) |
| sudo dnf install net-tools | Fedora, RHEL, Rocky, Alma |
| sudo yum install net-tools | RHEL 7 and older |
| sudo pacman -S net-tools | Arch |
| sudo zypper install net-tools | openSUSE |
| sudo apk add net-tools | Alpine, and most slim containers |

If apt install net-tools says it cannot locate the package, run sudo apt update first; the package list in a fresh container image is usually empty.

## Gotchas

- netstat: command not found on a modern distro is expected: the default answer is ss, and sudo apt install net-tools brings netstat back if a script insists on it.
- Without sudo, the -p column is blank for processes owned by other users, including every system service. No error, just missing names.
- Always add n. Without it both tools resolve every address and port name, which is slow and turns:22 into:ssh mid-scan.
- ss filter expressions are picky about spacing: '( dport = :443 )' works, '(dport=:443)' does not.
- A service bound to 127.0.0.1 will look fine in ss -tlnp but be unreachable from outside. Check the Local Address column, not just the port.
- On Windows, PID 4 is the kernel. http.sys parks ports there for IIS, WinRM, and WSL, so taskkill will not help; stop the service that registered the URL instead.
- A Windows port that refuses binds while netstat -ano shows nothing is usually inside a reserved range. netsh int ipv4 show excludedportrange protocol=tcp lists them, and Hyper-V grabs large blocks on every boot.
- Neither tool can look at another machine. Run it over SSH, or scan from outside with nmap.
- Connections you see in ss can still be invisible to clients if the firewall drops packets first. When listeners look right but connections fail, capture with [tcpdump](https://sshworkbench.com/cheatsheets/tcpdump) and check [iptables](https://sshworkbench.com/cheatsheets/iptables).

## netstat & ss FAQ

### How do I find which process is using a port?

On Windows, netstat -ano \| findstr :8080 puts the PID in the last column, then tasklist \| findstr 4312 names the program. Run it from an elevated prompt, or netstat -anob refuses with "The requested operation requires elevation" and prints "Could not obtain ownership information" for processes you do not own. On Linux, sudo ss -tlnp 'sport = :8080' shows the listener and its PID, and without sudo the process column is simply blank, with no error. On macOS, netstat cannot show processes at all, so use sudo lsof -i :8080. If Windows reports PID 4, the kernel holds the port through http.sys or a driver, and the fix is stopping the service behind it rather than killing the PID.

### Is netstat deprecated?

On Linux, yes. It ships in net-tools, which has had no real maintenance since 2011, and Debian, Ubuntu, RHEL, and Arch stopped installing it by default. The replacements are ss for sockets, ip route for the routing table, and ip -s link for interface counters. On Windows netstat is not deprecated, ships with every version, and netstat -ano is still the normal way to find what holds a port; Get-NetTCPConnection in PowerShell is an addition, not a replacement. macOS still ships the BSD netstat, which never had the Linux flags in the first place.

### What does TIME_WAIT mean in netstat output?

The side that closed the connection first holds the socket for twice the maximum segment lifetime, roughly 60 seconds on both Linux and Windows, so stray packets from the old connection cannot land in a new one reusing the same ports. Hundreds or thousands of TIME_WAIT rows on a busy server are normal and clear by themselves. It only becomes a real problem when a client machine runs out of ephemeral ports, and the answer there is connection reuse or keepalive, not net.ipv4.tcp_tw_recycle, which Linux removed in 4.12. CLOSE_WAIT is the state worth alerting on: it means your own program never closed a socket the other end closed already.

### Why is netstat so slow?

By default it resolves every address to a hostname and every port number to a service name, so a single DNS timeout stalls the whole listing. Add n (netstat -an, ss -tn) and it returns straight away. On Windows, -b is slow for a different reason: it walks the loaded modules of every process to name the executable, so netstat -ano plus tasklist is much quicker. ss beats netstat even with -n, because it asks the kernel over netlink instead of parsing /proc/net/tcp line by line, which shows on hosts with thousands of sockets.

### Can I run netstat on a remote machine?

No. netstat and ss read the local kernel's socket tables and have no remote mode. To see another machine's sockets, run the command over SSH: ssh user@host 'ss -tlnp'. To find out what is reachable from outside instead, scan from your side with nmap or test a single port with the SSH port checker. That answers a different question, and usually the more useful one when the listener looks correct locally but clients still cannot connect.

---
Source: https://sshworkbench.com/cheatsheets/netstat-ss
