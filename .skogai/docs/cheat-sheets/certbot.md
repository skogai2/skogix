# Certbot Commands

Certbot is the standard client for getting free Let's Encrypt TLS certificates and renewing them on a schedule. This sheet covers the certbot commands for installing it, nginx and Apache, certonly with the standalone, webroot, and DNS challenges, wildcards, renewal, and deploy hooks.

Last updated September 11, 2026

On this page

- [Install](#install)
- [nginx](#nginx)
- [Apache](#apache)
- [certonly](#certonly)
- [Standalone](#standalone)
- [Webroot](#webroot)
- [DNS Challenge](#dns-challenge)
- [Wildcard Certificates](#wildcard-certificates)
- [Renewal](#renewal)
- [Add and Remove Domains](#add-and-remove-domains)
- [List and Delete](#list-and-delete)
- [Deploy Hooks](#deploy-hooks)
- [Files and Logs](#files-and-logs)
- [Windows](#windows)
- [Account and Version](#account-and-version)
- [Docker](#docker)
- [Command Line Options](#command-line-options)
- [Gotchas](#gotchas)

## Install

Snap is what Certbot's own docs recommend, because it always carries the current release. Distro packages lag behind but update with the rest of the system. The plugin for your web server is a separate package either way.

[TABLE]

Without snap, a virtualenv keeps Certbot off the system Python:

```
sudo python3 -m venv /opt/certbot
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
```

Copy

A pip or virtualenv install schedules nothing, so add the renewal cron entry yourself. Snap and distro packages both bring their own timer.

## nginx

The nginx plugin is the usual route: it proves control of the domain, fetches the certificate, and edits the matching server block in one go. It needs an existing block whose server_name matches, which the [nginx config generator](https://sshworkbench.com/tools/nginx-config-generator) can produce.

[TABLE]

Confirm the result from outside with the [SSL checker](https://sshworkbench.com/tools/ssl-checker).

## Apache

Same idea with the Apache plugin. On Debian and Ubuntu the service is apache2; on RHEL and friends it is httpd.

| Command | What it does |
|----|----|
| sudo certbot --apache | Get and install, picking domains from your VirtualHosts |
| sudo certbot --apache -d example.com -d www.example.com | Get and install for the listed domains |
| sudo certbot certonly --apache -d example.com | Get the certificate only; leave Apache config untouched |
| sudo apachectl configtest | Check the config before reloading |
| sudo systemctl reload apache2 | Load the new certificate |

## certonly

certonly obtains or renews a certificate without touching any web server config; you point the server at the files yourself. Pick one authenticator per run.

| Command | What it does |
|----|----|
| sudo certbot certonly --nginx -d example.com | Prove control through the running nginx |
| sudo certbot certonly --apache -d example.com | Prove control through the running Apache |
| sudo certbot certonly --standalone -d example.com | Certbot runs its own temporary server on port 80 |
| sudo certbot certonly --webroot -w /var/www/html -d example.com | Drop challenge files into an existing site |
| --cert-name mysite | Name the certificate instead of using the first domain |

The files land in /etc/letsencrypt/live/\<name\>/ as fullchain.pem and privkey.pem. Inspect what you got with the [certificate decoder](https://sshworkbench.com/tools/certificate-decoder) or openssl x509 -text from the [OpenSSL cheat sheet](https://sshworkbench.com/cheatsheets/openssl).

## Standalone

Standalone binds its own listener on port 80, so it works on machines with no web server at all: mail servers, database hosts, brokers. Whatever already holds port 80 must stop first.

| Command | What it does |
|----|----|
| sudo certbot certonly --standalone -d example.com | Get a certificate with certbot's built-in server |
| sudo ss -tlnp \| grep :80 | See what is currently holding port 80 |
| --http-01-port 8888 | Listen locally on another port behind a proxy; Let's Encrypt still connects to 80 |

If a web server owns port 80, stop it around the run and restart it after:

```
sudo certbot certonly --standalone -d mail.example.com \
  --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx"
```

Copy

Certbot remembers the hooks and reuses them at renewal, so the stop-start happens automatically from then on.

## Webroot

Webroot never takes the site down: certbot writes the challenge into .well-known/acme-challenge/ under the directory you name, and Let's Encrypt fetches it over plain HTTP.

[TABLE]

One certificate for several sites, each with its own root:

```
sudo certbot certonly --webroot \
  -w /var/www/html -d example.com -d www.example.com \
  -w /var/www/blog -d blog.example.com
```

Copy

The path must be served over HTTP without a redirect to somewhere the challenge is not. A 404 on /.well-known/acme-challenge/... during the run means -w points at the wrong directory.

## DNS Challenge

The dns-01 challenge proves control with a TXT record, so it needs no open port at all, works behind a CDN, and is the only challenge that can issue wildcards.

| Command | What it does |
|----|----|
| --preferred-challenges dns | Ask for the DNS challenge |
| dig TXT \_acme-challenge.example.com | Check the record is visible before continuing |
| sudo snap set certbot trust-plugin-with-root=ok | Let snap-installed plugins run with certbot |
| sudo snap install certbot-dns-cloudflare | Install a DNS plugin (one exists per major provider) |

Manual, for a one-off certificate:

```
sudo certbot certonly --manual --preferred-challenges dns -d example.com
```

Copy

Certbot prints the TXT value, you add it at your DNS host, wait for it to propagate, and press Enter. A manual certificate cannot renew unattended unless you also supply --manual-auth-hook.

Automated, with a provider plugin and an API credentials file (chmod 600):

```
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d example.com
```

Copy

Slow DNS host? Add --dns-cloudflare-propagation-seconds 60 (each plugin has its own version of the flag).

Every plugin follows the same three-part pattern: a package, a --dns-\<provider\> flag, and a credentials file.

[TABLE]

Registrars with no official plugin, GoDaddy, Namecheap and Porkbun among them, have community plugins on PyPI, or you can delegate \_acme-challenge with a CNAME to a provider that does have one.

## Wildcard Certificates

Wildcards come only from the DNS challenge above.

```
sudo certbot certonly --manual --preferred-challenges dns \
  -d example.com -d "*.example.com"
```

Copy

- Quote
  \*.example.com
  so the shell does not try to expand it.
- Include the bare domain:
  \*.example.com
  does not cover
  example.com
  .
- A wildcard covers one level only:
  app.example.com
  yes,
  a.b.example.com
  no.
- For automatic renewal, use a DNS plugin instead of
  --manual
  .

## Renewal

Packaged installs (snap, apt, dnf) add a systemd timer or cron job that runs certbot renew twice a day. Each certificate renews once it is within 30 days of expiry, reusing the exact options it was created with, so you never repeat --nginx or -w.

| Command | What it does |
|----|----|
| sudo certbot renew | Renew everything that is close to expiry |
| sudo certbot renew --dry-run | Full rehearsal against the staging server, changes nothing |
| sudo certbot renew --cert-name example.com | Renew one certificate |
| sudo certbot renew --force-renewal | Renew now regardless of expiry; rate limits apply |
| systemctl list-timers \| grep certbot | Confirm the renewal timer is scheduled |
| cat /etc/letsencrypt/renewal/example.com.conf | See the stored renewal settings for one certificate |

The timer is a normal systemd unit, so the [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl) applies if it is missing or dead.

## Add and Remove Domains

There is no "add domain" subcommand. You reissue the certificate with the full list of names you want and pin --cert-name so it replaces the existing one instead of creating a second certificate under a new directory.

| Command | What it does |
|----|----|
| sudo certbot --nginx --cert-name example.com -d example.com -d www.example.com -d shop.example.com | Reissue with an extra name, same file paths |
| --expand | Skip the "expand this certificate?" prompt, for scripts |
| sudo certbot certonly --cert-name example.com -d example.com | Drop every other name by reissuing with a shorter list |
| --allow-subset-of-names | Issue with whatever names validate, instead of failing on one bad domain |
| sudo certbot delete --cert-name old.example.com | Remove a whole certificate and stop renewing it |

Get the current name list before you edit it, since leaving a domain out of the reissue removes it:

```
sudo certbot certificates --cert-name example.com
```

Copy

The live directory keeps its original name, so /etc/letsencrypt/live/example.com/ stays correct in nginx or Apache no matter which domains you add.

## List and Delete

[TABLE]

delete does not touch your web server config. Remove the ssl_certificate lines that point at the deleted files first, or nginx refuses to start on the next reload.

## Deploy Hooks

Nginx and Apache load certificate files at startup and never look again, so a renewed file on disk changes nothing until a reload. A deploy hook runs after each successful issue or renewal, which is exactly the moment for it.

[TABLE]

Add a hook to an existing certificate without reissuing it:

```
sudo certbot reconfigure --cert-name example.com \
  --deploy-hook "systemctl reload nginx"
```

Copy

## Files and Logs

Everything Certbot owns lives under /etc/letsencrypt/, and every run appends to one log file. That log carries the real ACME error text, which is usually far more specific than what the terminal printed.

[TABLE]

[TABLE]

Back up /etc/letsencrypt/ as a whole, with symlinks preserved (tar -czphf), or the restored copy points nowhere. See the [tar cheat sheet](https://sshworkbench.com/cheatsheets/tar).

## Windows

Certbot no longer ships a native Windows build; EFF stopped producing the Windows installer during the 2.x series, and the old beta .exe downloads are unsupported. Three options remain.

[TABLE]

IIS wants a .pfx, not the .pem pair, so convert with openssl pkcs12 -export -out cert.pfx -inkey privkey.pem -in fullchain.pem from the [OpenSSL cheat sheet](https://sshworkbench.com/cheatsheets/openssl).

## Account and Version

| Command | What it does |
|----|----|
| sudo certbot register -m [\[email protected\]](https://sshworkbench.com/cdn-cgi/l/email-protection) --agree-tos | Create a Let's Encrypt account (normally happens on first run) |
| sudo certbot show_account | Show the account this machine uses |
| sudo certbot update_account -m [\[email protected\]](https://sshworkbench.com/cdn-cgi/l/email-protection) | Change the contact email for expiry warnings |
| sudo certbot unregister | Deactivate the account |
| certbot --version | Print the installed version |
| certbot --help all | The full option reference |
| sudo snap refresh certbot | Update a snap install (apt and dnf installs update with the system) |

## Docker

The official image is certbot/certbot, and its entrypoint is certbot itself, so everything after the image name is a normal certbot command. Mount /etc/letsencrypt or the certificates die with the container.

```
docker run -it --rm -p 80:80 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone -d example.com
```

Copy

Renewal is the same image with renew; there is no timer inside a container, so schedule it yourself from host cron:

```
docker run --rm -p 80:80 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot renew
```

Copy

| Image | What it is |
|----|----|
| certbot/certbot | The base image |
| certbot/dns-cloudflare | Base image plus the Cloudflare DNS plugin (one image per provider) |

For webroot next to an nginx container, mount the same volume in both containers as the challenge directory. Docker basics are on the [Docker cheat sheet](https://sshworkbench.com/cheatsheets/docker).

## Command Line Options

[TABLE]

## Gotchas

- Let's Encrypt rate limits are real: five identical certificates per week. Test with
  --dry-run
  or
  --staging
  , and never put
  --force-renewal
  in cron.
- After a
  certonly
  renewal your server still serves the old certificate until it reloads. If the [SSL checker](https://sshworkbench.com/tools/ssl-checker) shows an expired certificate but
  certbot certificates
  shows a fresh one, the missing piece is a deploy hook.
- Everything in
  /etc/letsencrypt/live/
  is a symlink. Point your config there and never copy the files out; copies stop updating.
- The HTTP challenge needs port 80 reachable from the internet. A closed firewall gives "Timeout during connect"; open it with
  ufw allow 80/tcp
  ([UFW cheat sheet](https://sshworkbench.com/cheatsheets/ufw)) and confirm from outside with the [port checker](https://sshworkbench.com/tools/ssh-port-checker). Behind Cloudflare or another CDN, use the DNS challenge instead.
- Failed validations have their own limit, five per account, hostname and hour. Retrying a broken challenge in a loop earns "too many failed authorizations recently" and an hour of lockout, so read
  /var/log/letsencrypt/letsencrypt.log
  and fix the cause between attempts.
- certbot-auto
  and
  letsencrypt-auto
  are long dead. Install from your package manager or snap (
  sudo snap install --classic certbot
  ).

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## Certbot FAQ

### Does Certbot renew certificates automatically?

Yes, if Certbot came from snap, apt, or dnf. Those packages install a systemd timer (or a cron job on older systems) that runs certbot renew twice a day. Each run only acts on certificates within 30 days of expiry, which is why most runs print 'not yet due for renewal' and exit without doing anything. Confirm the schedule exists with systemctl list-timers \| grep certbot. A pip or from-source install schedules nothing, so you have to add the cron entry yourself. Renewal reuses the exact options stored in /etc/letsencrypt/renewal/example.com.conf, so you never repeat --nginx or -w, but it does not reload your web server unless a deploy hook tells it to.

### Does Certbot need port 80?

Only for the HTTP challenge, which is what --nginx, --apache, --standalone, and --webroot all use. Let's Encrypt connects to port 80 on your public IP to fetch the challenge file, so that port has to be reachable even on a site that serves nothing but HTTPS. A redirect from 80 to 443 is fine, the validation server follows it. --http-01-port changes only the local listener behind a proxy, not the port Let's Encrypt dials, so it is not a way around a closed firewall. When port 80 genuinely cannot be opened, behind a CDN, on a private network, or on a host where another service owns it, use the dns-01 challenge, which needs no inbound connection at all.

### How do I add a domain to an existing Certbot certificate?

Re-run certbot with the complete domain list and pin the certificate name: sudo certbot --nginx --cert-name example.com -d example.com -d [www.example.com](http://www.example.com) -d shop.example.com. Certbot sees the name already exists, issues a replacement covering the new set, and keeps the same /etc/letsencrypt/live/example.com/ paths, so nothing in your config changes. Add --expand to skip the confirmation prompt in a script. Removing a domain works the same way: run it again with the shorter -d list and Certbot reissues without the dropped names. Each reissue counts against the limit of 50 certificates per registered domain per week, so change the list once rather than adding subdomains one at a time.

### How do I run a command after Certbot renews a certificate?

Attach a deploy hook: sudo certbot certonly --webroot -w /var/www/html -d example.com --deploy-hook 'systemctl reload nginx'. Certbot saves the hook in the certificate's renewal config and runs it after every successful renewal of that certificate, which is exactly when nginx or Apache needs a reload to pick up the new file. To run something for every certificate on the machine, drop an executable script into /etc/letsencrypt/renewal-hooks/deploy/ instead. Inside a hook, \$RENEWED_LINEAGE holds the live directory path. Note that renew --dry-run skips deploy hooks unless you add --run-deploy-hooks.

### Where does Certbot store certificates?

Under /etc/letsencrypt/live/\<cert-name\>/, where fullchain.pem and privkey.pem are the two files a web server needs. They are symlinks into /etc/letsencrypt/archive/, and renewal repoints them at the newest version, so reference the live paths in your config and never copy the files somewhere else or they will silently go stale. Renewal settings live in /etc/letsencrypt/renewal/\<cert-name\>.conf, global defaults in /etc/letsencrypt/cli.ini, and the log of every run in /var/log/letsencrypt/letsencrypt.log. sudo certbot certificates prints every certificate with its domains, expiry date, and paths.

---
Källa: https://sshworkbench.com/cheatsheets/certbot
