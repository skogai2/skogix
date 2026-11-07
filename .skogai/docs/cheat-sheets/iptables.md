# iptables Commands

iptables is the classic Linux firewall tool, still everywhere even though nftables is its successor. This sheet covers listing and adding rules, opening and blocking ports, rule order, NAT and port forwarding, ipset, IPv6, Docker, making rules survive a reboot, and the DROP policy that locks you out of SSH.

Last updated September 11, 2026

On this page

- [Listing Rules](#listing-rules)
- [SSH Lockout](#ssh-lockout)
- [Allowing Traffic](#allowing-traffic)
- [Blocking Traffic](#blocking-traffic)
- [Adding and Deleting Rules](#adding-and-deleting-rules)
- [Rule Order](#rule-order)
- [Tables and Chains](#tables-and-chains)
- [Flushing Rules](#flushing-rules)
- [NAT and Port Forwarding](#nat-and-port-forwarding)
- [Saving Rules](#saving-rules)
- [IP Sets](#ip-sets)
- [Logging and Rate Limiting](#logging-and-rate-limiting)
- [IPv6](#ipv6)
- [Docker](#docker)
- [Common Errors](#common-errors)
- [nftables and Front Ends](#nftables-and-front-ends)
- [Gotchas](#gotchas)

## Listing Rules

Everything needs root. -n skips DNS lookups, -v adds packet counters, --line-numbers gives you the numbers used for deleting.

| Command | What it does |
|----|----|
| iptables -L -n -v | All rules in the filter table, numeric, with counters |
| iptables -L -n -v --line-numbers | Same, with rule numbers for deleting |
| iptables -L INPUT -n -v | One chain only |
| iptables -S | Rules printed as the commands that made them |
| iptables -t nat -L -n -v | Rules in the nat table (NAT rules never show in the default listing) |
| iptables -C INPUT -p tcp --dport 22 -j ACCEPT | Check whether an exact rule exists; exit code 0 means yes |
| iptables -Z | Zero the packet counters, leaving the rules alone |
| iptables -L -n -v \| grep 22 | Find rules touching port 22 |
| watch -n1 'iptables -L INPUT -n -v' | Watch packet counters move, live |

## SSH Lockout

This is the one that costs you the server. iptables -P INPUT DROP with no rule allowing port 22 kills the session you are typing in, not just the next login, because the policy applies to the packets carrying your keystrokes. The same thing happens when you flush a ruleset while the policy is already DROP, since -F removes the SSH allow rule and leaves the DROP in place. Add the allow rules first, set the policy last.

```
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -L INPUT -n -v --line-numbers   # confirm the SSH rule is live
# only now, once port 22 is open:
sudo iptables -P INPUT DROP
```

Copy

[TABLE]

Set up the deadman switch before the first DROP, not after, and cancel it once a new login works. If sshd listens on a non-standard port, open that port instead and check it from outside with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker). A DROP policy shows up as a timeout ([Network error: Connection timed out](https://sshworkbench.com/fix/putty-network-error-connection-timed-out)), a REJECT rule as [connection refused](https://sshworkbench.com/fix/ssh-connection-refused). The [nftables](https://sshworkbench.com/cheatsheets/nftables) and [UFW](https://sshworkbench.com/cheatsheets/ufw) sheets have the same trap in their own syntax, and the [firewall rule generator](https://sshworkbench.com/tools/firewall-rule-generator) writes a ruleset that already has the SSH rule in it.

## Allowing Traffic

Order matters: rules match top down, first match wins. Allow SSH before anything drops.

[TABLE]

A minimal safe INPUT policy, in the right order:

```
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT
sudo iptables -P INPUT DROP
```

Copy

The [firewall rule generator](https://sshworkbench.com/tools/firewall-rule-generator) builds rule sets like this from a checklist.

## Blocking Traffic

| Command | What it does |
|----|----|
| iptables -A INPUT -s 198.51.100.7 -j DROP | Block one IP |
| iptables -A INPUT -s 198.51.100.0/24 -j DROP | Block a range |
| iptables -I INPUT 1 -s 198.51.100.7 -j DROP | Block it ahead of every allow rule |
| iptables -A INPUT -p tcp --dport 23 -j DROP | Block a port silently |
| iptables -A INPUT -p tcp --dport 25 -j REJECT | Block a port with an immediate error |
| iptables -A OUTPUT -d 198.51.100.7 -j DROP | Stop this box talking to an IP |
| iptables -D INPUT -s 198.51.100.7 -j DROP | Unblock: delete the rule that blocked it |

DROP discards the packet silently, so the client hangs until it times out; REJECT answers with an error, so the client fails fast with connection refused. DROP gives port scanners nothing, REJECT is kinder for services your own users hit. If SSH suddenly gets [connection refused](https://sshworkbench.com/fix/ssh-connection-refused), look for a REJECT rule. For blocklists of more than a handful of addresses, or a whole country, see IP Sets below.

## Adding and Deleting Rules

-A appends to the bottom, -I inserts at the top (or a position). Since first match wins, a rule appended after a DROP does nothing.

| Command | What it does |
|----|----|
| iptables -A INPUT ... | Append at the end of the chain |
| iptables -I INPUT ... | Insert at position 1, the very top |
| iptables -I INPUT 3 ... | Insert at position 3 |
| iptables -D INPUT -p tcp --dport 80 -j ACCEPT | Delete by repeating the rule exactly |
| iptables -L INPUT -n --line-numbers | Get the numbers, then... |
| iptables -D INPUT 3 | Delete rule number 3 |
| iptables -R INPUT 3 -p tcp --dport 8080 -j ACCEPT | Replace rule number 3 |
| iptables -P INPUT DROP | Set the chain policy, the fate of packets no rule matched |
| iptables -w 5 -A INPUT ... | Wait up to 5 seconds for the xtables lock instead of failing |

Rule numbers shift after every delete. Deleting several by number goes highest first, or re-list between deletes.

## Rule Order

Inside a chain the first matching rule wins and evaluation stops, so a rule you append below an existing ACCEPT or DROP never runs. Chains run in a fixed order too, which is why NAT happens before your filter rules ever see the packet.

[TABLE]

Two consequences worth remembering: a DNAT rewrite in PREROUTING happens first, so a FORWARD rule has to match the internal address, not the public one; and a packet accepted in INPUT never reaches FORWARD, which is why Docker's published ports are invisible to your INPUT rules.

## Tables and Chains

A rule lives in a chain, a chain lives in a table. -t filter is the default, which is why NAT rules seem to disappear until you ask for their table.

[TABLE]

## Flushing Rules

-F deletes all rules but does not touch chain policies. If the policy is DROP, flushing locks you out of SSH instantly. Safe order:

```
# 1. Open the policies first, so an empty ruleset allows everything:
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
# 2. Now flush:
sudo iptables -F
sudo iptables -X          # delete custom chains
sudo iptables -t nat -F   # nat and mangle have their own rules
sudo iptables -t mangle -F
```

Copy

Keep the current SSH session open and test a fresh login before closing it. When rebuilding, the first rule you add back is the SSH allow, and the deadman switch in SSH Lockout above costs nothing.

## NAT and Port Forwarding

NAT rules live in the nat table and need forwarding enabled in the kernel first:

```
sudo sysctl -w net.ipv4.ip_forward=1
# permanent: echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-forward.conf
```

Copy

| Command | What it does |
|----|----|
| iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE | Share this box's IP with everything it routes (the home router rule) |
| iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE | Masquerade one subnet only (typical VPN setup) |
| iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to-source 203.0.113.10 | Source NAT to a fixed address; cheaper than MASQUERADE on a static IP |
| iptables -t nat -A PREROUTING -p tcp --dport 8080 -j REDIRECT --to-port 80 | Redirect a port on this box |
| iptables -t nat -A PREROUTING -p tcp --dport 2222 -j DNAT --to-destination 10.0.0.5:22 | Forward a port to an internal host |
| iptables -t nat -L -n -v | See what NAT is doing |

Forward port 80 arriving on this box to an internal server:

```
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.5:80
sudo iptables -A FORWARD -p tcp -d 10.0.0.5 --dport 80 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

Copy

A forward that does nothing is almost always ip_forward left at 0, a FORWARD chain with no matching ACCEPT, or a test run from the box itself: locally generated traffic never passes through PREROUTING, so test from another host or with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker).

## Saving Rules

Rules live in kernel memory and are gone after a reboot unless something restores them.

| Command | What it does |
|----|----|
| iptables-save \> /etc/iptables/rules.v4 | Dump current rules to a file |
| iptables-restore \< /etc/iptables/rules.v4 | Load them back, replacing everything |
| iptables-restore -n \< extra.v4 | Merge a file into the running rules instead of replacing them |
| iptables-save -c \> rules.v4 | Keep the packet counters in the dump |
| apt install iptables-persistent | Debian/Ubuntu: restores rules at boot |
| netfilter-persistent save | Save current rules for that boot restore |
| service iptables save | RHEL/CentOS with the iptables-services package |
| ip6tables-save \> /etc/iptables/rules.v6 | IPv6 rules are saved separately |
| iptables-apply rules.v4 | Apply with an automatic rollback if you do not confirm (lockout insurance) |

## IP Sets

ipset keeps thousands of addresses in one kernel hash, so a blocklist costs you one rule instead of one rule per address, and matching stays fast as it grows.

```
sudo apt install ipset
sudo ipset create blocklist hash:net
sudo ipset add blocklist 198.51.100.0/24
sudo iptables -I INPUT -m set --match-set blocklist src -j DROP
```

Copy

| Command | What it does |
|----|----|
| ipset list blocklist | Show a set and everything in it |
| ipset add blocklist 203.0.113.9 timeout 3600 | Add an address that expires on its own |
| ipset del blocklist 203.0.113.9 | Remove one |
| ipset test blocklist 203.0.113.9 | Ask whether an address is in the set |
| ipset create allowlist hash:ip | A set of single addresses rather than networks |
| iptables -I INPUT -m set --match-set allowlist src -j ACCEPT | Allow only what is in a set |
| ipset save \> /etc/ipset.conf | Sets are saved separately from iptables rules |
| ipset restore \< /etc/ipset.conf | Load them back; do this before the iptables rules |
| ipset destroy blocklist | Delete a set; the rules referencing it have to go first |

Country blocking works the same way: build a hash:net set from an aggregated zone file and point one DROP rule at it. The xt_geoip module from xtables-addons does it without a set, but the database needs updating by hand and it is a per-packet lookup. nftables has sets built into the ruleset, with no second tool to install or save; see the [nftables cheat sheet](https://sshworkbench.com/cheatsheets/nftables).

## Logging and Rate Limiting

[TABLE]

Logged packets land in the kernel log: journalctl -k \| grep IPT-DROP or dmesg. fail2ban inserts its bans into its own chain at the top of INPUT, so its rules are why a chain sometimes has entries you did not add.

## IPv6

ip6tables is a second, independent firewall with the same syntax. Locking down IPv4 on a service that also listens on IPv6 closes half the door.

[TABLE]

nftables' inet family covers both stacks in one rule, which is the main day-to-day reason to move.

## Docker

Docker writes its own chains and publishes container ports through FORWARD and the DOCKER chain, bypassing INPUT entirely. A container run with -p 8080:80 is reachable from the internet even when your INPUT rules say only 22 is open.

| Command | What it does |
|----|----|
| iptables -t nat -L DOCKER -n | The port publishing rules Docker wrote |
| iptables -L DOCKER-USER -n | The chain Docker leaves for you; it runs before Docker's own rules |
| iptables -I DOCKER-USER -i eth0 ! -s 10.0.0.0/8 -j DROP | Block outside traffic to every published port |
| docker run -p 127.0.0.1:8080:80 ... | Publish to localhost only, then reverse proxy in front |
| iptables -L -n -v \| grep -c DOCKER | Quick check whether Docker is managing rules on this box |
| systemctl restart docker | Rebuilds Docker's chains; rules you added inside them are lost, DOCKER-USER survives |

Setting {"iptables": false} in /etc/docker/daemon.json stops the bypass but breaks container networking in other ways, so almost nobody keeps it. Full container commands are on the [Docker cheat sheet](https://sshworkbench.com/cheatsheets/docker).

## Common Errors

[TABLE]

## nftables and Front Ends

nftables is the successor; new setups should use it or a front end rather than raw iptables.

[TABLE]

Convert whole rule sets with the [iptables to nftables converter](https://sshworkbench.com/tools/iptables-to-nftables), or write one rule for iptables, nft, UFW, and firewalld at once with the [firewall rule generator](https://sshworkbench.com/tools/firewall-rule-generator). The [nftables cheat sheet](https://sshworkbench.com/cheatsheets/nftables) has the native syntax side by side with these commands. If all you want is ports opened and closed on one server, [UFW](https://sshworkbench.com/cheatsheets/ufw) is the simpler front end and manages this layer for you.

## Gotchas

- Mixing tools bites: ufw, firewalld, and Docker all write their own iptables or nftables rules, so a rule you add by hand can be shadowed by theirs or wiped on their reload.
  nft list ruleset
  shows the whole truth; pick one manager per box.
- Rules are gone after a reboot unless you set up persistence. The classic failure: firewall works for months, a reboot silently drops it.
- iptables -L
  without
  -t nat
  hides all NAT rules, and without
  -n
  it stalls on DNS lookups.
- iptables-legacy and iptables-nft keep separate rule sets. If rules seem to be missing, the other binary may own them: check
  iptables -V
  and
  iptables-legacy -L -n
  .
- Docker publishes container ports by writing its own FORWARD and DOCKER chain rules, bypassing your INPUT rules entirely. A "closed" port can still be reachable through Docker.
- IPv6 is a separate firewall (
  ip6tables
  or the nft
  inet
  family). Locking down IPv4 while the service also listens on IPv6 locks down half the door.
- ipset
  contents are saved by
  ipset save
  , not by
  iptables-save
  . Restoring rules without restoring the sets leaves you with rules that match nothing, or that refuse to load at all.

### Firewall rules you can see

SSH Workbench shows the firewall on every server as a table you can edit, and warns before a rule locks you out of SSH.

[Try free for 7 days](https://sshworkbench.com/#install)

## iptables FAQ

### Do iptables rules persist after a reboot?

No. The running ruleset lives in kernel memory and is empty again at the next boot unless a package or a unit restores it. On Debian and Ubuntu, sudo apt install iptables-persistent saves whatever is loaded during the install and reloads it at boot, and after every later change you have to run sudo netfilter-persistent save yourself. On RHEL, Rocky, and Fedora the equivalent is iptables-services, enabled with systemctl enable iptables and saved with sudo service iptables save. The trap is saving too early: the save command writes the ruleset that is live right now, so a half-built one, or one you have not tested with a fresh SSH login, is the one that comes back after a reboot. IPv6 is a separate save (ip6tables-save), and ipset contents are a third.

### Where are iptables rules stored?

The live rules are not in a file at all, they are in the kernel, which is why sudo iptables -S is the only reliable way to read them. The file a distro restores at boot is /etc/iptables/rules.v4 and rules.v6 on Debian and Ubuntu with iptables-persistent, and /etc/sysconfig/iptables and ip6tables on RHEL, Rocky, and Fedora. Neither file updates itself. A rule you add on the command line is live and absent from the file, and a line you edit into the file changes nothing until iptables-restore reads it, so the two drift apart silently. If ufw or firewalld is managing the box, the real source is their config (/etc/ufw/\*.rules) and the iptables rules you see are generated output.

### Is iptables deprecated?

The command is not going away, but the machinery under it already changed. nftables replaced iptables in the kernel from 3.13, and on Debian 10, Ubuntu 20.04, RHEL 8 and anything newer the iptables binary is usually iptables-nft, a shim that translates your commands into nftables rules. Check with sudo iptables -V: a version ending in (nf_tables) is the shim, (legacy) is the old xtables path. Existing scripts keep working, so there is no rush, and iptables will outlive most of the servers running it. New rulesets are worth writing in native nft syntax, or handing to ufw or firewalld, because the shim cannot express everything nftables can.

### Is iptables running?

It is not a service you start, so there is nothing to be running. The rules sit in the kernel and are enforced from the moment they are added. What you actually want to know is whether any rules exist: sudo iptables -L -n -v shows them with counters, and chains that are empty with policy ACCEPT mean the firewall is doing nothing. The packet counters tell you whether a rule is being hit at all, which is the fastest way to prove a rule is in the wrong place. On RHEL there is an iptables.service, but it only loads the saved file at boot, so systemctl status iptables showing inactive does not mean your rules are gone.

### Can ufw and iptables work together?

They share one ruleset, so they cannot be kept apart. ufw generates iptables rules from its own config, and a rule you add by hand sits in the same chains, usually below ufw's, where it never gets reached, and it disappears the next time ufw reloads. If you need something ufw's syntax cannot express, such as NAT or a DOCKER-USER filter, put it in /etc/ufw/before.rules or after.rules so ufw applies it as part of its own set. The same applies to firewalld. Pick one manager per box and let it own the rules; sudo iptables -S and sudo nft list ruleset show you everything that is really loaded, whoever wrote it.

---
Källa: https://sshworkbench.com/cheatsheets/iptables
