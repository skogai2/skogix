# UFW Commands

UFW (Uncomplicated Firewall) is the front end for iptables that Ubuntu and Debian ship, and the firewall most single-server setups use. This sheet lists the ufw commands for enabling it without locking yourself out, opening and closing ports, allowing an IP, deleting rules, rate limiting SSH, and the Docker problem everyone hits once.

## Status and Enable

Allow SSH before you enable, every time. See SSH Lockout below for the order and the way out.

| Command | What it does |
|---|---|
| `sudo ufw status` | Check status of firewall (active or inactive) |
| `sudo ufw status verbose` | Check status with default policies and logging level |
| `sudo ufw status numbered` | Display active rules with line numbers (for deletion) |
| `sudo ufw enable` | Activate and start firewall on boot |
| `sudo ufw disable` | Deactivate firewall |

A safe first setup:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80,443/tcp
sudo ufw enable
sudo ufw status verbose
```

## SSH Lockout

ufw enable puts default deny incoming into force the moment you run it. The session you are typing in survives, because connection tracking counts it as established, but the next login is dropped unless a rule already allows the port. Add the SSH rule first and enable last.

```bash
sudo ufw allow OpenSSH          # or: sudo ufw allow 22/tcp
sudo ufw show added             # check the rule is there while ufw is still off
sudo ufw enable
```

| Step | Command |
|---|---|
| 1. Allow SSH first | `sudo ufw allow 22/tcp` or `sudo ufw allow OpenSSH` |
| 2. Verify rule added | `sudo ufw status` |
| 3. Enable firewall | `sudo ufw enable` |

Cancel the deadman switch once the new login works. If sshd listens on a non-standard port, allow that port instead and check it from outside with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker). A deny default shows up as a timeout ([Network error: Connection timed out](https://sshworkbench.com/fix/putty-network-error-connection-timed-out)), a reject default as [connection refused](https://sshworkbench.com/fix/ssh-connection-refused).

## Allow Rules

A port with no protocol opens both TCP and UDP. Service names come from /etc/services, app names from ufw app list. The [firewall rule generator](https://sshworkbench.com/tools/firewall-rule-generator) writes these for you.

| Command | What it does |
|---|---|
| `sudo ufw allow 80/tcp` | Allow incoming HTTP traffic on port 80 |
| `sudo ufw allow 443/tcp` | Allow incoming HTTPS traffic on port 443 |
| `sudo ufw allow 8000:8010/tcp` | Allow incoming port range 8000 through 8010 |
| `sudo ufw allow 53/udp` | Allow UDP traffic on port 53 (DNS) |

## Deny and Reject

deny drops packets silently, so the client waits until it times out. reject sends a refusal back, so the client fails at once with "connection refused". Deny is the usual choice for the internet, reject is kinder on internal networks.

| Command | What it does |
|----|----|
| sudo ufw deny 23/tcp | Block a port |
| sudo ufw deny from 203.0.113.5 | Block every packet from one address |
| sudo ufw deny from 203.0.113.0/24 | Block a subnet |
| sudo ufw deny from 203.0.113.5 to any port 22 | Block one address on one port |
| sudo ufw reject 113/tcp | Refuse instead of drop |
| sudo ufw deny out 25/tcp | Stop outbound mail from this box |
| sudo ufw deny in on eth1 | Block all inbound on one interface |

Deny rules only work when they sit above the allow rule they override; see Rule Order below.

## Allow From an IP or Subnet

| Command | What it does |
|---|---|
| `sudo ufw allow from 192.168.1.100` | Whitelist specific client IP for all ports |
| `sudo ufw allow from 192.168.1.0/24 to any port 22` | Allow SSH only from specified local subnet |
| `sudo ufw deny from 203.0.113.50` | Explicitly block malicious IP address |

from rules and plain port rules combine. Allowing 22 from a subnet and then also allow 22/tcp opens it to everyone, so check status after each change.

## Delete Rules

| Command | What it does |
|----|----|
| sudo ufw status numbered | Get the number |
| sudo ufw delete 3 | Delete rule 3 (asks for confirmation) |
| sudo ufw --force delete 3 | Delete without the prompt |
| sudo ufw delete allow 80/tcp | Delete by repeating the rule |
| sudo ufw delete allow from 203.0.113.5 to any port 22 proto tcp | Works for long rules too; spell it exactly as added |
| sudo ufw delete allow 'Nginx Full' | Delete an app profile rule |

Numbers renumber after each delete. To remove rules 2, 5, and 7, delete 7 first, then 5, then 2. With IPv6 on, every rule appears twice in status numbered, once plain and once marked (v6), and each copy carries its own number.

## Rule Order and Insert

ufw evaluates rules top to bottom and the first match wins. A deny from added after allow 22/tcp never fires for port 22, because the allow already matched.

| Command | What it does |
|---|---|
| `sudo ufw insert 1 allow from 10.0.0.5` | Insert rule at line 1 (evaluated first) |
| `sudo ufw delete 3` | Delete rule number 3 |
| `sudo ufw delete allow 80/tcp` | Delete rule matching exact syntax |

With IPv6 on, an insert position counts IPv4 and IPv6 rules together; ufw refuses a position that would split them and tells you so.

## Default Policies

Defaults apply to anything no rule matches. The normal shape is deny in, allow out.

| Command | Description |
|---|---|
| `sudo ufw default deny incoming` | Block all incoming connections by default (recommended) |
| `sudo ufw default allow outgoing` | Allow all outbound traffic initiated from host |

## Rate Limiting

limit allows a port but blocks an address that opens 6 or more connections within 30 seconds. It is the cheapest brute-force defence for SSH, and it costs nothing when you also use keys.

| Command | What it does |
|---|---|
| `sudo ufw limit ssh` | Limit connections on port 22 (denies IP if >6 connections in 30 seconds) |
| `sudo ufw limit 22/tcp` | Same, using port number explicitly |

A limit rule replaces the allow rule for that port; you do not need both. For anything beyond 6 hits per 30 seconds, use fail2ban.

## Logging

| Command / Path | Description |
|---|---|
| `sudo ufw logging on` | Enable packet logging |
| `sudo ufw logging medium` | Set logging level (`low`, `medium`, `high`, `full`) |
| `/var/log/ufw.log` | Standard log file for UFW messages |

## App Profiles

Packages such as OpenSSH, nginx, Apache, and Samba drop a profile in /etc/ufw/applications.d/ that names their ports. Rules made from a profile update when the package updates.

| Command | What it does |
|---|---|
| `sudo ufw app list` | List registered application profiles (e.g. `OpenSSH`, `Nginx Full`) |
| `sudo ufw app info 'Nginx Full'` | Show ports and description of application profile |
| `sudo ufw allow 'Nginx Full'` | Open all ports required by application profile |

A profile of your own goes in /etc/ufw/applications.d/myapp:

```
[MyApp]
title=My App
description=Internal API
ports=8080,8443/tcp
```

## Ping and ICMP

ufw's rule syntax has no ICMP protocol, so sudo ufw allow proto icmp fails with ERROR: Unsupported protocol 'icmp'. Ping is accepted in /etc/ufw/before.rules before your own rules run, and changing that means editing the file.

| File / Setting | Description |
|---|---|
| `/etc/ufw/before.rules` | ICMP echo requests (ping) are allowed by default |
| Disable Ping | Change `-p icmp --icmp-type echo-request -j ACCEPT` to `DROP` in `before.rules` |

To stop answering ping, change ACCEPT to DROP on the echo-request line in /etc/ufw/before.rules, and in before6.rules for IPv6:

```
-A ufw-before-input -p icmp --icmp-type echo-request -j DROP
```

Leave the other ICMP types accepted. destination-unreachable carries path MTU discovery, and dropping it breaks large packets over some links.

## Port Forwarding and NAT

The ufw CLI covers the INPUT chain. Forwarded traffic needs route rules, IP forwarding turned on, and a NAT block written by hand.

| File / Directive | Setting |
|---|---|
| `/etc/default/ufw` | Set `DEFAULT_FORWARD_POLICY="ACCEPT"` |
| `/etc/sysctl.conf` | Enable `net.ipv4.ip_forward=1` |
| `/etc/ufw/before.rules` | Add `*nat` table block with PREROUTING and POSTROUTING rules |

A DNAT port forward goes at the top of /etc/ufw/before.rules, above the *filter line:

```
*nat
:PREROUTING ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
-A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to-destination 10.0.0.5:8080
-A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
COMMIT
```

Then sudo ufw reload, and add a matching ufw route allow rule, because the rewritten packet still has to pass the FORWARD chain. Traffic from the server itself never goes through PREROUTING, so testing a forward from the box always fails; test from another host or with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker).

## Reload and Reset

| Command | Action |
|---|---|
| `sudo ufw reload` | Reload firewall rules without restarting daemon |
| `sudo ufw reset` | Disable firewall and reset all rules back to default factory state |

Rules added with allow, deny, and limit apply immediately; no reload needed. The files, if you ever need them:

| Command | Action |
|---|---|
| `sudo ufw reload` | Reload firewall rules without restarting daemon |
| `sudo ufw reset` | Disable firewall and reset all rules back to default factory state |

Anything ufw's syntax cannot express (NAT, port forwarding, DOCKER-USER filtering) goes in before.rules or after.rules as raw iptables. The [iptables to nftables converter](https://sshworkbench.com/tools/iptables-to-nftables) helps if you are moving that block elsewhere.

## Docker

Docker bypasses ufw. It writes its own iptables rules to publish ports, and traffic to a container goes through the FORWARD chain, not INPUT, so a -p 8080:80 container is open to the world even with default deny incoming. ufw status will not show it.

| Issue | Solution |
|---|---|
| Docker exposes ports bypassing UFW | Docker modifies iptables PREROUTING directly |
| Workaround | Use `ufw-docker` utility or bind containers to `127.0.0.1:port:port` |

Docker Desktop and rootless Docker do not publish through iptables this way, so the problem is specific to the standard Linux engine. Full container commands are on the [Docker cheat sheet](https://sshworkbench.com/cheatsheets/docker).

## IPv6

ufw handles IPv6 when IPV6=yes is set in /etc/default/ufw, which is the default on Ubuntu. With it on, every rule you add applies to both stacks and status lists each rule twice, the second marked (v6).

| Configuration | Setting |
|---|---|
| `/etc/default/ufw` | Ensure `IPV6=yes` is set (enabled by default on modern distros) |

If the server has an IPv6 address and IPV6=no, that address has no firewall at all.

## Install

Ubuntu Server ships ufw. Debian, Raspberry Pi OS, and minimal cloud images do not.

| Distribution | Command |
|---|---|
| Debian / Ubuntu | `sudo apt install ufw` |
| Arch Linux | `sudo pacman -S ufw` |

## Gotchas

- Enabling without an SSH rule is the classic lockout. sudo ufw allow OpenSSH first, then sudo ufw enable. If it already happened and the provider has a web console, disable ufw from there; a reject policy shows as [connection refused](https://sshworkbench.com/fix/ssh-connection-refused), a deny policy as a timeout.
- allow 22 opens TCP and UDP. Nothing listens on UDP 22, so it is harmless, but allow 22/tcp is what you meant.
- Docker ignores ufw. See the Docker section; ufw status saying only 22 is open does not mean 8080 is closed.
- First match wins. A deny from added after a matching allow does nothing; use insert 1 for blocks.
- ufw disable keeps your rules and ufw reset deletes them. ufw status says inactive in both cases; ufw show added tells them apart.
- ufw: command not found means the package is missing (Debian and minimal images) or you left off sudo, since /usr/sbin is not on a normal user's PATH.
- Inactive again after a reboot happens on Arch and on images where the systemd unit was never enabled. sudo systemctl enable ufw fixes it; on Ubuntu, ufw enable already does.
- ICMP is not expressible in a ufw rule. Ping is allowed in before.rules, so default deny incoming does not stop it.
- ufw on a distribution that uses firewalld (Rocky, Fedora) or on a box with a cloud provider firewall in front is a second layer. Two firewalls with different rules is the usual reason a port that ufw says is open still times out.
- Editing /etc/ufw/user.rules by hand gets overwritten by the next ufw command. Use the CLI for rules and the before.rules and after.rules files for the raw iptables ufw cannot express. See the [SSH cheat sheet](https://sshworkbench.com/cheatsheets/ssh) for the ssh side of testing a port after a change.

## UFW FAQ

### Will ufw block SSH when I enable it?

Not the session you are already in. Connection tracking treats it as established, so it survives sudo ufw enable even though ufw warns that enabling may disrupt existing ssh connections. The next login is the one that gets dropped, and only when no rule allows the port. Run sudo ufw allow OpenSSH (or sudo ufw allow 22/tcp if the app profile is missing), confirm it with sudo ufw show added, then enable. If sshd listens somewhere other than 22, allow that port instead, and if you always connect from the same network, sudo ufw allow from 203.0.113.0/24 to any port 22 proto tcp is tighter than opening 22 to everyone.

### Why does ufw status say inactive?

Because nothing has run sudo ufw enable since the last boot. Rules added while it is off are kept, and sudo ufw show added lists them, so an inactive status does not mean an empty rule set. Two causes beyond simply forgetting: on Arch and on minimal Debian images the package does not enable the systemd unit, so ufw is inactive again after a reboot until you run sudo systemctl enable ufw; and sudo ufw reset switches it off and deletes the rules, unlike sudo ufw disable, which keeps them. A plain user gets an error instead of the status, because ufw needs root and /usr/sbin is not on a normal user's PATH.

### Are ufw rules persistent after a reboot?

Yes. Every allow, deny, and limit you add is written to /etc/ufw/user.rules (and user6.rules for IPv6) the moment you run it, and ufw.service reloads them at boot. Nothing else is needed, which is the main reason people pick ufw over raw iptables, where rules vanish at reboot unless you save them. The one way to lose them is sudo ufw reset, which backs the files up with a timestamp suffix in /etc/ufw and then empties them. sudo ufw disable does not delete rules; sudo ufw show added lists them even while the firewall is off.

### Can I use ufw with Docker?

Yes, but not the way you would expect. Docker writes its own iptables rules to publish container ports, in the DOCKER and FORWARD chains, and packets to a published port never pass through the INPUT chain where ufw's rules live. So a container started with -p 8080:80 is reachable from the internet even when ufw shows only port 22 open. Two fixes work: bind the port to localhost (-p 127.0.0.1:8080:80) and put nginx or Caddy in front, or install the ufw-docker script, which adds a filter to the DOCKER-USER chain so ufw route allow rules govern container traffic. Setting iptables to false in daemon.json also stops the bypass but breaks container networking in other ways, so most people avoid it.

### Does ufw block ping?

Not by default. The rules in /etc/ufw/before.rules accept ICMP echo-request before any of your own rules run, so a server with default deny incoming still answers ping. The CLI cannot change that, because ufw's rule syntax has no icmp protocol and sudo ufw deny proto icmp returns ERROR: Unsupported protocol icmp. To stop replying, change the echo-request line in /etc/ufw/before.rules from ACCEPT to DROP, do the same in before6.rules for IPv6, then run sudo ufw reload. Leave the other ICMP types accepted: destination-unreachable carries path MTU discovery, and dropping it breaks large packets on some links.

---
Source: https://sshworkbench.com/cheatsheets/ufw
