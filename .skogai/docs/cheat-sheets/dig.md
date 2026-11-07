# dig Command Examples

dig (Domain Information Groper) is the DNS lookup tool that ships with BIND, preinstalled on macOS and most Linux servers. This sheet covers dig command examples for every record type, +short output, querying a specific server, reverse lookups, +trace, and how to read the output.

Last updated September 11, 2026

On this page

- [Basic Queries](#basic-queries)
- [All Records](#all-records)
- [Short Answers](#short-answers)
- [Querying a Specific Server](#querying-a-specific-server)
- [Reverse Lookups](#reverse-lookups)
- [Tracing and Debugging](#tracing-and-debugging)
- [Reading the Output](#reading-the-output)
- [Options](#options)
- [Installing dig](#installing-dig)
- [dig on Windows](#dig-on-windows)
- [dig on macOS](#dig-on-macos)
- [Gotchas](#gotchas)

## Basic Queries

The shape is dig \[@server\] name \[type\]. With no type, dig asks for A records.

[TABLE]

## All Records

There is no working "give me everything" query any more.

| Command | What it does |
|----|----|
| dig example.com ANY | The old catch-all; Cloudflare and others reply with one RFC 8482 HINFO record |
| dig example.com A example.com MX | The practical replacement: repeat name and type per query |
| dig axfr @ns1.example.com example.com | Full zone transfer; refused unless your IP is an allowed secondary |
| dig ixfr=2026010101 @ns1.example.com example.com | Incremental transfer from a zone serial |

Loop the types you actually care about:

```
for t in A AAAA MX TXT NS SOA CAA; do dig +noall +answer example.com "$t"; done
```

Copy

## Short Answers

| Command | What it does |
|----|----|
| dig +short example.com | Just the address, one per line |
| dig +short example.com MX | Priority and mail server, nothing else |
| dig +noall +answer example.com | Full answer records with TTLs, none of the header noise |
| dig +short +identify example.com | Answer plus which server gave it |
| dig +noall +answer +multiline example.com SOA | One field per line; readable for SOA and DNSKEY |

An aliased name prints its whole CNAME chain under +short, one line per step:

```
dig +short www.example.com | tail -n1   # only the final IP address
```

Copy

## Querying a Specific Server

Prefix any query with @server to skip your normal resolver.

| Command | What it does |
|----|----|
| dig @8.8.8.8 example.com | Ask Google's public resolver instead of your own |
| dig @1.1.1.1 example.com MX | Ask Cloudflare's |
| dig @ns1.example.com example.com | Ask the domain's own name server; no cache in the way |
| dig -p 5300 @127.0.0.1 example.com | Non-standard port, for a local test resolver |
| dig example.com +nssearch | SOA serial from every authoritative server; spots a lagging secondary |

Checking whether a DNS change has propagated is a two-query job:

```
dig +short example.com @ns1.example.com   # what the zone actually says
dig +short example.com @8.8.8.8           # what the world still sees cached
```

Copy

## Reverse Lookups

-x takes a plain IP and builds the in-addr.arpa PTR query for you, octet reversal included.

| Command | What it does |
|----|----|
| dig -x 203.0.113.10 | Hostname for an IPv4 address (PTR record) |
| dig -x 203.0.113.10 +short | Just the hostname |
| dig -x 2001:db8::1 | IPv6 reverse; dig writes the nibble name for you |

An empty answer is common here: many addresses simply have no PTR record, and that is not an error.

## Tracing and Debugging

[TABLE]

## Reading the Output

A default dig response, trimmed:

```
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 23918
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;example.com.                 IN      A

;; ANSWER SECTION:
example.com.          300     IN      A       203.0.113.10

;; Query time: 24 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
```

Copy

[TABLE]

## Options

[TABLE]

Batch mode pairs naturally with the short output flags:

```
dig -f domains.txt +noall +answer
```

Copy

Options you always want can live in ~/.digrc, one line, same syntax:

```
+noall +answer
```

Copy

## Installing dig

dig: command not found means the BIND utilities are missing, not that DNS is broken. No distro ships a package called dig.

[TABLE]

## dig on Windows

cmd and PowerShell have no dig. The built-ins cover most lookups, and WSL gives you the real thing.

[TABLE]

ISC stopped building BIND for Windows after 9.16, so standalone dig-for-Windows downloads are old builds. WSL or Chocolatey gets you a current one.

nslookup asks the same servers the same questions, but prints a stripped summary with no TTLs, no flags, and no status line, which is why DNS guides assume dig.

## dig on macOS

dig is preinstalled on every macOS release. It reads /etc/resolv.conf, which macOS generates from the primary network service only, so dig can miss the per-domain resolvers a VPN adds and disagree with the rest of the system.

[TABLE]

Flush the system cache before retesting a record that changed:

```
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

Copy

## Gotchas

- +short
  prints nothing when the name does not exist. Drop it and read the
  status:
  line before deciding a record is missing.
- ANY is effectively dead: Cloudflare and many other servers answer it with a single RFC 8482 HINFO record. Query each type you care about instead.
- dig asks the DNS server directly and ignores
  /etc/hosts
  , nsswitch, and mDNS, so dig can resolve a name that
  ssh
  still cannot, and the other way round. When SSH is the one failing, see [Could not resolve hostname](https://sshworkbench.com/fix/ssh-could-not-resolve-hostname).
- SERVER: 127.0.0.53
  means systemd-resolved answered, possibly from its cache. Retest with
  @1.1.1.1
  before blaming the upstream record.
- A falling TTL plus a 0 ms query time means you are looking at a cached answer, not the zone.
  +trace
  or
  @ns1.example.com
  gets the live data.
- ANY
  and
  axfr
  both look like a way to dump a zone, and neither works against a domain you do not run. See All Records for what to do instead.
- dig missing? It lives in the BIND utilities package, never one called dig. See Installing dig above.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## dig FAQ

### How do I get only the IP address from the dig command?

Add +short: dig +short example.com prints the address and nothing else. For a name behind a CNAME it prints the whole chain, one line per step, so pipe through tail -n1 when you only want the final address. dig +noall +answer is the middle ground: full records with TTLs but none of the header noise. One catch: +short prints nothing at all when the name does not exist, so drop it and check the status line before concluding a record is gone.

### How do I make the dig command use a specific DNS server?

Put the server after an @ anywhere in the command: dig @8.8.8.8 example.com, or dig example.com MX @1.1.1.1. Add -p 5300 for a resolver on a non-standard port. Without @, dig uses the first nameserver line in /etc/resolv.conf, which on current Ubuntu and Fedora is 127.0.0.53, the local systemd-resolved stub answering from its own cache. The SERVER line at the bottom of the output always names who actually replied, so check it before trusting the answer. Pointing @ at the zone's own name server is how you read the record with no cache in the way.

### How do I run the dig command in Windows?

cmd does not ship with dig. nslookup is built in and handles most lookups (nslookup -type=mx example.com 8.8.8.8), PowerShell's Resolve-DnsName does more record types, and if WSL is installed, wsl dig example.com +short gives you the real thing from any cmd window. For a native install, choco install bind-toolsonly puts dig on the PATH. ISC stopped building BIND for Windows after 9.16, so the standalone dig-for-Windows zips floating around are old builds.

### How do I read dig command output?

Read it bottom to top when you are debugging. The SERVER line says who answered, and Query time near 0 msec means it came from a cache rather than the zone. Then the ANSWER SECTION: the number after the name is the TTL in seconds, counting down inside whichever cache holds it. Then the HEADER line: status is the verdict, and the flags matter more than they look. aa means the reply came from a server authoritative for the zone, ad means DNSSEC validated it, and ra means the server you asked is willing to recurse for you. Strip everything but the records with +noall +answer once you know what you are looking at.

### Why does the dig command return no ANSWER SECTION?

Check the status field first. NXDOMAIN means the name does not exist at all. NOERROR with ANSWER: 0 means the name exists but has no record of the type you asked for: a domain with only an A record answers MX queries this way, and querying example.com when the record lives on [www.example.com](http://www.example.com) does too. SERVFAIL usually points at the resolver, often a DNSSEC validation failure; retry with +cd to skip validation, or run dig +trace to see where the chain breaks.

---
Källa: https://sshworkbench.com/cheatsheets/dig
