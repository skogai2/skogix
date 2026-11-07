# nginx Directives

nginx is the web server and reverse proxy in front of most Linux deployments. This sheet covers the directives you edit most, which block each one is allowed in, and the commands that test and reload a config safely.

Last updated September 11, 2026

On this page

- [Test and Reload](#test-and-reload)
- [Server Blocks](#server-blocks)
- [Location Matching](#location-matching)
- [Reverse Proxy](#reverse-proxy)
- [Upstream](#upstream)
- [root vs alias](#root-vs-alias)
- [Redirects and Rewrites](#redirects-and-rewrites)
- [SSL](#ssl)
- [Gzip and Caching](#gzip-and-caching)
- [map](#map)
- [Variables](#variables)
- [Includes and File Locations](#includes-and-file-locations)
- [Logs and Error Pages](#logs-and-error-pages)
- [Allow, Deny and Auth](#allow-deny-and-auth)
- [Timeouts and Limits](#timeouts-and-limits)
- [Stream](#stream)
- [Global and Events](#global-and-events)
- [Modules](#modules)
- [Context Rules](#context-rules)
- [Order and Inheritance](#order-and-inheritance)
- [Gotchas](#gotchas)

## Test and Reload

Never restart when a reload will do. Reload keeps existing connections open and falls back to the old config if the new one is broken.

[TABLE]

The safe edit loop, in one line:

```
sudo nginx -t && sudo systemctl reload nginx
```

Copy

## Server Blocks

One server block per site (virtual host). nginx picks the block by matching listen port, then server_name: exact name, longest \*. wildcard, first matching regex, then the default_server.

[TABLE]

A minimal static site:

```
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    root /var/www/example;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Copy

The [nginx config generator](https://sshworkbench.com/tools/nginx-config-generator) builds a full server block from a form.

## Location Matching

File order does not decide prefix matches. nginx checks = first, then the longest prefix, then regexes in file order; the first regex hit wins, and only if none match does the longest prefix apply.

| Pattern | How it matches |
|----|----|
| location = /health | Exact URI only, checked first |
| location ^~ /static/ | Prefix; if it is the longest prefix, skip regex checks |
| location ~ \\php\$ | Regex, case-sensitive |
| location ~\* \\(jpg\|png\|webp)\$ | Regex, case-insensitive |
| location /api/ | Plain prefix |
| location / | Prefix that matches everything, the fallback |
| try_files \$uri \$uri/ /index.php?\$args; | Serve the file, else the directory, else hand off |
| try_files \$uri \$uri/ =404; | Serve the file or return 404 |

## Reverse Proxy

proxy_pass forwards requests to an app server. Pass the headers below or the app sees every request as coming from 127.0.0.1 over HTTP.

| Directive | What it does |
|----|----|
| proxy_pass http://127.0.0.1:3000; | Forward to the app, URI passed through unchanged |
| proxy_pass http://127.0.0.1:3000/; | Trailing slash: the location prefix is stripped first |
| proxy_set_header Host \$host; | Give the app the original hostname |
| proxy_set_header X-Real-IP \$remote_addr; | The visitor's IP |
| proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; | The full client IP chain |
| proxy_set_header X-Forwarded-Proto \$scheme; | http or https, so the app builds correct URLs |
| proxy_http_version 1.1; | Needed for websockets and upstream keepalive |
| proxy_buffering off; | Stream responses through (SSE, long polling) |

A complete proxy block, websockets included:

```
location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

Copy

## Upstream

An upstream block names a group of backend servers for proxy_pass http://name;. It lives directly inside http, next to your server blocks, not inside one.

| Directive | What it does |
|----|----|
| server 10.0.0.1:3000; | A backend; round-robin between servers is the default |
| server 10.0.0.2:3000 weight=2; | Gets twice the traffic |
| server 10.0.0.3:3000 backup; | Used only when the others are down |
| server 10.0.0.4:3000 down; | Temporarily out of rotation |
| server ... max_fails=3 fail_timeout=30s; | Mark dead after 3 failures, retry after 30s |
| least_conn; | Send to the backend with fewest active connections |
| ip_hash; | Same client IP always hits the same backend (sticky) |
| keepalive 32; | Pool of idle connections to the backends |

```
upstream app {
    least_conn;
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
    keepalive 32;
}
```

Copy

## root vs alias

root appends the full URI to the path; alias replaces the location prefix with the path.

```
location /img/ { root /var/www; }
# /img/a.png  ->  /var/www/img/a.png

location /img/ { alias /var/www/pics/; }
# /img/a.png  ->  /var/www/pics/a.png
```

Copy

[TABLE]

## Redirects and Rewrites

For a plain redirect, return is simpler and faster than rewrite.

| Directive | What it does |
|----|----|
| return 301 https://example.com\$request_uri; | Permanent redirect, keeps the path and query |
| return 302 /maintenance.html; | Temporary redirect |
| return 404; | Answer with a status code, no redirect |
| rewrite ^/old/(.\*)\$ /new/\$1 permanent; | Regex redirect with a captured path (301) |
| rewrite ^/old/(.\*)\$ /new/\$1 redirect; | Same, temporary (302) |
| rewrite ^/app\$ /app/index.html last; | Internal rewrite, re-runs location matching |
| rewrite ... break; | Internal rewrite, stays in the current location |

The classic www and HTTP cleanup, as separate small server blocks:

```
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://example.com$request_uri;
}

server {
    listen 443 ssl;
    server_name www.example.com;
    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    return 301 https://example.com$request_uri;
}
```

Copy

## SSL

[TABLE]

```
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:SSL:10m;
}
```

Copy

Verify what a live server actually presents with the [SSL checker](https://sshworkbench.com/tools/ssl-checker), and inspect a cert file with the [certificate decoder](https://sshworkbench.com/tools/certificate-decoder).

## Gzip and Caching

[TABLE]

Long cache for fingerprinted static assets:

```
location ~* \.(css|js|png|jpg|svg|woff2)$ {
    expires 365d;
    add_header Cache-Control "public, immutable";
}
```

Copy

## map

map sets one variable from the value of another, and belongs directly inside http. It replaces most if chains.

```
map $http_upgrade $connection_upgrade {
    default upgrade;
    ""      close;
}

map $host $backend {
    hostnames;
    default          http://127.0.0.1:3000;
    api.example.com  http://127.0.0.1:4000;
    *.example.com    http://127.0.0.1:3000;
}
```

Copy

[TABLE]

## Variables

Variables are read anywhere a directive takes a value, and any request header is available as \$http\_\<name\> with dashes turned into underscores.

[TABLE]

## Includes and File Locations

[TABLE]

## Logs and Error Pages

[TABLE]

Startup failures land in the systemd journal rather than the error log; see the [journalctl cheat sheet](https://sshworkbench.com/cheatsheets/journalctl) for journalctl -u nginx.

## Allow, Deny and Auth

Rules are checked top to bottom and the first match wins.

| Directive | What it does |
|----|----|
| allow 192.168.1.0/24; | Permit a network |
| allow 203.0.113.7; | Permit one IP |
| deny all; | Block everyone else; goes last |
| auth_basic "Restricted"; | Ask for a username and password |
| auth_basic_user_file /etc/nginx/.htpasswd; | Where the credentials live |
| satisfy any; | Let a request pass on allowed IP or valid password |

```
location /admin/ {
    satisfy any;
    allow 192.168.1.0/24;
    deny  all;
    auth_basic "Admin";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

Copy

Generate the password file with the [htpasswd generator](https://sshworkbench.com/tools/htpasswd-generator).

## Timeouts and Limits

[TABLE]

## Stream

stream proxies raw TCP and UDP (databases, SMTP, game servers). It sits beside http in nginx.conf, never inside it, which is why pasting one into a conf.d/ file returns "stream directive is not allowed here".

```
stream {
    upstream db {
        server 10.0.0.10:5432;
    }

    server {
        listen 5432;
        proxy_pass db;
    }
}
```

Copy

[TABLE]

## Global and Events

The top of /etc/nginx/nginx.conf, outside every block. Simple directives here end in a semicolon; block directives take braces and no semicolon.

[TABLE]

## Modules

nginx: \[emerg\] unknown directive means nginx does not recognize the name at all. Either it is misspelled, or the module that provides it was never built into this binary or loaded.

[TABLE]

## Context Rules

Every directive is valid only in certain blocks; using the right directive in the wrong block is the "directive is not allowed here" error. Files under conf.d/ and sites-enabled/ are included inside http, so they can hold server, upstream, and map blocks.

[TABLE]

## Order and Inheritance

[TABLE]

## Gotchas

- The trailing slash on
  proxy_pass
  changes the URI: with a URI part (
  http://app/
  ), the matched location prefix is stripped; without one (
  http://app
  ), the path passes through untouched.
- add_header
  in a location throws away every
  add_header
  inherited from
  server
  and
  http
  . Repeat the parents' headers or set them all at one level.
- Prefer
  map
  and
  return
  over
  if
  . Inside a location,
  if
  combined with anything beyond
  return
  or
  rewrite
  behaves in famously surprising ways.
- If no block has
  default_server
  , the first server block for that port silently answers every unmatched hostname, including raw IP requests.
- When
  root
  seems to do nothing, check which server block actually answered (
  nginx -T
  ), whether the
  root
  sits in a location the request never matched, and whether the worker user can traverse every parent directory. The error log prints the exact path nginx tried to open.
- error_page
  ignores statuses that came from a backend until you add
  proxy_intercept_errors on;
  , and the page it points at must be servable by the same server block.

### Config changes without the white knuckles

SSH Workbench lets you browse and edit configs, tail logs, and restart the service from one place over plain SSH, so a reload never means six terminal tabs.

[Try free for 7 days](https://sshworkbench.com/#install)

## nginx FAQ

### What are nginx directives?

A directive is one instruction in the config. Simple directives are a name, its arguments, and a semicolon (root /var/www;). Block directives take braces instead and hold other directives inside them (server { ... }), which is why they take no semicolon. The block a directive sits in is its context, and most directives are valid in only some contexts. Values set in an outer context pass down to the blocks inside it until one of them sets the same directive again.

### Why does nginx say a directive is not allowed here?

The directive is real but sits in the wrong block. Every directive is valid only in certain contexts: alias only inside location, proxy_pass inside location, upstream and map only directly inside http, listen and server_name only inside server, events and stream only in the main context beside http. Files under conf.d/ and sites-enabled/ are included inside the http block, so they can hold server, upstream, and map blocks, but a location pasted at the top of such a file, outside any server block, triggers exactly this error. nginx -t names the file and line.

### What does nginx unknown directive mean?

Unknown directive means nginx does not recognize the name at all, so the module that provides it is not in this build. It is the usual answer for stream, brotli, rtmp, geoip2, and the lua directives. Run nginx -V to see what was compiled in. On Debian and Ubuntu the extras ship as separate packages (apt install libnginx-mod-stream, libnginx-mod-http-geoip2) that drop a load_module line into /etc/nginx/modules-enabled/; on RHEL and Fedora they are the nginx-mod-\* packages. If the name is misspelled or the module is third-party, no package will help and you need a build that includes it.

### What order does nginx apply directives in?

File order rarely decides anything. For locations, nginx checks = first, then the longest matching prefix, then regex locations (~ and ~~\*) in file order, taking the first hit; only when no regex matches does the longest prefix win, and a ^~~ on that prefix skips the regex step. server_name matching goes exact name, then *.example.com, then example.*, then regex, then default_server. Inside a block, allow and deny are read top to bottom with first match winning, and rewrite rules all run in sequence.

### Why is the nginx root directive not working?

Three things cause almost all of it. root appends the whole request URI to the path while alias replaces the matched location prefix, so location /img/ { root /var/www; } reads /var/www/img/a.png and the same location with alias /var/www/pics/ reads /var/www/pics/a.png. A root set inside one location does not apply to requests that matched a different location, so set it once at server level. And the worker user (www-data or nginx) needs execute permission on every parent directory, not just the files. nginx -T shows the root nginx actually ended up with, and the error log prints the full path it tried to open.

---
Källa: https://sshworkbench.com/cheatsheets/nginx
