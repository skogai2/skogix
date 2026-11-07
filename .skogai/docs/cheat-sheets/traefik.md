# Traefik Cheat Sheet

Traefik is a reverse proxy that configures itself from Docker labels, Kubernetes CRDs, or config files, so there is little to type and a lot to look up. This sheet covers router rule syntax, the labels for docker compose, static vs dynamic config, middlewares, Let's Encrypt, IngressRoute, TCP and UDP routing, logs, and the few CLI commands Traefik has.

## Router Rules

Rules live on routers, in a label or a dynamic config file. Values go in backticks, never quotes. Combine matchers with && (and), \|\| (or), ! (not), and parentheses.

| Rule | Matches |
|----|----|
| Host(\`example.com\`) | Requests for exactly that hostname |
| Host(\`a.com\`) \|\| Host(\`b.com\`) | Either hostname |
| Host(\`example.com\`) && PathPrefix(\`/api\`) | Both conditions at once |
| PathPrefix(\`/api\`) | Any path starting with /api |
| Path(\`/health\`) | That exact path only |
| HostRegexp(\`^.+\\example\\com$\`) | Hostnames by Go regex (v3 syntax) |
| PathRegexp(\`^/items/[0-9]+$\`) | Paths by Go regex |
| Header(\`X-Env\`, \`staging\`) | Exact header match |
| HeaderRegexp(\`Accept\`, \`json\`) | Header value by regex |
| Query(\`token\`, \`secret\`) | Query parameter key and value |
| Method(\`POST\`) | HTTP method |
| ClientIP(\`10.0.0.0/8\`) | Source IP or CIDR range |
| !PathPrefix(\`/admin\`) | Everything except /admin |

When two routers both match, the longer rule string wins. Override with traefik.http.routers.<name>.priority=10 (higher wins).

v2 differences: HostRegexp used {name:regex} placeholders instead of plain regex, the matchers were Headers() and HeadersRegexp() (plural), and Host()/PathPrefix() accepted comma-separated values. In v3 chain them with \|\|.

## Docker Labels

Labels on the app container, not on Traefik. The [Traefik label generator](https://sshworkbench.com/tools/traefik-label-generator) builds these interactively.

| Docker Label | Example Value | Purpose |
|---|---|---|
| `traefik.enable` | `true` | Expose container to Traefik |
| `traefik.http.routers.app.rule` | `Host(\`app.example.com\`)` | Routing rule for incoming HTTP requests |
| `traefik.http.routers.app.entrypoints` | `websecure` | Entrypoint to attach router to (port 443) |
| `traefik.http.routers.app.tls.certresolver` | `myresolver` | ACME resolver to issue SSL certificate |
| `traefik.http.services.app.loadbalancer.server.port` | `8080` | Internal container port to route traffic to |

A working docker compose setup:

```bash
services:
  traefik:
    image: traefik:v3
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

  app:
    image: myapp:latest
    labels:
      - traefik.enable=true
      - traefik.http.routers.app.rule=Host(`app.example.com`)
      - traefik.http.routers.app.entrypoints=websecure
      - traefik.http.routers.app.tls.certresolver=letsencrypt
      - traefik.http.services.app.loadbalancer.server.port=3000
```

The router name (app here) is arbitrary; it just has to be the same across that container's labels.

## Static vs Dynamic Config

Static config is read once at startup: entrypoints, providers, certificate resolvers, logging. It comes from traefik.yml (looked up in /etc/traefik/), CLI flags, or TRAEFIK\_* environment variables; pick one style. Dynamic config is routers, services, and middlewares; it comes from labels or watched files and applies without a restart.

```bash
# /etc/traefik/traefik.yml (static)
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false
  file:
    directory: /etc/traefik/dynamic
    watch: true

api:
  dashboard: true
```

A dynamic file routes to things that are not containers, like a service on the host:

```
# /etc/traefik/dynamic/api.yml
http:
  routers:
    api:
      rule: Host(`api.example.com`)
      entryPoints: [websecure]
      service: api
      tls:
        certResolver: letsencrypt
  services:
    api:
      loadBalancer:
        servers:
          - url: http://192.168.1.10:3000
```

Changing a dynamic file or a label applies immediately. Changing traefik.yml needs a container restart.

## EntryPoints

EntryPoints are the ports Traefik listens on. The names web and websecure are convention, not built in.

| Config | What it does |
|----|----|
| entryPoints.web.address: ":80" | Listen on port 80 |
| entryPoints.websecure.address: ":443" | Listen on port 443 |
| entryPoints.udp-dns.address: ":53/udp" | UDP entrypoint |
| --entrypoints.web.address=:80 | Same, as a CLI flag |
| --entrypoints.websecure.asdefault=true | Make this the default for routers that name none (v3) |
| --entrypoints.websecure.http3=true | Serve HTTP/3 on this entrypoint |
| --entrypoints.websecure.forwardedheaders.trustedips=173.245.48.0/20 | Trust X-Forwarded-* only from these IPs |
| --entrypoints.web.proxyprotocol.trustedips=10.0.0.0/8 | Accept the PROXY protocol from these IPs |
| --entrypoints.websecure.transport.respondingtimeouts.readtimeout=60s | Per-entrypoint timeouts |

Behind Cloudflare or another proxy, the client IP arrives in X-Forwarded-For and Traefik ignores it until that proxy's ranges are in forwardedheaders.trustedips. Without that, ClientIP rules, ipallowlist, and rate limits all see the proxy instead of the visitor.

Redirect all HTTP to HTTPS at the entrypoint, so no per-container labels are needed:

```
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
```

## Middlewares

Define a middleware once, attach it to any router with traefik.http.routers.<router>.middlewares=<name>. Reference one from another provider with a suffix: auth@file, auth@docker, auth@kubernetescrd.

| Middleware Type | Example Configuration | Purpose |
|---|---|---|
| Basic Auth | `traefik.http.middlewares.auth.basicauth.users=user:hash` | HTTP basic authentication gate |
| Redirect Scheme | `traefik.http.middlewares.https-redirect.redirectscheme.scheme=https` | HTTP to HTTPS redirection |
| Strip Prefix | `traefik.http.middlewares.strip.stripprefix.prefixes=/api` | Remove prefix before passing to backend |
| Rate Limit | `traefik.http.middlewares.limit.ratelimit.average=100` | Rate limiting per IP address |

In a compose file every $ in a basicauth hash or a regex replacement must be doubled to $$ or compose eats it as a variable.

## Let's Encrypt

Certificate resolvers are static config. Traefik requests and renews certificates on its own and stores them in acme.json.

```bash
certificatesResolvers:
  letsencrypt:
    acme:
      email: git@github.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

| Configuration Key | Example Value | Description |
|---|---|---|
| `certificatesResolvers.myresolver.acme.email` | `admin@example.com` | Registration email for Let's Encrypt |
| `certificatesResolvers.myresolver.acme.storage` | `/etc/traefik/acme.json` | JSON file storing generated TLS certificates |
| `certificatesResolvers.myresolver.acme.tlschallenge` | `true` | Use TLS-ALPN-01 ACME verification challenge |
| `certificatesResolvers.myresolver.acme.httpchallenge` | `true` | Use HTTP-01 ACME verification challenge |

A wildcard from Cloudflare needs the DNS challenge in static config and an API token in the environment:

```bash
certificatesResolvers:
  letsencrypt:
    acme:
      email: git@github.com
      storage: /letsencrypt/acme.json
      dnsChallenge:
        provider: cloudflare
        resolvers:
          - "1.1.1.1:53"
```

```
# same compose service
environment:
  - CF_DNS_API_TOKEN=...   # needs Zone:Read and DNS:Edit on that zone
labels:
  - traefik.http.routers.app.tls.certresolver=letsencrypt
  - traefik.http.routers.app.tls.domains[0].main=example.com
  - traefik.http.routers.app.tls.domains[0].sans=*.example.com
```

Let's Encrypt limits issuance to 5 duplicate certificates a week, so keep acme.json in a volume and use the staging CA while testing. "Could not find zone for domain" means the token cannot read that zone, or the apex is delegated to different nameservers than the one you asked for.

## TCP & UDP

Non-HTTP services get their own router type on their own entrypoint. TCP rules match on SNI, not on paths or headers.

| Label | What it does |
|----|----|
| --entrypoints.postgres.address=:5432 | Add a TCP entrypoint (static config) |
| traefik.tcp.routers.db.rule=HostSNI(\`*\`) | Match anything on that entrypoint (the only rule for plain TCP) |
| traefik.tcp.routers.db.entrypoints=postgres | Which entrypoint the router listens on |
| traefik.tcp.services.db.loadbalancer.server.port=5432 | Backend port |
| traefik.tcp.routers.web.rule=HostSNI(\`db.example.com\`) | Route by SNI, only possible when the client sends TLS |
| traefik.tcp.routers.web.tls.passthrough=true | Hand the TLS session to the backend untouched |
| traefik.tcp.routers.db.rule=ClientIP(\`10.0.0.0/8\`) | Match by source IP (v3) |
| traefik.udp.routers.dns.entrypoints=udp-dns | UDP router; UDP has no matchers, so no rule |
| traefik.udp.services.dns.loadbalancer.server.port=53 | UDP backend port |

Protocols without SNI (SSH, Postgres, plain MQTT) can only use HostSNI(\`*\`), and one entrypoint holds one such router. Give each backend its own port. With tls.passthrough=true Traefik never decrypts, so no middleware or certificate resolver applies to that router.

## Kubernetes

Traefik ships as an ingress controller. It reads plain Ingress objects, its own IngressRoute CRDs, and the Gateway API. k3s installs it by default.

| Command | What it does |
|----|----|
| helm repo add traefik https://traefik.github.io/charts | Add the official chart repo |
| helm install traefik traefik/traefik -n traefik --create-namespace | Install the controller |
| helm show values traefik/traefik | Every value the chart accepts |
| kubectl get ingressroute -A | List IngressRoute objects |
| kubectl get middleware -A | List Middleware objects |
| kubectl describe ingressroute app | Why a route is not live |
| kubectl logs -n traefik deploy/traefik -f | Follow the controller log |
| kubectl get svc -n traefik traefik | The external IP requests should point at |
| curl -sfL https://get.k3s.io \| sh -s - --disable=traefik | Skip the Traefik that k3s bundles |
| kubectl -n kube-system edit helmchartconfig traefik | Change k3s's bundled Traefik values |

```
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: app
spec:
  entryPoints: [websecure]
  routes:
    - match: Host(`app.example.com`) && PathPrefix(`/`)
      kind: Rule
      middlewares:
        - name: strip
      services:
        - name: app
          port: 3000
  tls:
    certResolver: letsencrypt
```

Annotations do the same job on a plain Ingress:

```
metadata:
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
    traefik.ingress.kubernetes.io/router.middlewares: default-strip@kubernetescrd
```

The CRD API group is traefik.io/v1alpha1 in v3 and traefik.containo.us/v1alpha1 in v2; applying v2 manifests to a v3 install fails with "no matches for kind". A middleware in another namespace needs that namespace in the reference and providers.kubernetesCRD.allowCrossNamespace=true.

## Plugins

Plugins are declared in static config, downloaded from plugins.traefik.io at startup, and run as interpreted Go, so no rebuild is involved. Once declared, a plugin is used like any other middleware.

```
# static config
experimental:
  plugins:
    bouncer:
      moduleName: github.com/maxlerebourg/crowdsec-bouncer-traefik-plugin
      version: v1.4.5
```

| Directive | Context | Purpose |
|---|---|---|
| `experimental.plugins` | Static config | Declare plugin name, module path, and pinned version |
| `middlewares.myplugin` | Dynamic config | Instantiate declared plugin with configuration options |
| `traefik.http.routers.app.middlewares` | Router label | Attach plugin middleware to target router |

Plugins load only at startup, so adding one means restarting Traefik, not just editing a label.

## CLI & Flags

The binary has two subcommands; everything else is flags. Every flag maps to a static config key and to a TRAEFIK\_* environment variable.

| Flag | Purpose |
|---|---|
| `--api.dashboard=true` | Enable web UI dashboard |
| `--entrypoints.web.address=:80` | Bind HTTP entrypoint on port 80 |
| `--entrypoints.websecure.address=:443` | Bind HTTPS entrypoint on port 443 |
| `--providers.docker=true` | Enable Docker container discovery provider |
| `--providers.docker.exposedbydefault=false` | Require explicit `traefik.enable=true` label |

## Logs & Metrics

Two separate logs. The Traefik log is about Traefik; the access log is about requests. Both go to stdout unless given a path.

| Directive | Value / Purpose |
|---|---|
| `log.level` | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `accessLog` | `true` (outputs structured JSON or Common Log Format) |
| `metrics.prometheus` | Exposes `/metrics` endpoint for Prometheus scraping |

Access logs written to a file inside the container disappear on recreate unless the path is on a volume. docker compose logs traefik only shows what went to stdout.

## Healthcheck

Two different things share the name: checking Traefik itself, and Traefik checking your backends.

| Command / Flag | Purpose |
|---|---|
| `--ping=true` | Enable Traefik internal ping endpoint |
| `traefik healthcheck` | CLI command used in Docker `HEALTHCHECK` |

When a backend fails its check, Traefik takes it out of rotation until it passes again; with one replica that means 404s, so backend healthchecks matter most with multiple replicas.

## Dashboard & API

The dashboard shows every router, service, and middleware, and flags configuration errors that logs bury.

| Setting | Description |
|---|---|
| `--api.insecure=true` | Exposes dashboard directly on port 8080 (dev only) |
| Secure Router Setup | Protect dashboard router with TLS and Basic Auth in production |

Never ship api.insecure=true on a public host; the dashboard reveals every internal hostname and middleware secret name.

## Running & Debugging

Traefik runs as a container, so day-to-day operation is docker compose. The [docker compose cheat sheet](https://sshworkbench.com/cheatsheets/docker-compose) covers the rest.

| Action | Command / Method |
|---|---|
| View Traefik logs | `docker compose logs -f traefik` |
| Validate routing rules | Check Dashboard HTTP Routers list |
| Inspect ACME certificate state | Verify file permissions `chmod 600 acme.json` |

More container commands are on the [docker cheat sheet](https://sshworkbench.com/cheatsheets/docker).

## v2 to v3

Most setups move over untouched. These are the renames that stop a container from starting or silently drop a route.

| Feature | Traefik v2 | Traefik v3 |
|---|---|---|
| WebAssembly (Wasm) | Experimental | First-class native support via Coraza |
| OpenTelemetry | Basic tracing | Full OpenTelemetry tracing and metrics |
| HTTP/3 | Experimental | Stable and enabled by default |

Run the old config against v3 with --log.level=DEBUG in a throwaway container first; unknown keys are reported by name at startup.

## Gotchas

- Rules use backticks around values. Quotes inside Host("...") fail silently in some setups and loudly in others; backticks always work.
- Set exposedByDefault: false. Without it every container on the socket gets routed, including ones you never meant to publish.
- A 404 from Traefik usually means no router matched (wrong Host, wrong entrypoint); a "Bad Gateway" means the router matched but Traefik cannot reach the container, almost always a network mismatch. Put both containers on one network or set traefik.docker.network.
- When a container exposes several ports, Traefik picks one arbitrarily. Pin it with loadbalancer.server.port.
- $ doubling in compose applies to basicauth hashes only in compose files, not in dynamic file config. The same hash needs $$ in a label and $ in a YAML file.
- If HTTPS works but keeps serving the "TRAEFIK DEFAULT CERT", the resolver failed; check the logs for acme errors and confirm port 80 (HTTP challenge) reaches Traefik.
- "Too many redirects" behind Cloudflare means Cloudflare SSL is set to Flexible while Traefik also redirects to HTTPS. Set Cloudflare to Full (strict).
- Upgrading v2 to v3 mostly just works, but HostRegexp placeholder rules, Headers() matchers, and ipWhiteList middlewares need renaming first.

## Traefik FAQ

### How does Traefik work?

Traefik watches a provider (the Docker socket, a Kubernetes API, or a directory of config files) and builds its routing table from what it finds, so you configure the app, not the proxy. A request arrives on an entrypoint (a port), a router matches it with a rule like Host(`app.example.com`), optional middlewares transform it, and a service forwards it to the container or upstream URL. Start a container with the right labels and the route appears; stop it and the route is gone. No reload step exists because dynamic config is re-read continuously.

### Where does Traefik store certificates, config, and logs?

Certificates go in the acme.json file named by the storage key of the resolver, usually /letsencrypt/acme.json. That single file holds every certificate plus the ACME account key, so it belongs on a volume; without one, every restart starts from scratch. Static config is read from /etc/traefik/traefik.yml (also .yaml or .toml) unless --configfile points somewhere else, and dynamic files come from whatever providers.file.directory names. Logs and access logs go to stdout by default, which means docker compose logs -f traefik is where they are; set log.filePath and accesslog.filepath to write real files instead.

### Does Traefik auto renew certificates?

Yes. Traefik reads acme.json at startup and rechecks periodically, renewing anything inside 30 days of expiry with no cron job and no reload. Renewal repeats the original challenge, so port 80 has to stay reachable for an HTTP challenge and the DNS API token has to stay valid for a DNS challenge. When renewal appears to fail, the cause is almost always that acme.json is not on a volume: each restart re-issues, and Let's Encrypt caps duplicate certificates at 5 a week. To force a renewal, stop Traefik, delete that domain's entry from acme.json, and start it again.

### Can Traefik proxy SSH?

Yes, with a TCP router. SSH sends no SNI, so the rule has to be HostSNI(`*`), and an entrypoint can carry only one such router. Add --entrypoints.ssh.address=:2222 to the static config, then label the target container traefik.tcp.routers.ssh.rule=HostSNI(`*`), traefik.tcp.routers.ssh.entrypoints=ssh, and traefik.tcp.services.ssh.loadbalancer.server.port=22. Several SSH backends cannot share one port, because the protocol gives Traefik nothing to match on. Give each one its own entrypoint and port, or put a single jump host behind Traefik and route from there.

### How do I access the Traefik dashboard?

Two ways, with different failure modes. For local work set --api.insecure=true, publish port 8080, and open [http://localhost:8080/dashboard/](http://localhost:8080/dashboard/) including the trailing slash; without the slash you get a 404. In production leave insecure off and route it like any other app: a router with rule Host(`traefik.example.com`), traefik.http.routers.dash.service=api@internal, and a basicauth middleware. If the page loads but every panel reads "failed to fetch data", the router is serving /dashboard but not /api. Pointing the router at api@internal covers both paths.

---
Source: https://sshworkbench.com/cheatsheets/traefik
