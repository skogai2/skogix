# Docker Compose Commands

Docker Compose runs a multi-container app from one compose.yaml file. This sheet covers both halves of the job: the docker compose commands you type, and the YAML keys you write, from ports and volumes to networks, environment variables and healthchecks.

Last updated September 11, 2026

On this page

- [docker compose vs docker-compose](#docker-compose-vs-docker-compose)
- [Start and Stop](#start-and-stop)
- [Status and Logs](#status-and-logs)
- [Exec and Run](#exec-and-run)
- [Build and Pull](#build-and-pull)
- [Files, Projects and Profiles](#files-projects-and-profiles)
- [Environment Variables](#environment-variables)
- [Validate and Clean Up](#validate-and-clean-up)
- [compose.yaml Keys](#composeyaml-keys)
- [Volumes](#volumes)
- [Networks](#networks)
- [Restart and Autostart](#restart-and-autostart)
- [Limits, Users and Devices](#limits-users-and-devices)
- [Example compose.yaml](#example-composeyaml)
- [Healthcheck and depends_on](#healthcheck-and-dependson)
- [command vs entrypoint](#command-vs-entrypoint)
- [Install and Version](#install-and-version)
- [Gotchas](#gotchas)

Compose v2 is a Docker CLI plugin, so the command is docker compose with a space. The hyphenated docker-compose was v1, written in Python, and has been retired. Every command below is v2.

## docker compose vs docker-compose

Most tutorials written before 2023 use the hyphen. Translating them is usually one keystroke, but a few things moved.

[TABLE]

Two error messages come out of this split, and they mean opposite things. The third case is the one that confuses people most, because the old command works:

[TABLE]

If scripts on the machine still call the old name, an alias covers interactive shells:

```
alias docker-compose='docker compose'
```

Copy

Aliases are not read by shell scripts, so anything running under sh script.sh or cron needs the command edited, or a two-line wrapper in /usr/local/bin/docker-compose.

## Start and Stop

Run these from the directory that holds compose.yaml, or point at it with -f.

[TABLE]

up -d is also how you apply changes: it compares the file against the running containers and recreates only the ones whose configuration changed. restart does not do that.

## Status and Logs

| Command | What it does |
|----|----|
| docker compose ps | Containers for this project, with state and ports |
| docker compose ps -a | Include stopped ones |
| docker compose ps --services | Just the service names |
| docker compose ls | Every Compose project running on this host |
| docker compose logs | Logs from every service |
| docker compose logs -f | Follow |
| docker compose logs -f web | Follow one service |
| docker compose logs -f --tail 100 web | Last 100 lines, then follow |
| docker compose logs --since 10m | Only the last ten minutes |
| docker compose logs -t web | With timestamps |
| docker compose top | Processes in every container |
| docker compose stats | Live CPU and memory per container |
| docker compose events | Stream container events for the project |
| docker compose images | Which image and tag each service runs |
| docker compose port web 80 | Which host port maps to container port 80 |

## Exec and Run

exec runs inside an existing container. run starts a new one from the service definition, which is the right tool for one-off jobs like migrations.

[TABLE]

Without --rm, every run leaves a stopped container behind. docker compose ps -a shows them and docker compose rm clears them.

## Build and Pull

[TABLE]

Update a running stack to newer images:

```
docker compose pull
docker compose up -d
```

Copy

up -d recreates only the containers whose image changed. For services you build yourself, docker compose up -d --build does the same thing in one step. The [Dockerfile generator](https://sshworkbench.com/tools/dockerfile-generator) is a quick way to get the build: side started.

watch needs a develop: block on the service, and it replaces the usual edit, rebuild, restart loop in development:

```
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: package.json
```

Copy

sync copies changed files into the running container, rebuild rebuilds the image and recreates the container, and sync+restart copies then restarts the process.

## Files, Projects and Profiles

[TABLE]

compose.override.yaml is loaded automatically alongside compose.yaml when you do not pass -f, which is the usual way to keep dev-only ports and bind mounts out of the main file. The same flags can live in the environment: COMPOSE_FILE=compose.yaml:compose.prod.yaml, COMPOSE_PROFILES=debug, COMPOSE_PROJECT_NAME=myproject.

Inside the file, include: pulls in another compose file as if it were part of this one, and x- keys hold YAML anchors you can reuse across services. Compose ignores any top-level key starting with x-, which is what makes them safe to define:

```
include:
  - ./monitoring/compose.yaml

x-logging: &default-logging
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"

services:
  web:
    image: nginx
    logging: *default-logging
  api:
    image: myapi
    logging: *default-logging
```

Copy

extends: on a service does the same for one service at a time, pulling its definition from another file and letting you override parts of it.

## Environment Variables

Two different things share the name. \${VAR} in the file is substituted by Compose before anything starts, reading the shell environment and the project .env file. environment: and env_file: put variables inside the container. A variable in .env does not reach the container unless you pass it through.

[TABLE]

When the same variable is set in more than one place, the order from strongest to weakest is run -e, then environment:, then env_file:, then ENV in the image's Dockerfile. warning: The "X" variable is not set. Defaulting to a blank string. means substitution found nothing, and docker compose config is the fastest way to see what it did use.

For passwords, secrets: keeps the value out of the environment and out of docker inspect. The file is mounted at /run/secrets/\<name\>, and most official images take a \_FILE variant that reads it:

```
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./db_password.txt
```

Copy

## Validate and Clean Up

| Command | What it does |
|----|----|
| docker compose config | Validate the file and print the fully resolved version |
| docker compose config -q | Validate only, no output; non-zero exit on error |
| docker compose config --services | List service names |
| docker compose config --volumes | List volume names |
| docker compose config --profiles | List profiles |
| docker compose rm | Remove stopped service containers |
| docker compose rm -f -s -v | Stop, remove, and drop anonymous volumes without asking |
| docker compose down --remove-orphans | Remove containers for services you deleted from the file |
| docker compose version | Which Compose you have |

Found orphan containers on up is a warning, not an error: a service was renamed or removed from the file and its old container is still around. --remove-orphans on up or down clears it.

## compose.yaml Keys

The keys you actually use, per service. Indentation is two spaces and matters.

[TABLE]

Top-level volumes: and networks: declare the names the services refer to:

```
volumes:
  data:
networks:
  backend:
```

Copy

Services on the same project network reach each other by service name (db:5432), which is why DB_HOST=db works. Compose creates a default network per project, so you only need networks: when you want to split services up.

## Volumes

[TABLE]

Named volumes have to be declared at the top level before a service can use one:

```
volumes:
  data:
  cache:
    external: true
```

Copy

external: true means Compose will use a volume you created yourself with docker volume create and will not remove it, even on down -v. Everything else gets the project name as a prefix, so data in project myapp is really myapp_data and lives under /var/lib/docker/volumes/myapp_data/\_data on a Linux host. docker volume ls lists them, docker volume inspect myapp_data gives the path, and docker compose config --volumes prints the names the file declares.

## Networks

Compose puts every service on a network called \<project\>\_default and registers each service name in its DNS, so db resolves from any other container in the project. Nothing else is needed for containers to talk to each other.

[TABLE]

To join a network created outside the project, for example one shared with a reverse proxy, declare it as external:

```
services:
  web:
    networks:
      - proxy
      - default

networks:
  proxy:
    external: true
```

Copy

could not resolve host or a connection refused between two containers is almost always one of three things: the services are not on a shared network, you used the published host port instead of the container port (db:5432, not db:15432), or you used localhost, which inside a container means that container. docker compose exec web getent hosts db settles it in one line. This is how [Traefik](https://sshworkbench.com/cheatsheets/traefik) and [Caddy](https://sshworkbench.com/cheatsheets/caddy) reach app containers: the proxy joins the same network and talks to the service name.

## Restart and Autostart

[TABLE]

For a stack that should come back after a reboot, restart: unless-stopped on every service plus sudo systemctl enable docker is enough. When the stack needs a defined boot order, a mounted disk, or a wait for the network, a unit file is better:

```
[Unit]
Description=myapp compose stack
Requires=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/srv/myapp
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
```

Copy

systemctl enable --now myapp then owns the stack. The [systemd unit generator](https://sshworkbench.com/tools/systemd-unit-generator) writes files like this, and the [systemctl commands](https://sshworkbench.com/cheatsheets/systemctl) sheet covers the rest. A container stuck in a restart loop is a different problem; see [Docker container keeps restarting](https://sshworkbench.com/fix/docker-container-keeps-restarting).

## Limits, Users and Devices

[TABLE]

deploy.resources is honoured by plain docker compose, not only by Swarm. GPUs go under reservations:

```
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

Copy

## Example compose.yaml

A web app built from the local Dockerfile, a Postgres database with a healthcheck, and a named volume for its data:

```
services:
  web:
    build: .
    image: myapp:latest
    ports:
      - "8080:3000"
    env_file: .env
    environment:
      DB_HOST: db
      NODE_ENV: production
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16
    volumes:
      - data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

volumes:
  data:
```

Copy

\${DB_PASSWORD:-changeme} reads DB_PASSWORD from the shell or the project .env file and falls back to changeme. The [Docker Compose generator](https://sshworkbench.com/tools/docker-compose-generator) builds files like this for common stacks.

## Healthcheck and depends_on

depends_on alone only orders startup: the db container starts first, but Postgres may still be initialising when web connects. A healthcheck plus condition: service_healthy makes Compose wait.

[TABLE]

The check runs inside the container, so curl or pg_isready has to exist in that image. Alpine images often lack curl; wget -qO- http://localhost:3000/health usually works instead. docker compose ps shows (healthy) or (unhealthy) next to the state, and docker inspect -f '{{json .State.Health}}' container shows the last few results.

## command vs entrypoint

[TABLE]

The string form (command: npm start) is split on spaces by Compose without a shell, so quotes inside it are kept literally and && is passed as an argument. When in doubt, use the list form and name sh -c explicitly. A multi-line script can go under a folded block scalar:

```
    command: >
      sh -c "npm run migrate &&
             npm run seed &&
             npm start"
```

Copy

## Install and Version

Compose v2 is a plugin, so it installs next to the Docker CLI rather than on its own.

[TABLE]

The distribution package called docker-compose is v1 on older Debian and Ubuntu releases, which is why the plugin package has a different name and comes from Docker's repository, not the distribution's. To install by hand:

```
mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
docker compose version
```

Copy

Use /usr/local/lib/docker/cli-plugins/ instead of ~/.docker/cli-plugins/ to install it for every user. If every command needs sudo, add yourself to the docker group with sudo usermod -aG docker \$USER and log out and back in; see [Cannot connect to the Docker daemon](https://sshworkbench.com/fix/docker-cannot-connect-to-docker-daemon) when it still fails.

## Gotchas

- docker compose restart
  does not read the file again. After editing
  compose.yaml
  , run
  docker compose up -d
  ; it recreates only what changed.
- stop
  and
  down
  are not the same.
  stop
  keeps the containers so
  start
  resumes them with their writable layer intact;
  down
  deletes them and the project network, and
  up
  builds new ones. Named volumes outlive both.
- down -v
  deletes every named volume declared in the file, including the database.
  down
  alone keeps them.
- the attribute "version" is obsolete
  is v2 telling you to delete the
  version: "3.8"
  line at the top of the file. It has no effect and never did in v2.
- additional property X is not allowed
  is a schema error: a misspelled key, or a service key written at the top level (or the other way round).
  docker compose config -q
  points at the line.
- depends_on
  without a
  condition
  only orders container starts. Add a healthcheck and
  condition: service_healthy
  when the app crashes on boot because the database is not ready.
- Ports in YAML must be quoted (
  "8080:80"
  );
  22:22
  unquoted is parsed as a base-60 number by some YAML parsers and becomes garbage.
- .env
  in the project directory feeds
  \${VAR}
  substitution in the file.
  env_file:
  feeds the container. They are different files with different jobs, and a variable in
  .env
  does not reach the container unless you also pass it through
  environment:
  or
  env_file:
  .
- Services started with
  --profile
  need the same
  --profile
  on
  down
  , or their containers are left running.
- Error response from daemon: ... port is already allocated
  on
  up
  means another container, or a process on the host, holds that port.
  docker ps
  and
  ss -tlnp
  find it; see [Error response from daemon](https://sshworkbench.com/fix/docker-error-response-from-daemon) for the other variants.
- Bare
  docker
  commands work on Compose containers too:
  docker logs myproject-web-1
  ,
  docker exec -it myproject-web-1 sh
  . The [docker commands](https://sshworkbench.com/cheatsheets/docker) sheet covers them.

### Manage Docker without the CLI gymnastics

SSH Workbench gives you a visual layer over Docker and Podman: start, stop, inspect, view logs without memorising flags.

[Try free for 7 days](https://sshworkbench.com/#install)

## Docker Compose FAQ

### What is the difference between docker-compose and docker compose?

The hyphen is v1 and the space is v2. v1 was a separate Python program; v2 is written in Go and ships as a plugin to the docker CLI, which is why it is a subcommand now. v1 reached end of support in 2023 and was dropped from Docker Desktop. The catch is that docker-compose often still works, because Docker installs a small wrapper under the old name that forwards to v2: run docker-compose version and a 2.x answer means you are already on v2 through the wrapper. The change that actually breaks things is naming. v1 called containers myproject_web_1 and v2 calls them myproject-web-1, so log greps, monitoring rules and scripts that match container names need updating. Networks and volumes kept the underscore form, so myproject_default and myproject_data are unchanged.

### Does docker compose down remove volumes?

No. down removes the containers and the project network and leaves every named volume alone, which is why a database survives a down and up. down -v is the one that deletes them, along with any anonymous volumes those containers had, and there is no undo. A volume declared external: true is skipped even by -v, since Compose did not create it. Bind mounts are just host directories, so no form of down touches them. Volumes from a project you renamed or deleted stay on disk under their old myproject_name and only docker volume ls will show you they are still there.

### Does docker compose up rebuild images?

No. up builds an image only when none exists under that name yet, so after the first run it keeps using the image it already has and your Dockerfile edits appear to do nothing. up -d --build rebuilds, and build --no-cache ignores the layer cache when a step like apt-get update has gone stale. Pulling works the same way: up fetches a missing image but never checks whether a tag has moved, so :latest stays on whatever you downloaded first until you run docker compose pull, or up -d --pull always. docker compose images prints the image ID behind each running service, which is the quickest way to tell whether a rebuild actually took.

### Can docker compose be used in production?

Yes, on a single host, and plenty of small production stacks run exactly this way. What you give up is multi-host scheduling and rolling updates: up -d stops the old container before it starts the new one, so there is a short gap on every deploy. A reverse proxy in front absorbs that, which is why Traefik and Caddy are both configured from the same compose file. Pin image tags rather than latest so a pull cannot change the version under you, keep passwords in secrets or an env file that is not in git, set restart: unless-stopped, and start the stack from a systemd unit so a reboot brings it back.

### Where is the docker compose file?

Compose looks in the current directory for compose.yaml, then compose.yml, then docker-compose.yaml, then docker-compose.yml, and if it finds none it walks up the parent directories until it hits the filesystem root. no configuration file provided: not found means that search came up empty, almost always because of the directory you are standing in. compose.override.yaml next to the file is merged in automatically. For a stack someone else started, docker compose ls prints the config file path of every running project, and docker inspect -f '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' container-name gets it from a single container.

---
Källa: https://sshworkbench.com/cheatsheets/docker-compose
