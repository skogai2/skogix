# Caddyfile Examples

Caddy is a web server with HTTPS built in: point it at a domain and it obtains and renews the certificate on its own. This sheet collects working Caddyfile examples, from a one-line reverse proxy to Docker, wildcard certificates, and PHP, plus the syntax rules the examples rely on.

Last updated September 11, 2026

On this page

- [Reverse Proxy](#reverse-proxy)
- [Syntax and Comments](#syntax-and-comments)
- [Docker](#docker)
- [Docker Compose](#docker-compose)
- [HTTPS and TLS](#https-and-tls)
- [No Domain or HTTP Only](#no-domain-or-http-only)
- [Wildcard and Cloudflare DNS](#wildcard-and-cloudflare-dns)
- [Subdomains](#subdomains)
- [File Server](#file-server)
- [PHP FastCGI](#php-fastcgi)
- [Basic Auth](#basic-auth)
- [Rewrites and Redirects](#rewrites-and-redirects)
- [Handle and Matchers](#handle-and-matchers)
- [Placeholders](#placeholders)
- [Error Pages](#error-pages)
- [WebSockets](#websockets)
- [Logging](#logging)
- [Caddy Commands](#caddy-commands)
- [Gotchas](#gotchas)

## Reverse Proxy

The site address gets HTTPS automatically; reverse_proxy does the rest. Caddy sets X-Forwarded-For and passes the Host header through on its own.

| Directive | What it does |
|----|----|
| reverse_proxy localhost:3000 | Send every request to one backend |
| reverse_proxy /api/\* localhost:8080 | Proxy only requests matching a path |
| reverse_proxy node1:3000 node2:3000 | Round-robin across several backends |
| reverse_proxy https://10.0.0.5:8443 | Proxy to an upstream that speaks HTTPS |
| lb_policy least_conn | Pick the backend with the fewest active requests |
| health_uri /healthz | Take a backend out of rotation when its health check fails |
| header_up Host {upstream_hostport} | Send the upstream's hostname instead of the site's |

The whole Caddyfile for a single app:

```
example.com {
    reverse_proxy localhost:3000
}
```

Copy

Split an API off from the frontend:

```
example.com {
    handle_path /api/* {
        reverse_proxy localhost:8080
    }
    handle {
        reverse_proxy localhost:3000
    }
}
```

Copy

Load balancing with health checks:

```
example.com {
    reverse_proxy node1:3000 node2:3000 {
        lb_policy least_conn
        health_uri /healthz
        health_interval 10s
    }
}
```

Copy

Caddy already sends X-Forwarded-For, X-Forwarded-Proto, and X-Forwarded-Host on every proxied request, so you rarely need to set them. Backends that expect X-Real-IP do need a line, since Caddy does not send it:

```
example.com {
    reverse_proxy localhost:3000 {
        header_up X-Real-IP {remote_host}
    }
}
```

Copy

When Caddy itself sits behind another proxy or a CDN, tell it which hops to trust so the client IP is read from the incoming header instead of the connection:

```
{
    servers {
        trusted_proxies static 10.0.0.0/8 172.16.0.0/12
    }
}
```

Copy

An internal upstream with a self-signed certificate:

```
example.com {
    reverse_proxy https://10.0.0.5:8443 {
        transport http {
            tls_insecure_skip_verify
        }
    }
}
```

Copy

tls_insecure_skip_verify disables certificate checks, so keep it for backends you control on a private network.

## Syntax and Comments

A Caddyfile is one optional global options block followed by site blocks. Comments start with \# and run to the end of the line; there is no block comment form.

```
# Global options come first and have no site address
{
    email [email protected]
    admin off
}

# One site block per address
example.com {
    reverse_proxy localhost:3000 # trailing comments work too
}
```

Copy

[TABLE]

Useful global options:

| Option | What it does |
|----|----|
| email [\[email protected\]](https://sshworkbench.com/cdn-cgi/l/email-protection) | ACME account address for every site |
| debug | Verbose logs, including ACME failures |
| admin off | Turn off the admin API on port 2019 |
| admin :2019 | Move or expose the admin API |
| auto_https off | No certificates and no HTTP to HTTPS redirect |
| auto_https disable_redirects | Keep certificates, drop the port 80 redirect |
| http_port 8080 | Listen somewhere other than 80 |
| order \<directive\> before \<other\> | Change where a plugin directive runs |

Directives run in Caddy's own fixed order, not the order you wrote them. caddy fmt --overwrite Caddyfile normalizes indentation to tabs, and caddy validate --config Caddyfile checks the config without starting the server.

## Docker

The official image reads /etc/caddy/Caddyfile. Mount your config and a /data volume; /data holds the certificates, so losing it means re-requesting them.

```
docker run -d --name caddy \
  -p 80:80 -p 443:443 -p 443:443/udp \
  -v ./Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data \
  caddy:2
```

Copy

Apply config changes without restarting the container:

```
docker exec -w /etc/caddy caddy caddy reload
```

Copy

A custom image with a DNS plugin baked in:

```
FROM caddy:2-builder AS builder
RUN xcaddy build --with github.com/caddy-dns/cloudflare

FROM caddy:2
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Copy

The docker run flags themselves are covered in the [Docker cheat sheet](https://sshworkbench.com/cheatsheets/docker).

## Docker Compose

```
services:
  caddy:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Copy

Other services in the same Compose file are reachable by service name, so the Caddyfile proxies to them directly:

```
example.com {
    reverse_proxy app:3000
}
```

Copy

The 443:443/udp mapping is for HTTP/3; Caddy enables it by default. Compose commands themselves are in the [Docker Compose cheat sheet](https://sshworkbench.com/cheatsheets/docker-compose).

## HTTPS and TLS

Any site address with a domain gets a Let's Encrypt or ZeroSSL certificate automatically, plus the HTTP to HTTPS redirect. The tls directive only exists for the exceptions.

| Directive | What it does |
|----|----|
| example.com { ... } | Automatic public certificate, renewed for you |
| tls [\[email protected\]](https://sshworkbench.com/cdn-cgi/l/email-protection) | Set the ACME account email for expiry notices |
| tls internal | Self-signed certificate from Caddy's local CA |
| tls cert.pem key.pem | Use a certificate you already have |
| http://example.com | Opt this one site out of HTTPS |
| auto_https off | Global option: no certificates, no redirects |

Set the email once globally instead of per site:

```
{
    email [email protected]
}

example.com {
    reverse_proxy localhost:3000
}
```

Copy

Use the Let's Encrypt staging CA while testing, so failures do not hit rate limits:

```
example.com {
    tls {
        ca https://acme-staging-v02.api.letsencrypt.org/directory
    }
    reverse_proxy localhost:3000
}
```

Copy

On your own machine, localhost as the site address gets a locally trusted certificate. Run caddy trust once so browsers accept it.

```
localhost {
    reverse_proxy localhost:3000
}
```

Copy

Check what a live domain is actually serving with the [SSL checker](https://sshworkbench.com/tools/ssl-checker).

## No Domain or HTTP Only

Caddy only goes looking for a public certificate when the site address is a domain name. Give it a port or an IP and it serves plain HTTP without touching Let's Encrypt.

[TABLE]

A home server reachable only on the LAN, with no port forwarding and no public DNS:

```
http://192.168.1.10 {
    reverse_proxy localhost:8096
}
```

Copy

The same host over HTTPS, using Caddy's own CA:

```
home.lan {
    tls internal
    reverse_proxy localhost:8096
}
```

Copy

Run caddy trust on the server to install that CA locally. Other machines need the root certificate from /var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt added to their own trust store, or they will show a warning.

To turn off certificates and the port 80 redirect across the whole config at once:

```
{
    auto_https off
}
```

Copy

## Wildcard and Cloudflare DNS

A wildcard certificate requires the DNS challenge, which requires a DNS provider module the stock binary does not ship. Install one with caddy add-package github.com/caddy-dns/cloudflare (or build with xcaddy, see the Docker section), then give it an API token with Zone Read and DNS Edit permissions.

```
*.example.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }

    @app host app.example.com
    handle @app {
        reverse_proxy localhost:3001
    }

    @blog host blog.example.com
    handle @blog {
        reverse_proxy localhost:3002
    }

    handle {
        abort
    }
}
```

Copy

One certificate covers every subdomain, and new subdomains never appear in certificate transparency logs. The handle blocks route by hostname inside the single wildcard site; abort drops requests for subdomains you have not defined.

## Subdomains

Several addresses can share one block when they serve the same thing. Caddy gets a certificate covering all of them:

```
example.com, www.example.com, example.net {
    reverse_proxy localhost:3000
}
```

Copy

Without a wildcard, each subdomain that serves something different is its own site block with its own certificate. Caddy fetches them all.

```
app.example.com {
    reverse_proxy localhost:3001
}

api.example.com {
    reverse_proxy localhost:8080
}
```

Copy

Share settings between blocks with a snippet:

```
(common) {
    encode zstd gzip
    header -Server
}

app.example.com {
    import common
    reverse_proxy localhost:3001
}

api.example.com {
    import common
    reverse_proxy localhost:8080
}
```

Copy

## File Server

file_server is off by default; root sets where it serves from. The \* after root is a path matcher meaning all requests.

```
example.com {
    root * /var/www/site
    encode zstd gzip
    file_server
}
```

Copy

A directory listing for sharing files:

```
files.example.com {
    root * /srv/files
    file_server browse
}
```

Copy

A single-page app, where every unknown path falls back to index.html:

```
app.example.com {
    root * /var/www/app
    encode zstd gzip
    try_files {path} /index.html
    file_server
}
```

Copy

## PHP FastCGI

php_fastcgi bundles the try_files rewrite to index.php, the FastCGI transport, and the file server hand-off, so WordPress, Laravel, and Nextcloud work with one line.

```
example.com {
    root * /var/www/site
    encode zstd gzip
    php_fastcgi unix//run/php/php8.3-fpm.sock
    file_server
}
```

Copy

For PHP-FPM listening on TCP instead of a socket:

```
php_fastcgi 127.0.0.1:9000
```

Copy

The socket path must match your PHP version; check it with ls /run/php/.

## Basic Auth

The directive is basic_auth since Caddy 2.8 (the old spelling basicauth still works but is deprecated). Passwords are bcrypt hashes; generate one with caddy hash-password.

```
example.com {
    basic_auth {
        alice $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
    }
    reverse_proxy localhost:3000
}
```

Copy

That hash is the Caddy docs example for the password hiccup; replace it with your own. Protect only part of a site with a path matcher:

```
example.com {
    basic_auth /admin/* {
        alice $2a$14$...
    }
    reverse_proxy localhost:3000
}
```

Copy

## Rewrites and Redirects

redir sends the browser somewhere else; rewrite changes the path internally without the URL bar moving.

| Directive | What it does |
|----|----|
| redir /old /new permanent | 301 one path to another |
| redir https://example.com{uri} permanent | Redirect a whole host, keeping the path |
| rewrite /old-page /new-page | Serve different content, URL unchanged |
| uri strip_prefix /api | Drop a prefix before later directives see the path |
| try_files {path} /index.html | Rewrite to a fallback when the file does not exist |

Redirect www to the apex domain:

```
www.example.com {
    redir https://example.com{uri} permanent
}

example.com {
    reverse_proxy localhost:3000
}
```

Copy

## Handle and Matchers

Named matchers start with @ and can combine host, path, header, and method conditions. handle blocks are mutually exclusive: the first matching block wins, so put specific routes before the catch-all.

```
example.com {
    @static path *.css *.js *.svg *.woff2
    handle @static {
        root * /var/www/site
        header Cache-Control "public, max-age=31536000, immutable"
        file_server
    }

    handle_path /api/* {
        reverse_proxy localhost:8080
    }

    handle {
        reverse_proxy localhost:3000
    }
}
```

Copy

handle_path behaves like handle but strips the matched prefix, so the backend above sees /users, not /api/users.

Caddy runs directives in a fixed order regardless of how you wrote them. When two directives must run in a specific sequence, wrap them in route, which keeps your order and, unlike handle, is not mutually exclusive with its siblings:

```
example.com {
    route {
        uri strip_prefix /app
        rewrite * /index.html
        reverse_proxy localhost:3000
    }
}
```

Copy

## Placeholders

Placeholders are {...} values Caddy fills in per request. They work in most directive arguments, including respond, redir, header, log, and reverse_proxy header lines.

[TABLE]

{env.VAR} and {\$VAR} are not the same. {\$VAR} is textual substitution done while the Caddyfile is parsed, so it can appear anywhere, even inside a site address. {env.VAR} is looked up when the request or the certificate is handled, so it only works where Caddy supports placeholders.

```
{$SITE_ADDRESS} {
    reverse_proxy localhost:{$APP_PORT}
}
```

Copy

## Error Pages

respond returns a body straight from Caddy with no backend, error raises a status that handle_errors can then catch, and handle_errors renders whatever the routes failed with.

```
example.com {
    handle /health {
        respond "OK" 200
    }

    handle /admin* {
        error 403
    }

    handle {
        reverse_proxy localhost:3000
    }

    handle_errors {
        rewrite * /{err.status_code}.html
        root * /var/www/errors
        file_server
    }
}
```

Copy

A single page for every error, instead of one file per status code:

```
handle_errors {
    respond "{err.status_code} {err.status_text}" {err.status_code}
}
```

Copy

The difference matters: respond 403 sends the status straight to the client and handle_errors never sees it, while error 403 hands control to handle_errors so your styled page renders. abort drops the connection without answering at all.

## WebSockets

reverse_proxy handles WebSocket upgrades automatically; a plain proxy needs nothing extra. A matcher is only needed when socket traffic goes to a different backend than normal requests:

```
example.com {
    @websockets {
        header Connection *Upgrade*
        header Upgrade websocket
    }
    reverse_proxy @websockets localhost:6001
    reverse_proxy localhost:8080
}
```

Copy

## Logging

Caddy logs its own runtime messages to stderr, but per-site access logs are off until you add log. The default format is JSON; format console is easier to read by eye.

```
example.com {
    log {
        output file /var/log/caddy/example.log {
            roll_size 10MiB
            roll_keep 5
        }
    }
    reverse_proxy localhost:3000
}
```

Copy

Verbose output for debugging certificate problems goes in the global options:

```
{
    debug
}
```

Copy

## Caddy Commands

[TABLE]

## Gotchas

- basicauth
  became
  basic_auth
  in Caddy 2.8. The old name still parses, but new configs should use the underscore form.
- In Docker, always mount a volume at
  /data
  . Without it, every container recreate re-requests certificates and can hit Let's Encrypt rate limits within a day.
- caddy reload
  run from the wrong directory silently reloads nothing useful. Pass
  --config /etc/caddy/Caddyfile
  when in doubt.
- Behind Cloudflare's orange-cloud proxy, the HTTP ACME challenge never reaches your server. Use the DNS challenge or disable the proxy while issuing.
- A site address with no scheme serves HTTPS and redirects port 80. Prefix
  http://
  for a plain HTTP site instead of fighting the redirect.
- HTTP/3 is on by default. If browsers report flaky connections, check UDP 443 through the firewall, not just TCP.
- Migrating an existing nginx config? The [nginx to Caddy converter](https://sshworkbench.com/tools/nginx-to-caddy) translates server blocks to Caddyfile syntax.

### Config changes without the white knuckles

SSH Workbench lets you browse and edit configs, tail logs, and restart the service from one place over plain SSH, so a reload never means six terminal tabs.

[Try free for 7 days](https://sshworkbench.com/#install)

## Caddy FAQ

### What format is a Caddyfile?

It is Caddy's own plain-text format, not JSON, YAML, or TOML, and it needs no file extension. Caddy's native configuration language is actually JSON; the Caddyfile is a convenience layer that gets adapted to that JSON every time Caddy starts or reloads. caddy adapt --pretty prints the JSON your Caddyfile turns into, which is the fastest way to see what a directive really did. Anything expressible in the Caddyfile is expressible in JSON, but not the reverse, so a few advanced options are JSON-only.

### Where is the Caddyfile located?

There is no fixed location. caddy run and caddy reload look for a file named Caddyfile in the current directory unless you pass --config. The Debian, Ubuntu, and Fedora packages, and the official Docker image, all use /etc/caddy/Caddyfile, which is why that path shows up in most examples. Homebrew puts it in /opt/homebrew/etc/Caddyfile on Apple Silicon. To see which config a running instance actually loaded, query the admin API with curl localhost:2019/config/ rather than guessing from the file on disk.

### How do I comment in a Caddyfile?

Use \#, which comments out the rest of the line. The \# has to start a token, meaning it needs whitespace or a line break in front of it, so reverse_proxy localhost:3000 \# main app works but localhost:3000#app does not. There is no block comment syntax, so commenting out a whole site block means prefixing every line. Inside a quoted string \# is a literal character, which matters for header values like "public, max-age=31536000". caddy fmt preserves comments.

### How do I format a Caddyfile?

caddy fmt --overwrite Caddyfile rewrites the file in place with Caddy's own conventions: tabs for indentation, one directive per line, consistent brace placement. The warning 'Caddyfile input is not formatted' on run or reload means the file does not match that output. It is only a warning, the config still loads, so nothing is broken, but running caddy fmt clears it. Formatting is not validation: caddy fmt happily formats a config with unknown directives, so follow it with caddy validate --config Caddyfile.

### How do I reload the Caddyfile without downtime?

Run caddy reload from the directory that holds the Caddyfile, or caddy reload --config /etc/caddy/Caddyfile from anywhere. Caddy applies the new config with zero downtime, and if the file has an error it keeps running on the old config instead of dying. On Debian and Ubuntu package installs, systemctl reload caddy does the same thing. In Docker, run docker exec -w /etc/caddy caddy caddy reload after editing the mounted file; restarting the container also works but drops open connections.

---
Källa: https://sshworkbench.com/cheatsheets/caddy
