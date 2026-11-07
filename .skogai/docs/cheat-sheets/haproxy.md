# HAProxy Config

HAProxy is the TCP and HTTP load balancer in front of many busy Linux sites. This sheet covers the config file itself, frontends, backends, ACLs, SSL, timeouts, and rate limiting, alongside the commands that check a config, reload it without dropping connections, and drive the stats socket.

## Config File

One file, /etc/haproxy/haproxy.cfg, read top to bottom and built out of named blocks.

| Section | Purpose |
|---|---|
| `global` | Process-wide settings (user, group, logging, SSL ciphers) |
| `defaults` | Default settings inherited by frontend and backend sections |
| `frontend` | Defines client-facing listening sockets, SSL, and routing rules |
| `backend` | Defines pool of upstream servers and healthcheck policies |
| `listen` | Combines frontend and backend into a single self-contained block |

| Section | Purpose |
|---|---|
| `global` | Process-wide settings (user, group, logging, SSL ciphers) |
| `defaults` | Default settings inherited by frontend and backend sections |
| `frontend` | Defines client-facing listening sockets, SSL, and routing rules |
| `backend` | Defines pool of upstream servers and healthcheck policies |
| `listen` | Combines frontend and backend into a single self-contained block |

There is no include directive. Split a large config by passing a directory to -f (or by dropping files in conf.d/), which loads every .cfg in it in name order. A second defaults block resets the inheritance for everything after it, which is how one file serves both HTTP and TCP sections.

## Frontend, Backend & Listen

A frontend accepts traffic, a backend holds the server pool, and listen is both in one block. A minimal complete config:

```
global
    log /dev/log local0
    stats socket /run/haproxy/admin.sock mode 660 level admin

defaults
    mode http
    log global
    option httplog
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend fe_web
    bind :80
    default_backend bk_web

backend bk_web
    balance roundrobin
    server web1 10.0.0.11:8080 check
    server web2 10.0.0.12:8080 check
```

The built-in stats page is the classic listen block:

```
listen stats
    bind :8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats auth admin:changeme
```

Add stats admin if TRUE to enable/disable servers from the page itself; keep the port firewalled or bound to an internal address.

## Check the Config

Always check before a reload; a config error found at reload time is a config error found the hard way.

| Command | What it does |
|----|----|
| haproxy -c -f /etc/haproxy/haproxy.cfg | Parse the config, exit 0 when valid |
| haproxy -c -V -f /etc/haproxy/haproxy.cfg | Same, and print "Configuration file is valid" |
| haproxy -c -f /etc/haproxy/conf.d/ | Check every config file in a directory, loaded in name order |

Chain the check with the reload so a typo never goes live:

```bash
haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy
```

## Service Control

HAProxy runs under systemd on every mainstream distro; the [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl) covers the full service surface.

| Command | What it does |
|----|----|
| sudo systemctl reload haproxy | Apply config changes without dropping connections |
| sudo systemctl restart haproxy | Full restart; drops every active connection |
| sudo systemctl start haproxy | Start the service |
| sudo systemctl stop haproxy | Stop it |
| sudo systemctl enable --now haproxy | Start now and on every boot |
| systemctl status haproxy | Running or not, recent log lines, worker PIDs |
| ss -tlnp \| grep haproxy | Confirm which ports it is actually listening on |

Reload is the one to remember: it starts new workers on the new config while the old workers finish their existing connections.

## Stats Socket

Runtime admin without touching the config, also called the Runtime API. It needs one line in the global section, then a reload:

```
global
    stats socket /run/haproxy/admin.sock mode 660 level admin
```

Send commands with socat, one-shot or interactive:

```
echo "show stat" | socat stdio /run/haproxy/admin.sock
socat readline /run/haproxy/admin.sock    # interactive; type "prompt" to keep it open
```

| Socket command | What it does |
|----|----|
| show info | Version, uptime, current and max connections |
| show stat | Full stats as CSV: every frontend, backend, and server |
| show servers state | Every backend server with its state and health |
| disable server bk_web/web1 | Stop sending traffic to a server (maintenance) |
| enable server bk_web/web1 | Put it back in rotation |
| set server bk_web/web1 state drain | No new connections; existing ones finish |
| set server bk_web/web1 state ready | Back to normal after drain or maint |
| set weight bk_web/web1 50 | Change a server's load balancing weight |
| show sess | List live sessions |
| shutdown sessions server bk_web/web1 | Kill every session on one server |
| show errors | Recent request and response parse errors |
| show table | Stick table contents, e.g. rate limiting counters |
| clear counters | Reset the stats counters |
| set maxconn global 10000 | Change the global connection limit live |
| help | List every socket command this build supports |

show stat prints around 80 columns. This trims it to name, status, and weight:

```
echo "show stat" | socat stdio /run/haproxy/admin.sock | cut -d, -f1,2,18,19 | column -s, -t
```

## Logs

HAProxy logs through syslog, not to a file of its own. On Debian and Ubuntu the packaged rsyslog rule writes traffic to /var/log/haproxy.log.

| Command | What it does |
|----|----|
| tail -f /var/log/haproxy.log | Follow live traffic logs |
| journalctl -u haproxy -n 50 | Process events only: starts, reloads, config warnings |
| grep ' 503 ' /var/log/haproxy.log | Find requests that got a 503 |
| halog -srv < /var/log/haproxy.log | Per-server report: errors and response times (halog ships with HAProxy) |
| halog -u < /var/log/haproxy.log | Per-URL report from the same log |

The config side that makes traffic logging work:

```
global
    log /dev/log local0

defaults
    log global
    mode http
    option httplog
    option dontlognull
```

journalctl -u haproxy is still where reload failures land; the [journalctl cheat sheet](https://sshworkbench.com/cheatsheets/journalctl) covers filtering it.

## Termination State

Every option httplog line ends with a four-character field, the session state at disconnection. The first character says who ended the session and the second says what it was doing, which is usually enough to tell a client problem from a backend problem.

| Flag Code | Meaning | Common Cause |
|---|---|---|
| `CD` | Client disconnected | Client aborted connection before transfer finished |
| `sD` | Server disconnected | Upstream server closed connection unexpectedly |
| `CC` | Client aborted during connect | Client dropped while waiting for backend connection |
| `CS` | Connection refused by server | Backend server down or port unreachable |
| `PR` | Proxy rejected | Client request rejected by HAProxy ACL or inspection rule |

Lowercase first character means a timeout, uppercase means an abort or an explicit action. A run of sH-- points at timeout server being shorter than the app's slowest response.

## Health Checks

check on a server line turns on TCP health checks; option httpchk upgrades them to real HTTP requests.

```
backend bk_web
    option httpchk
    http-check send meth GET uri /health hdr Host example.com
    http-check expect status 200
    server web1 10.0.0.11:8080 check inter 2s fall 3 rise 2
    server web2 10.0.0.12:8080 check inter 2s fall 3 rise 2
    server spare 10.0.0.13:8080 check backup
```

| Server option | What it does                                   |
|---------------|------------------------------------------------|
| check         | Enable health checks on this server            |
| inter 2s      | Time between checks                            |
| fall 3        | Failed checks before the server is marked down |
| rise 2        | Passed checks before it comes back up          |
| backup        | Only used when every non-backup server is down |
| maxconn 200   | Cap concurrent connections to this server      |

Watch the results with show servers state on the stats socket, or on the stats page.

## Command Line Options

| Command | What it does |
|---|---|
| `haproxy -c -f /etc/haproxy/haproxy.cfg` | Check configuration syntax without starting |
| `haproxy -f /etc/haproxy/haproxy.cfg -D` | Start HAProxy in daemon mode |
| `haproxy -f cfg -st $(cat /run/haproxy.pid)` | Gracefully reload with zero-downtime socket transfer |

## Balance

| Algorithm | Behavior |
|---|---|
| `roundrobin` | Sequential distribution with dynamic server weights |
| `leastconn` | Routes connection to backend server with lowest active connection count |
| `source` | Hashes client IP to ensure same client reaches same backend |
| `uri` | Hashes requested URI path for caching proxy efficiency |

Cookie-based sticky sessions, which survive a server coming back better than balance source does:

```
backend bk_app
    balance roundrobin
    cookie SRV insert indirect nocache
    server app1 10.0.0.11:8080 check cookie a1
    server app2 10.0.0.12:8080 check cookie a2
```

balance source re-hashes when a server goes down, which moves other clients too. The cookie only moves the clients on the dead server.

## ACLs

ACLs name a condition; use_backend, http-request, and friends act on it. Rules run top to bottom, first match wins.

```
frontend fe_web
    bind :80
    acl is_api path_beg /api
    acl is_static path_end .css .js .png .jpg
    acl host_blog hdr(host) -i blog.example.com
    acl internal src 10.0.0.0/8 192.168.0.0/16
    http-request deny if is_api !internal
    use_backend bk_api if is_api
    use_backend bk_blog if host_blog
    use_backend bk_static if is_static
    default_backend bk_web
```

Anonymous ACLs inline in braces work too, as in redirect scheme https unless { ssl_fc }.

## Headers

The backend sees HAProxy's IP, not the client's, until you say otherwise. option forwardfor belongs in defaults so every backend inherits it.

| Directive | Action |
|---|---|
| `http-request set-header X-Forwarded-Proto https` | Set header to explicit value |
| `http-request add-header X-Real-IP %[src]` | Append header with client IP address |
| `http-request del-header Proxy` | Remove dangerous or untrusted header |
| `http-response set-header X-Server %s` | Return backend server name in response header |

%[...] is a fetch evaluated per request; %{+Q}[...] quotes the result, which matters for anything that can contain spaces. The app still has to trust X-Forwarded-For, and it should only do that when HAProxy is the only thing that can reach it.

## HTTPS & SSL

HAProxy terminates TLS on the bind line. The crt file is the certificate, any intermediate chain, and the private key concatenated into one PEM, in that order.

```
frontend fe_https
    bind :443 ssl crt /etc/haproxy/certs/example.com.pem alpn h2,http/1.1
    http-request set-header X-Forwarded-Proto https
    default_backend bk_web
```

Building that PEM from a Let's Encrypt certificate:

```bash
sudo cat /etc/letsencrypt/live/example.com/fullchain.pem \
         /etc/letsencrypt/live/example.com/privkey.pem \
  | sudo tee /etc/haproxy/certs/example.com.pem > /dev/null
```

Point crt at a directory to load every certificate in it; HAProxy picks the right one per request by SNI. Verify the served chain with the [SSL checker](https://sshworkbench.com/tools/ssl-checker).

## Redirects

```
frontend fe_web
    bind :80
    bind :443 ssl crt /etc/haproxy/certs/example.com.pem
    http-request redirect scheme https code 301 unless { ssl_fc }
    http-request redirect prefix https://example.com code 301 if { hdr(host) -i www.example.com }
```

The first rule sends every plain HTTP request to HTTPS; the second folds www onto the bare domain while keeping the path.

## Timeouts & Limits

timeout connect, timeout client, and timeout server have no defaults. Leave them out and HAProxy warns at startup, then lets stuck connections sit forever.

```
defaults
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    timeout http-request 10s
    timeout http-keep-alive 10s
    timeout queue 30s
    timeout check 5s
    timeout tunnel 1h
```

| Directive | Recommended Default | Purpose |
|---|---|---|
| `timeout connect` | `5s` | Max time waiting to establish connection with backend |
| `timeout client` | `50s` | Max inactivity time on client side |
| `timeout server` | `50s` | Max inactivity time on server side |
| `timeout http-request` | `10s` | Max time waiting for complete HTTP request headers |
| `maxconn` | `50000` | Maximum simultaneous open connections |

Raise timeout tunnel for WebSockets: after the upgrade, timeout client and timeout server no longer apply, so a short tunnel timeout is what cuts idle sockets.

## Rate Limiting

A stick table counts what a key does; a rule reads the counter and acts.

```
frontend fe_web
    bind :80
    stick-table type ip size 100k expire 60s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
```

| Socket command | What it does |
|----|----|
| show table fe_web | Every key in the table with its counters |
| show table fe_web data.http_req_rate gt 50 | Only the keys over a threshold |
| clear table fe_web key 203.0.113.9 | Drop one entry, which unbans that IP |
| clear table fe_web | Empty the table |
| set table fe_web key 203.0.113.9 data.http_req_rate 0 | Reset one counter |

Swap http_req_rate for conn_rate(10s) to limit new connections, or conn_cur for concurrent ones. For a block that outlives the request, track the source in a second table with a longer expire and deny on sc_get_gpc0.

## TCP Mode

mode tcp proxies raw bytes: databases, SMTP, Redis, anything that is not HTTP. Frontend and backend must both be mode tcp.

```
frontend fe_pg
    mode tcp
    bind :5432
    default_backend bk_pg

backend bk_pg
    mode tcp
    balance leastconn
    option tcp-check
    server pg1 10.0.0.21:5432 check
    server pg2 10.0.0.22:5432 check backup
```

leastconn beats roundrobin for long-lived connections like database sessions.

## SNI

To route TLS by hostname without terminating it (passthrough), read the SNI from the ClientHello in TCP mode:

```
frontend fe_tls_passthrough
    mode tcp
    bind :443
    tcp-request inspect-delay 5s
    tcp-request content accept if { req_ssl_hello_type 1 }
    use_backend bk_app1 if { req_ssl_sni -i app1.example.com }
    use_backend bk_app2 if { req_ssl_sni -i app2.example.com }
```

The backends stay mode tcp and the apps keep their own certificates. When HAProxy terminates TLS itself, match on ssl_fc_sni instead of req_ssl_sni.

## Docker

The official image reads /usr/local/etc/haproxy/haproxy.cfg, not /etc/haproxy, and runs as the haproxy user. Docker's default capability set includes NET_BIND_SERVICE, so binding :80 inside the container still works.

```bash
docker run -d --name hap -p 80:80 -p 443:443 \
  -v "$PWD/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro" \
  haproxy:3.0

# check a config without installing HAProxy at all
docker run --rm -v "$PWD/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro" \
  haproxy:3.0 haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg
```

| Command | What it does |
|----|----|
| docker kill -s HUP hap | Reload the config in place, no container restart |
| docker exec -it hap haproxy -vv | Build info and compiled features for that image |
| docker logs -f hap | Follow the logs |
| docker compose up -d --force-recreate haproxy | Pick up a changed mount under Compose |

There is no syslog socket in the container, so send logs to stdout instead:

```
global
    log stdout format raw local0 info
```

The [docker cheat sheet](https://sshworkbench.com/cheatsheets/docker) covers the container side.

## Install

| Distribution | Command |
|---|---|
| Debian / Ubuntu | `sudo apt install haproxy` |
| Arch Linux | `sudo pacman -S haproxy` |
| Fedora / RHEL | `sudo dnf install haproxy` |

The distro package is fine for most sites; the PPA is for when you need a feature from a newer branch. The http-check send syntax used above needs 2.2 or newer, so check haproxy -v before copying config off the internet.

## Keepalived

One HAProxy box is a single point of failure. Keepalived runs on two of them and moves a floating IP (VRRP) to whichever is alive, so clients only ever see one address.

```
vrrp_script chk_haproxy {
    script "killall -0 haproxy"
    interval 2
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 101
    virtual_ipaddress {
        203.0.113.50
    }
    track_script {
        chk_haproxy
    }
}
```

The backup node uses state BACKUP and a lower priority. Set net.ipv4.ip_nonlocal_bind=1 in sysctl on both so HAProxy can bind the floating IP while it lives on the other box.

## Gotchas

- systemctl restart drops every active connection. After a config edit, reload is what you want, and only after haproxy -c passes.
- Stats socket changes ( disable server, set weight, set maxconn) vanish at the next reload. Anything permanent belongs in the config file.
- The crt PEM must contain the private key. Certbot's fullchain.pem alone fails at startup with "unable to load SSL private key".
- No traffic logs usually means a missing log /dev/log local0 or rsyslog rule; journalctl -u haproxy only ever shows process events. With chroot enabled, the syslog socket must exist inside the chroot (the Debian package sets this up).
- A 503 from HAProxy itself, with the backends supposedly fine, means no server in the chosen backend passed its health check. show servers state on the stats socket says why.
- mode must match between a frontend and the backends it routes to; haproxy -c catches the mismatch, another reason to run it every time.
- "cannot bind socket (permission denied)" on:80 or:443 means HAProxy is no longer root at bind time. The packaged unit binds as root and then drops to the haproxy user; a hardened unit or a container needs CAP_NET_BIND_SERVICE instead. The same message with a bind on a floating IP usually needs net.ipv4.ip_nonlocal_bind=1.
- mode and the timeouts come from the nearest defaults block above a section, not from the first one in the file. Add a second defaults for the TCP sections and everything after it inherits that one, HTTP sections included.

## HAProxy FAQ

### Where is the HAProxy config file?

/etc/haproxy/haproxy.cfg on Debian, Ubuntu, RHEL, and their derivatives; the systemd unit picks it up through the CONFIG variable in /etc/default/haproxy or /etc/sysconfig/haproxy. Recent units also load /etc/haproxy/conf.d/ as a directory, so extra .cfg files there are merged in filename order and you can split per-site blocks out of the main file. The official Docker image is the odd one out at /usr/local/etc/haproxy/haproxy.cfg, and pfSense and OPNsense generate the file from their web UI, so edit those there rather than on disk.

### Is HAProxy layer 4 or layer 7?

Both, and the mode line decides which. mode http parses requests, so ACLs can match paths and headers, cookies can pin sessions, and HAProxy can rewrite what it forwards; that is layer 7. mode tcp forwards bytes without reading them, which is what you want for Postgres, SMTP, Redis, or TLS passthrough; that is layer 4. The mode must match between a frontend and every backend it routes to. In TCP mode you can still route on the TLS SNI, because that field is readable before the handshake completes.

### How do I check the HAProxy config before reloading?

Run haproxy -c -f /etc/haproxy/haproxy.cfg. It exits 0 when the config parses and prints each error with its line number when it does not; add -V for an explicit 'Configuration file is valid'. Chain it with the reload so a typo never takes the proxy down: haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy. A failed reload under systemd leaves the old process running, but the check gives you the error message instead of a silent unit failure.

### How do I reload HAProxy without dropping connections?

sudo systemctl reload haproxy. Modern packages run HAProxy in master-worker mode, so a reload starts new workers on the new config while the old workers finish their existing connections and then exit. systemctl restart is different: it stops the process first and drops every active connection. Long-lived connections such as WebSockets can keep an old worker alive for a long time; cap that with hard-stop-after 30s in the global section.

### Where does HAProxy write its logs?

To syslog, not to a file of its own. The config needs log /dev/log local0 in the global section and log global with option httplog in defaults; the Debian and Ubuntu packages ship an rsyslog rule that then writes traffic to /var/log/haproxy.log. journalctl -u haproxy shows only process events such as starts, reloads, and config warnings. If the log file stays empty, the rsyslog rule is missing or HAProxy is chrooted without a syslog socket inside the chroot.

---
Source: https://sshworkbench.com/cheatsheets/haproxy
