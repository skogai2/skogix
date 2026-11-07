# tcpdump Command Examples

tcpdump is the packet capture tool on every Linux box, and it needs root, so prefix everything here with sudo. This sheet covers the filters people actually type, how to read a capture line once it scrolls past, and how to write a pcap file you can open in Wireshark.

Last updated September 11, 2026

On this page

- [Basics](#basics)
- [Reading the Output](#reading-the-output)
- [Host and Port Filters](#host-and-port-filters)
- [Combining and Excluding](#combining-and-excluding)
- [Protocols](#protocols)
- [Saving Captures](#saving-captures)
- [Stopping and Rotating](#stopping-and-rotating)
- [Wireshark Handoff](#wireshark-handoff)
- [Payloads and Hex](#payloads-and-hex)
- [MAC and VLAN Filters](#mac-and-vlan-filters)
- [BPF Syntax](#bpf-syntax)
- [Installing tcpdump](#installing-tcpdump)
- [Gotchas](#gotchas)

## Basics

tcpdump needs root. Every command here assumes sudo, and Ctrl+C stops a capture.

[TABLE]

## Reading the Output

A line is timestamp, source, destination, then the TCP state in brackets. This is one SYN opening a connection to port 443:

```
14:22:31.478934 IP 10.0.0.9.52344 > 10.0.0.5.443: Flags [S], seq 1829375192, win 64240, length 0
```

Copy

[TABLE]

The dot inside the brackets is the ACK bit, so \[P.\] means push plus ack.

[TABLE]

Non-TCP lines have their own shapes:

| Line | What it means |
|----|----|
| ARP, Request who-has 10.0.0.5 tell 10.0.0.9 | 10.0.0.9 is asking which MAC owns that IP |
| ARP, Reply 10.0.0.5 is-at aa:bb:cc:dd:ee:ff | The answer, with the MAC address |
| ICMP echo request, id 1, seq 1, length 64 | A ping leaving the host |
| ICMP 10.0.0.5 udp port 53 unreachable | Nothing is listening on that UDP port |
| 10.0.0.9.52344 \> 10.0.0.5.53: 4919+ A? example.com. (29) | A DNS query for an A record ([dig](https://sshworkbench.com/cheatsheets/dig) asks the same thing on purpose) |

## Host and Port Filters

Quote any filter that has more than one word so the shell leaves it alone.

| Command | What it does |
|----|----|
| tcpdump -i any host 10.0.0.5 | Traffic to or from one IP |
| tcpdump -i any src 10.0.0.5 | Traffic coming from an IP |
| tcpdump -i any dst 10.0.0.5 | Traffic going to an IP |
| tcpdump -i any port 443 | Traffic on a port, either direction |
| tcpdump -i any src port 22 | Traffic from a source port |
| tcpdump -i any dst port 3306 | Traffic to a destination port |
| tcpdump -i any portrange 8000-8100 | A range of ports |
| tcpdump -i any net 10.0.0.0/24 | Traffic to or from a whole subnet |
| tcpdump -i any 'dst 10.0.0.5 and dst port 80' | To one IP on one port |
| tcpdump -i any 'host example.com' | Resolves the name once at startup, then filters on the IPs |

## Combining and Excluding

and, or, and not combine primitives; parentheses group them. Always quote the whole expression, or the shell will grab the special characters first.

| Command | What it does |
|----|----|
| tcpdump -i any 'port 80 and host 10.0.0.5' | One host's traffic on port 80 |
| tcpdump -i any 'host 10.0.0.5 and host 10.0.0.9' | Only the conversation between two hosts |
| tcpdump -i any 'port 80 or port 443' | Either of two ports |
| tcpdump -i any 'not port 22' | Everything except SSH (essential when capturing over SSH) |
| tcpdump -i any 'not host 10.0.0.5' | Exclude one noisy machine |
| tcpdump -i any 'not port 22 and not port 53' | Exclude SSH and DNS together |
| tcpdump -i any 'src 10.0.0.5 and not dst port 53' | From a host, minus its DNS lookups |
| tcpdump -i any 'tcp and (port 80 or port 443)' | Grouping with parentheses |
| tcpdump -i any 'host 10.0.0.5 or host 10.0.0.9' | Two hosts, each with anyone |

## Protocols

A bare protocol name is a filter on its own, and it combines with everything above.

[TABLE]

## Saving Captures

Write with -w, analyze later with -r or Wireshark. Terminal output stops while writing to a file; add -v to see a packet count tick up.

| Command | What it does |
|----|----|
| tcpdump -i eth0 -w capture.pcap | Write raw packets to a file |
| tcpdump -i eth0 -s0 -w capture.pcap | Full packets, not truncated (do this for Wireshark) |
| tcpdump -i eth0 -c 1000 -w capture.pcap | Capture 1000 packets, then stop |
| tcpdump -i eth0 -U -w capture.pcap | Write each packet immediately instead of buffering |
| tcpdump -r capture.pcap | Read a capture back |
| tcpdump -nr capture.pcap | Read it back without resolving anything |
| tcpdump -r capture.pcap 'port 443' | Filter while reading (filters work on files too) |
| tcpdump -r big.pcap 'host 10.0.0.5' -w small.pcap | Cut a big capture down to one host |

## Stopping and Rotating

Nothing stops a capture on its own, and a busy interface fills a disk faster than you expect.

| Command | What it does |
|----|----|
| tcpdump -i eth0 -c 500 -w cap.pcap | Stop after 500 packets |
| timeout 30 tcpdump -i eth0 -w cap.pcap | Stop after 30 seconds |
| tcpdump -i eth0 -w cap.pcap -C 100 -W 5 | Rotate at 100 MB, keep 5 files |
| tcpdump -i eth0 -G 3600 -w 'cap-%H%M.pcap' | Start a new file every hour |
| tcpdump -i eth0 -G 3600 -W 24 -w 'cap-%H.pcap' | Hourly files, one day, then overwrite |
| tcpdump -i eth0 -w cap.pcap -z gzip | Gzip each file as it rotates |
| nohup tcpdump -i eth0 -w cap.pcap & | Leave it running after you log out |

-G needs strftime placeholders (%H, %M) in the filename, or every rotation overwrites the same file.

## Wireshark Handoff

Capture on the server, analyze on your desktop. Wireshark opens .pcap and .pcapng directly.

| Command | What it does |
|----|----|
| tcpdump -i eth0 -s0 -w capture.pcap | Capture full packets so nothing is half-parsed |
| scp user@host:capture.pcap . | Copy the file down to your machine |
| tcpdump -r big.pcap 'port 443' -w small.pcap | Trim a huge capture before opening it |
| ssh user@host 'sudo tcpdump -i eth0 -U -s0 -w -' \| wireshark -k -i - | Stream a remote capture into Wireshark live |
| tshark -r capture.pcap | Wireshark's decoders, in the terminal |
| editcap -c 100000 big.pcap part.pcap | Split a capture into 100k-packet files |

## Payloads and Hex

[TABLE]

TLS traffic on 443 shows only gibberish with -A. That is the encryption working, not a tcpdump problem.

```
# Busiest source addresses in a saved capture:
sudo tcpdump -nr capture.pcap | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head
```

Copy

## MAC and VLAN Filters

For layer 2 problems: DHCP fights, ARP mysteries, tagged frames, finding a device with no IP yet.

| Command | What it does |
|----|----|
| tcpdump -i eth0 ether host aa:bb:cc:dd:ee:ff | Traffic to or from one MAC |
| tcpdump -i eth0 ether src aa:bb:cc:dd:ee:ff | Frames sent by a MAC |
| tcpdump -i eth0 -e | Show MAC addresses on every line |
| tcpdump -i eth0 ether broadcast | Broadcast frames only |
| tcpdump -i eth0 -e vlan | Tagged frames, with the VLAN id visible |
| tcpdump -i eth0 'vlan 100' | One VLAN only |
| tcpdump -i eth0 'vlan and port 80' | Port 80 inside a tagged frame |
| tcpdump -i eth0 multicast | Multicast frames (routing chatter, mDNS) |

vlan shifts every offset that follows it, so it has to come first in the expression. 'port 80 and vlan' matches nothing useful.

## BPF Syntax

Filters compile to Berkeley Packet Filter programs, and the bracket syntax reads raw bytes: proto\[offset\] is a byte within that protocol's header. The practical use is matching TCP flags.

| Filter | What it matches |
|----|----|
| 'tcp\[tcpflags\] & tcp-syn != 0' | Any packet with SYN set (new connections) |
| 'tcp\[tcpflags\] == tcp-syn' | SYN only, no ACK (inbound connection attempts) |
| 'tcp\[tcpflags\] & (tcp-syn\|tcp-ack) == tcp-syn' | Same, spelled with a mask |
| 'tcp\[tcpflags\] & tcp-rst != 0' | Resets (something refusing connections) |
| 'tcp\[tcpflags\] & tcp-fin != 0' | Connection teardowns |
| 'tcp\[13\] & 2 != 0' | SYN again, by raw offset (13 is the flags byte) |
| 'greater 1000' | Packets of at least 1000 bytes |

```
# Who is trying to open connections to this box, live:
sudo tcpdump -i any -n 'tcp[tcpflags] == tcp-syn'

# Check what a filter compiles to without capturing:
sudo tcpdump -d 'tcp[tcpflags] & tcp-syn != 0'
```

Copy

## Installing tcpdump

[TABLE]

tcpdump lives in /usr/sbin, which is not on a normal user's PATH on Debian and Ubuntu. Running it under sudo finds it; typing tcpdump as yourself often does not.

## Gotchas

- packets dropped by kernel
  at the end means tcpdump could not keep up. Add
  -n
  , write to a file with
  -w
  instead of printing, and narrow the filter;
  -B 4096
  raises the capture buffer.
- syntax error in filter expression
  is usually the shell eating your quotes. Wrap any multi-word filter in single quotes, and check keywords (
  portrange
  , not
  port-range
  ).
  -d
  compiles a filter without capturing, so you can test one in a second.
- Capturing over SSH shows you your own SSH packets, which generate more packets, forever. Start every remote capture with
  'not port 22'
  .
- -i any
  sees all interfaces but cannot use promiscuous mode, so it misses traffic not addressed to the host. Switch to the real interface once you know it.
- Old tcpdump versions truncated packets at 68 bytes by default. Modern ones capture full packets, but
  -s0
  still makes the intent explicit for files headed to Wireshark.
- checksum incorrect
  on outgoing packets is almost always checksum offload: the NIC fills the field in after tcpdump has already seen the packet. Nothing is wrong.
- tcpdump has no idea which process sent a packet. Map the port to a PID with [ss](https://sshworkbench.com/cheatsheets/netstat-ss) or [lsof](https://sshworkbench.com/cheatsheets/lsof), then go back to the capture.
- tcpdump shows packets arriving; it does not show what the firewall then drops. Compare with your [iptables rules](https://sshworkbench.com/cheatsheets/iptables) when packets arrive but the service never sees them.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## tcpdump FAQ

### Does tcpdump show packets dropped by iptables?

On the way in, yes. tcpdump taps the device layer before netfilter sees the packet, so an inbound packet appears in your capture even when an INPUT rule drops it a moment later. A capture full of SYNs with no reply is the classic signature of a firewall, not a broken network. Outbound works the other way round: tcpdump sees packets after the OUTPUT chain, so anything your own rules drop never reaches the capture at all. Confirm either way with iptables -L -v -n and watch the packet counters move.

### Can I run tcpdump without root?

Yes, with file capabilities: sudo setcap cap_net_raw,cap_net_admin+eip \$(which tcpdump) lets your normal user capture, until the next package upgrade replaces the binary and resets it. There is a second thing to know either way. After tcpdump opens the interface it drops privileges to the unprivileged tcpdump user, so any directory you write -w files into has to be writable by that user, not just by you. /tmp works, a root-owned directory fails with a permission error even under sudo.

### Why is tcpdump not showing any packets?

Almost always one of four things. The interface is wrong, so run tcpdump -D and fall back to -i any until you know where traffic flows. The filter is too tight, so drop it completely, confirm packets appear, then add it back one primitive at a time. The traffic never touches that interface, which is normal on container and VM hosts where packets ride a bridge like docker0 or a veth pair. Or the traffic exists but never reaches your NIC, because a switch only forwards the host its own traffic unless someone configured a mirror port.

### When should I use tcpdump instead of Wireshark?

Use tcpdump to get the packets and Wireshark to understand them. tcpdump is already installed on the server, needs no desktop session, and is cheap enough to leave running, so it wins for capturing remotely and for quick checks where you only need to know whether packets arrive. Wireshark is where you follow a TCP stream, read a TLS handshake, or chase one retransmission through a thousand packets. The normal workflow uses both: capture with -w, copy the file down, open it. For Wireshark's decoders in a terminal, tshark reads the same files.

### Where does tcpdump save the capture file?

Nowhere, unless you ask. Without -w it prints to the terminal and keeps nothing. With -w capture.pcap the file lands in the working directory of the shell you launched it from, which under sudo is still your own directory rather than root's. Pass an absolute path such as -w /tmp/capture.pcap when you are not sure where you are. Nothing is written until the buffer flushes either, so a file can look empty until you stop the capture with Ctrl+C or add -U to write packet by packet.

---
Källa: https://sshworkbench.com/cheatsheets/tcpdump
