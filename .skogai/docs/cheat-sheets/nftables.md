# nftables Cheat Sheet

nftables is the firewall that replaced iptables in the Linux kernel, driven by a single nft command. This sheet covers listing the ruleset, adding and deleting rules by handle, the match syntax, sets, NAT, rate limits, logging, keeping rules across a reboot, and translating the iptables rules you already have.

## Listing Rules

Everything here needs root. nft prints nothing at all when a table does not exist, which usually means the firewall is empty rather than broken.

| Command | What it does |
|---|---|
| `sudo nft list ruleset` | Print all active tables, chains, and rules across all families |
| `sudo nft list table inet filter` | Print rules for specific table |
| `sudo nft list chain inet filter input` | Print rules for specific chain |
| `sudo nft -a list ruleset` | Print rules with handle IDs displayed (required for deletion) |

## From iptables

Most people land here with an iptables ruleset already running. iptables-translate prints the nft equivalent of any iptables command without touching the firewall.

| iptables Concept | nftables Equivalent |
|---|---|
| Fixed default tables (`filter`, `nat`) | Custom tables declared in configuration (no tables by default) |
| Separate `iptables` and `ip6tables` | Unified `inet` family handles IPv4 and IPv6 simultaneously |
| Multiple sequential rules for ports | Native sets: `tcp dport { 80, 443 } accept` |

Paste a ruleset into the [iptables to nftables converter](https://sshworkbench.com/tools/iptables-to-nftables) for the same job in a browser, or the [firewall rule generator](https://sshworkbench.com/tools/firewall-rule-generator) to write one rule for nft, iptables, UFW, and firewalld at once.

| iptables Concept | nftables Equivalent |
|---|---|
| Fixed default tables (`filter`, `nat`) | Custom tables declared in configuration (no tables by default) |
| Separate `iptables` and `ip6tables` | Unified `inet` family handles IPv4 and IPv6 simultaneously |
| Multiple sequential rules for ports | Native sets: `tcp dport { 80, 443 } accept` |

The full iptables side of the mapping is on the [iptables cheat sheet](https://sshworkbench.com/cheatsheets/iptables).

## Tables and Chains

nftables ships with nothing: no filter table, no INPUT chain. You create what you need. The inet family covers IPv4 and IPv6 in one place and is the right default.

| Address Family | Description |
|---|---|
| `inet` | Dual-stack table handling both IPv4 and IPv6 packets |
| `ip` | IPv4 packets only |
| `ip6` | IPv6 packets only |
| `arp` | ARP packet filtering |
| `bridge` | Packets traversing network bridges |

A chain only sees traffic if it is a base chain, meaning it declares a type, a hook, and a priority. The shell eats {, }, and ;, so quote the block.

```bash
sudo nft add table inet filter
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy accept; }'
sudo nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
sudo nft add chain inet filter output '{ type filter hook output priority 0; policy accept; }'
```

| Hook        | Where it sits                                                 |
|-------------|---------------------------------------------------------------|
| prerouting  | Before the routing decision; NAT destination rewrites go here |
| input       | Packets addressed to this machine                             |
| forward     | Packets routed through this machine                           |
| output      | Packets this machine generates                                |
| postrouting | After routing, on the way out; NAT source rewrites go here    |

Chain types are filter, nat, and route. Priority is a number, low first, and named values read better: raw (-300), mangle (-150), dstnat (-100), filter (0), srcnat (100). Two base chains on the same hook both run, in priority order.

## SSH Lockout

A base input chain with policy drop and no rules kills the session you are typing in, not just the next one, because nftables judges every packet including the ones carrying your keystrokes. Build the allow rules first and set the policy last.

```bash
sudo nft add table inet filter
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy accept; }'
sudo nft add rule inet filter input ct state established,related accept
sudo nft add rule inet filter input ct state invalid drop
sudo nft add rule inet filter input iif lo accept
sudo nft add rule inet filter input tcp dport 22 accept
# only now, once port 22 is open:
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
```

| Step | Safe Command Sequence | Purpose |
|---|---|---|
| 1. Create Table & Chain | `sudo nft add table inet filter`<br>`sudo nft add chain inet filter input { type filter hook input priority 0 \; }` | Create chain with default accept policy first |
| 2. Allow SSH & Established | `sudo nft add rule inet filter input ct state established,related accept`<br>`sudo nft add rule inet filter input tcp dport 22 accept` | Ensure SSH is permitted |
| 3. Set Drop Policy | `sudo nft add chain inet filter input { policy drop \; }` | Change policy to drop safely |

Cancel the deadman switch once the new ruleset works: systemctl stop run-r*.timer, or list the pending jobs with systemctl list-timers. If SSH listens somewhere other than 22, open that port instead, and check with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker) from outside the box. The [SSH cheat sheet](https://sshworkbench.com/cheatsheets/ssh) covers the client side of a connection that will not come back.

## Adding Rules

add appends to the end of a chain, insert puts the rule at the top. Order matters: the first rule with a verdict wins, so a drop above an accept is the end of the story.

| Command | What it does |
|---|---|
| `sudo nft add rule inet filter input tcp dport 22 accept` | Append rule to input chain |
| `sudo nft insert rule inet filter input position 5 tcp dport 80 accept` | Insert rule at specific handle position |

## Rule Syntax

A rule is a list of matches followed by a verdict. Everything before the verdict has to be true for the verdict to apply.

| nftables Expression | Meaning |
|---|---|
| `ct state established,related accept` | Accept return traffic for established connections |
| `iifname "lo" accept` | Accept traffic on loopback interface |
| `tcp dport { 22, 80, 443 } accept` | Match multiple destination ports in a set |
| `ip saddr 192.168.1.0/24 accept` | Filter by source IPv4 subnet |
| `drop` / `reject` | Drop packet silently or return ICMP unreachable |

| nftables Expression | Meaning |
|---|---|
| `ct state established,related accept` | Accept return traffic for established connections |
| `iifname "lo" accept` | Accept traffic on loopback interface |
| `tcp dport { 22, 80, 443 } accept` | Match multiple destination ports in a set |
| `ip saddr 192.168.1.0/24 accept` | Filter by source IPv4 subnet |
| `drop` / `reject` | Drop packet silently or return ICMP unreachable |

Variables keep a file readable. define wan = "eth0" at the top, then oifname $wan in the rules.

## Deleting and Flushing

There are no rule numbers. Deletion works by handle, and handles only appear with -a, which is where this stops being obvious.

| Command | What it does |
|---|---|
| `sudo nft flush ruleset` | Wipe and clear all tables, chains, and rules completely |
| `sudo nft flush table inet filter` | Remove all rules within specific table |
| `sudo nft delete rule inet filter input handle 8` | Delete specific rule by its handle ID |

Handles are assigned in order but are not reused and do not survive a reload, so list them again after every nft -f.

## Sets and Maps

Sets replace ipset. A named set is part of the ruleset, so it saves and reloads with everything else, and lookups stay fast as it grows.

```bash
sudo nft add set inet filter blocklist '{ type ipv4_addr; flags interval; }'
sudo nft add element inet filter blocklist '{ 203.0.113.0/24, 198.51.100.7 }'
sudo nft add rule inet filter input ip saddr @blocklist drop
```

| Command | What it does |
|----|----|
| nft list sets | Every named set with its elements |
| nft list set inet filter blocklist | One set |
| nft add element inet filter blocklist '{ 198.51.100.9 }' | Add an address |
| nft delete element inet filter blocklist '{ 198.51.100.7 }' | Remove an address |
| nft flush set inet filter blocklist | Empty a set, leave the rules pointing at it |
| nft add set inet filter ports '{ type inet_service; }' | A set of ports instead of addresses |
| flags interval | Allows CIDR ranges as elements |
| flags timeout; timeout 1h | Elements expire on their own, fail2ban style |
| nft add element inet filter blocklist '{ 203.0.113.9 timeout 10m }' | A timeout on one element |
| tcp dport vmap { 22 : accept, 80 : accept, 443 : accept } | Verdict map: one rule, one lookup, many ports |

A map pairs a key with a value, which is how you write a port forwarding table in one rule:

```bash
sudo nft add map ip nat porthost '{ type inet_service : ipv4_addr; }'
sudo nft add element ip nat porthost '{ 80 : 10.0.0.5, 8443 : 10.0.0.6 }'
sudo nft add rule ip nat prerouting dnat to tcp dport map @porthost
```

## NAT and Port Forwarding

NAT needs its own table with nat type chains; a filter chain cannot rewrite addresses. Forwarding between interfaces also needs net.ipv4.ip_forward=1 and a forward chain that accepts the traffic.

```bash
sudo nft add table ip nat
sudo nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; }'
sudo nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; }'
sudo nft add rule ip nat postrouting oifname "eth0" masquerade
sudo nft add rule ip nat prerouting iifname "eth0" tcp dport 8080 dnat to 10.0.0.5:80
```

| Rule Example | Purpose |
|---|---|
| `dnat to 192.168.1.50:8080` | Forward incoming destination traffic to internal host IP and port |
| `masquerade` | Dynamic Source NAT (SNAT) on outgoing WAN interface |

A dnat rule that does nothing is usually a forward chain with policy drop and no matching accept, or ip_forward left at 0. Traffic from the same machine does not pass through prerouting, so a local test of a port forward always fails; test from another host, or with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker).

## Rate Limiting

limit matches while traffic is under the rate; limit rate over matches once it goes above. Put the verdict that suits the one you picked.

| Command | What it does |
|----|----|
| nft add rule inet filter input tcp dport 22 ct state new limit rate 3/minute accept | Accept up to 3 new SSH connections a minute, rest falls through |
| nft add rule inet filter input tcp dport 22 ct state new limit rate over 3/minute drop | Drop new SSH connections above 3 a minute |
| limit rate 10/second burst 20 packets | Allow a short burst before the limit bites |
| limit rate 1 mbytes/second | Limit by bandwidth rather than packet count |
| icmp type echo-request limit rate 5/second accept | Answer ping, but not a flood of it |

A plain limit counts every packet together, so one noisy address starves everyone. For a per-address limit, use a dynamic set:

```bash
sudo nft add set inet filter ssh_meter '{ type ipv4_addr; flags dynamic; timeout 1m; }'
sudo nft add rule inet filter input tcp dport 22 ct state new \
  add @ssh_meter { ip saddr limit rate 3/minute } accept
```

Each source address gets its own counter. Over the limit the statement stops matching, so the packet falls through to whatever comes next, which should be a drop rule. For a single server, ufw limit 22/tcp does the same thing in one line; see the [UFW cheat sheet](https://sshworkbench.com/cheatsheets/ufw).

## Counters and Logging

Unlike iptables, counters are off unless you ask for them, which is why an nftables ruleset is cheaper to evaluate.

| Keyword | Example Syntax | Purpose |
|---|---|---|
| `counter` | `tcp dport 22 counter accept` | Track packet and byte counts for rule |
| `log` | `log prefix "NFT-DROP: " drop` | Log dropped packets to kernel ring buffer |

Logging happens where the rule sits, so a log rule at the bottom of a policy drop chain shows you exactly what the firewall is turning away. [journalctl](https://sshworkbench.com/cheatsheets/journalctl) has the rest of the reading options.

## nftables.conf

One file holds the whole ruleset. flush ruleset on the first line makes loading it idempotent: the file replaces what is running instead of adding to it.

```
#!/usr/sbin/nft -f

flush ruleset

define wan = "eth0"
define admin = { 203.0.113.10, 198.51.100.0/24 }

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        ct state established,related accept
        ct state invalid drop
        iif lo accept

        ip protocol icmp accept
        ip6 nexthdr icmpv6 accept

        ip saddr $admin tcp dport 22 accept
        tcp dport { 80, 443 } accept

        limit rate 5/minute log prefix "nft-input-drop " counter
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

| Directive | Syntax Example | Purpose |
|---|---|---|
| Shebang | `#!/usr/sbin/nft -f` | Allows script execution directly from terminal |
| Flush Ruleset | `flush ruleset` | Atomically wipe existing rules before loading new file |
| Variables | `define wan = "eth0"` | Declare reusable variable macros |
| Sets | `define admin = { 10.0.0.1, 10.0.0.2 }` | Declare reusable IP/port sets |

## Persist and Reload

Rules added with nft add are live immediately and gone at the next reboot. Nothing writes them to disk for you.

| Action | Command |
|---|---|
| Save current ruleset | `sudo nft list ruleset > /etc/nftables.conf` |
| Reload configuration | `sudo nft -f /etc/nftables.conf` |
| Enable systemd service | `sudo systemctl enable --now nftables` |

Saving and enabling, in full:

```bash
sudo sh -c 'echo "flush ruleset" > /etc/nftables.conf && nft -s list ruleset >> /etc/nftables.conf'
sudo nft -c -f /etc/nftables.conf
sudo systemctl enable --now nftables
```

nft -f is atomic: the whole file applies or none of it does. A reload never leaves the firewall half configured, which is the main reason to edit the file rather than type rules one at a time.

## Syntax Check

-c parses and checks without applying, so a broken file never reaches the kernel. Run it before every reload.

| Command | What it does |
|----|----|
| nft -c -f /etc/nftables.conf | Check the whole file, change nothing |
| nft -c add rule inet filter input tcp dport 22 accept | Check one command before running it |
| nft --check --file ruleset.nft | The long form of the same thing |
| nft -f - | Read a ruleset from standard input (useful in scripts) |
| nft --debug=netlink -c -f file.nft | Show what would be sent to the kernel |

An error names the file, line, and column, with a caret under the token it choked on:

```
/etc/nftables.conf:14:17-20: Error: syntax error, unexpected string
        tcp dport 80 ACCEPT
                     ^^^^^^
```

The usual causes: iptables words in an nft file (-A, -j ACCEPT, uppercase verdicts), unquoted {, }, or ; on a shell command line, a base chain missing its type ... hook ... priority line, a set used before it is declared, and nft reading a file that was written for iptables-restore.

## nftables vs iptables

| Feature | `nftables` | `iptables` |
|---|---|---|
| Dual Stack | Native (`inet` family) | Requires separate `iptables` and `ip6tables` |
| Multiport / Sets | Native set syntax `{ 22, 80, 443 }` | Requires `-m multiport` match extension |
| Performance | Faster rule evaluation via bytecode engine | Slower linear rule traversal |
| Atomic Reloads | Single atomic transaction (`nft -f`) | Requires userspace reload utilities |

Existing iptables scripts keep working through iptables-nft, so there is no rush. New rulesets are worth writing in native nft syntax.

## Gotchas

- A base chain with policy drop and no rules drops the packets carrying your SSH session, immediately. Add ct state established,related accept and the port 22 rule before you set the policy.
- nft flush ruleset deletes the tables, so the policies go with them and the box ends up wide open. That is the opposite of the iptables trap, where flushing with a DROP policy locks you out. Both are worth a deadman switch.
- The shell, not nft, is what rejects { type filter hook input priority 0; policy drop; }. Wrap the braces in single quotes.
- Handles are not line numbers. They do not survive a reload, so re-run nft -a list ruleset after every nft -f before deleting anything.
- A rule added with nft add is not in /etc/nftables.conf, and a rule written in that file is not live. Nothing syncs them.
- iif / oif match the interface index and go stale when a device is recreated, which happens with VPN and container interfaces. Use iifname / oifname unless you have measured that you need the speed.
- Docker writes its own rules and publishes container ports through the forward path, so a container with -p 8080:80 is reachable even when your input chain says otherwise. Bind it to 127.0.0.1 and put a reverse proxy in front.
- Two base chains on the same hook both run. If a rule seems to be ignored, look for another table hooking the same place at a lower priority, including the tables iptables-nft and firewalld create.
- nft list ruleset shows nothing when there are no tables. That is an open firewall, not a broken command.

## nftables FAQ

### How do I delete a single nftables rule?

By handle, not by line number. Run sudo nft -a list ruleset to print every rule with a trailing \# handle N comment, find the rule you want, then sudo nft delete rule inet filter input handle 7. Without -a there are no handles in the output, which is where most people get stuck. Handles are assigned when a rule is added and stay with that rule until it is removed, but they are not reused or preserved across a reload, so list them again after every nft -f. There is no way to delete a rule by retyping it, so if you cannot find the handle, edit /etc/nftables.conf, remove the line, and reload the file with sudo nft -f /etc/nftables.conf.

### Where are nftables rules stored?

Nowhere by default. The live ruleset exists only in the kernel, and sudo nft list ruleset is the only way to read it. The file the nftables service loads at boot is /etc/nftables.conf on Debian, Ubuntu, and Arch, and /etc/sysconfig/nftables.conf on RHEL, Rocky, and Fedora, where it usually just includes files from /etc/nftables/. Neither file updates itself: a rule you add with nft add rule is live immediately and absent from the file, and a rule you write in the file does nothing until you run sudo nft -f on it. Write the running ruleset back out with sudo nft -s list ruleset before you reboot.

### Are nftables rules persistent after a reboot?

Only if you save them and enable the service. Two steps: write the ruleset to disk with sudo sh -c 'nft -s list ruleset > /etc/nftables.conf', then sudo systemctl enable --now nftables so the file is loaded at every boot. Check with systemctl is-enabled nftables. Add flush ruleset as the first line of the file so a reload replaces the ruleset instead of stacking a second copy of every rule on top of the running one. UFW and firewalld handle this for you, which is why a single server is often better off with one of those than with raw nft.

### Can iptables and nftables run at the same time?

Technically yes, and it is a common way to get a firewall that behaves nothing like either ruleset. Both front ends feed the same netfilter hooks, so rules from both are evaluated and the first drop wins. On Debian 10, Ubuntu 20.04, RHEL 8 and anything newer, the iptables command is usually iptables-nft, a shim that writes nftables rules into tables named filter, nat and mangle in the ip family, so sudo nft list ruleset shows them alongside your own. Check which binary you have with sudo iptables -V: a version ending in (nf_tables) is the shim, (legacy) is the old xtables path, and the legacy one really does run a separate ruleset the nft command cannot see. Pick one tool and move everything to it.

### Where does nftables log dropped packets?

To the kernel log, not to a file of its own. A rule with a log statement writes through the kernel's printk buffer, so it lands in journalctl -k (or /var/log/kern.log and /var/log/messages on systems with rsyslog). Give each rule a prefix, such as log prefix "nft-input-drop ", and follow it with sudo journalctl -k -f \| grep nft-input-drop. A busy drop rule can flood the log, so put limit rate 5/minute in front of the log statement. For logs in their own file, use log group 2 instead, which hands packets to ulogd2 over nflog.

---
Source: https://sshworkbench.com/cheatsheets/nftables
