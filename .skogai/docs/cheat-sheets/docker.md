# Docker Commands

Docker runs applications in containers built from images. This sheet is the docker commands list you reach for day to day: starting and stopping containers, getting a shell inside one, reading logs, building and pushing images, cleaning up disk, and the Dockerfile instructions that matter.

Last updated August 29, 2026

On this page

- [Run a Container](#run-a-container)
- [List Containers](#list-containers)
- [Stop, Start and Restart](#stop-start-and-restart)
- [Remove Containers](#remove-containers)
- [Exec Into a Container](#exec-into-a-container)
- [Logs](#logs)
- [Copy Files](#copy-files)
- [Build Images](#build-images)
- [Pull, Push and Login](#pull-push-and-login)
- [Remove Images](#remove-images)
- [Clean Up](#clean-up)
- [Volumes](#volumes)
- [Networks](#networks)
- [Inspect and Stats](#inspect-and-stats)
- [Daemon and Service](#daemon-and-service)
- [Windows, Mac and WSL](#windows-mac-and-wsl)
- [Dockerfile Instructions](#dockerfile-instructions)
- [Gotchas](#gotchas)

## Run a Container

docker run creates a container from an image and starts it. Flags go before the image name; anything after the image name replaces the image's default command.

[TABLE]

A typical long-running service:

```
docker run -d --name web \
  -p 8080:80 \
  -v data:/data \
  --restart unless-stopped \
  nginx
```

Copy

docker run --name web fails with Conflict. The container name "/web" is already in use when an old container with that name exists, stopped or not. Remove it first with docker rm web; see [Error response from daemon](https://sshworkbench.com/fix/docker-error-response-from-daemon) for the other common variants. For multi-container apps, put all of this in a compose file instead: see the [docker compose commands](https://sshworkbench.com/cheatsheets/docker-compose) sheet or the [Docker Compose generator](https://sshworkbench.com/tools/docker-compose-generator).

## List Containers

[TABLE]

docker ps and docker container ls are the same command. Docker added the docker container ..., docker image ..., docker volume ... groupings in 2017 and kept the short forms as aliases, so use whichever you type faster.

## Stop, Start and Restart

[TABLE]

A container that stops on its own the moment it starts has a main process that exited; run docker logs web to see why. One that goes Restarting (1) over and over is the same problem under a restart policy; see [Docker container keeps restarting](https://sshworkbench.com/fix/docker-container-keeps-restarting).

## Remove Containers

| Command | What it does |
|----|----|
| docker rm web | Remove a stopped container |
| docker rm -f web | Stop and remove in one step |
| docker rm -v web | Also remove its anonymous volumes (named volumes stay) |
| docker rm \$(docker ps -aq) | Remove every stopped container (running ones error out) |
| docker rm -f \$(docker ps -aq) | Remove every container, running or not |
| docker container prune | Remove all stopped containers |
| docker container prune --filter until=24h | Only ones stopped more than a day ago |

Removing a container does not remove its image or its named volumes.

## Exec Into a Container

[TABLE]

exec needs a running container. To poke at a stopped one, copy files out with docker cp or start it with a different command: docker run -it --entrypoint sh image.

## Logs

Docker captures whatever the container's main process writes to stdout and stderr. Files the app writes inside the container do not show up here.

[TABLE]

Logs grow without limit unless you cap them. In daemon.json set "log-driver": "json-file" with "log-opts": {"max-size": "10m", "max-file": "3"}, or pass --log-opt max-size=10m to docker run.

## Copy Files

docker cp works on running and stopped containers. Paths are container:/path on the container side.

[TABLE]

Files copied in are owned by root unless you use -a. For anything more than a one-off, use a bind mount or a volume instead.

## Build Images

[TABLE]

The build context is the . at the end: everything in that directory is sent to the daemon, so add a .dockerignore with node_modules, .git and build output in it. Starting from scratch? The [Dockerfile generator](https://sshworkbench.com/tools/dockerfile-generator) writes a sensible multi-stage file for common stacks.

## Pull, Push and Login

[TABLE]

latest is only a tag, not a promise of the newest version: docker pull fetches whatever the publisher last tagged latest, and a running container does not update itself when you pull. Pull, then recreate the container.

## Remove Images

[TABLE]

image is being used by running container means exactly that: stop and remove the container, then rmi works. image has dependent child images means another image was built on top of it; remove the child first.

## Clean Up

Docker never deletes anything on its own. Stopped containers, old images, build cache and orphaned volumes pile up until the disk is full.

[TABLE]

docker system prune -a --volumes removes every volume that no running container is using right now. A database container that happens to be stopped counts as "not using" its volume, and the data is gone with no undo. Stop and think before adding --volumes. If the disk is already full, see [Docker no space left on device](https://sshworkbench.com/fix/docker-no-space-left-on-device) for the order to do things in.

## Volumes

Named volumes are managed by Docker and live under /var/lib/docker/volumes. Bind mounts map a host path you choose.

[TABLE]

Bind mount paths must be absolute, which is why \$(pwd) shows up so often. Back up a named volume with a throwaway container:

```
docker run --rm -v data:/data -v $(pwd):/backup alpine \
  tar czf /backup/data.tar.gz -C /data .
```

Copy

Restore it the same way with tar xzf /backup/data.tar.gz -C /data.

## Networks

Containers on the same user-defined network reach each other by container name. The default bridge network does not do name resolution, so create one.

[TABLE]

From inside a container, host.docker.internal reaches the host machine on Docker Desktop; on Linux add --add-host host.docker.internal:host-gateway.

## Inspect and Stats

| Command | What it does |
|----|----|
| docker inspect web | Everything Docker knows about a container, as JSON |
| docker inspect -f '{{.State.Status}}' web | One field |
| docker inspect -f '{{.NetworkSettings.IPAddress}}' web | The container's IP on the default bridge |
| docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web | IP on any network |
| docker inspect -f '{{json .Mounts}}' web | Volumes and bind mounts |
| docker inspect -f '{{.RestartCount}}' web | How many times the restart policy fired |
| docker inspect -f '{{.Config.Env}}' web | Environment variables it was started with |
| docker inspect -f '{{.State.Health.Status}}' web | Healthcheck result, if the image defines one |
| docker inspect nginx:latest | Works on images, volumes and networks too |
| docker stats | Live CPU, memory, network and disk I/O for every container |
| docker stats --no-stream | One snapshot and exit |
| docker stats web db | Only these containers |
| docker top web | Processes running inside a container |
| docker diff web | Files changed since the container started |
| docker events | Stream daemon events (starts, stops, dies, pulls) |
| docker info | Daemon configuration, storage driver, number of containers |
| docker version | Client and server versions |

docker inspect output is Go template territory: -f takes {{.Field.Subfield}} and {{json .Field}}. Pipe the plain output into jq when the template gets hard to read.

## Daemon and Service

The docker command is only a client. Every command on this page needs a daemon to talk to, so when they all hang, fail or ask for sudo, start here.

[TABLE]

docker: command not found and Cannot connect to the Docker daemon are different problems. The first means the CLI is not installed or not on your PATH; the second means it is installed and the daemon is not reachable, which is either a stopped service or a permissions problem on /var/run/docker.sock. See [Cannot connect to the Docker daemon](https://sshworkbench.com/fix/docker-cannot-connect-to-docker-daemon).

## Windows, Mac and WSL

Containers are Linux containers everywhere. On Windows and macOS the engine runs in a VM, so paths inside a container are always Linux paths no matter what shell you typed the command in.

[TABLE]

If docker works in PowerShell but not inside a WSL distro, that distro is missing the integration toggle under Settings, Resources, WSL integration. Reading files on the Windows drive from a container goes through a network share and is slow, so keep anything build-heavy inside the WSL filesystem (\\wsl\$\Ubuntu\home\you) instead of C:\\

## Dockerfile Instructions

The essentials, in the order they usually appear. Each instruction that changes the filesystem (RUN, COPY, ADD) creates a layer, and Docker caches layers from the top down, so put the things that change least first.

[TABLE]

Use the JSON array form (\["node", "server.js"\]) for CMD and ENTRYPOINT. The shell form (CMD node server.js) wraps the command in sh -c, so PID 1 is the shell and your process never sees the SIGTERM from docker stop. Any RUN step that exits non-zero stops the build, so a step that is allowed to fail needs \|\| true on the end. A multi-stage skeleton:

```
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

Copy

The [Dockerfile generator](https://sshworkbench.com/tools/dockerfile-generator) produces this shape for Node, Python, Go and others.

## Gotchas

- permission denied while trying to connect to the Docker daemon socket
  means your user is not in the
  docker
  group.
  sudo usermod -aG docker \$USER
  , then log out and in. If the socket is missing altogether, the daemon is not running: see [Cannot connect to the Docker daemon](https://sshworkbench.com/fix/docker-cannot-connect-to-docker-daemon).
- A container lives as long as its main process.
  docker run -d ubuntu
  exits immediately because
  bash
  with no terminal has nothing to do. Give it a real service, or
  -it
  for a shell.
- docker stop
  waits ten seconds and then kills. Apps that ignore SIGTERM (usually because the Dockerfile used the shell form of
  CMD
  ) always take the full ten seconds and lose in-flight work.
- docker pull
  does not update running containers. Pull, then
  docker rm -f
  and
  docker run
  again (or
  docker compose up -d
  , which does this for you).
- docker system prune -a --volumes
  deletes volumes of stopped containers, including databases. Leave
  --volumes
  off unless you mean it.
- docker rmi
  refuses while any container, even a stopped one, references the image.
  docker ps -a --filter ancestor=image
  finds them.
- Bind mount paths on
  docker run -v
  must be absolute.
  ./data:/data
  only works in compose files; on the command line use
  -v \$(pwd)/data:/data
  .
- A failed
  docker run
  has two layers of exit code. 125 means Docker itself rejected the command, usually a bad flag or an unknown image; 126 means the command exists in the image but is not executable; 127 means it is not on the container's PATH, which is nearly always a typo or a missing package; anything else is your own program's exit code.
- Anything beyond one or two containers belongs in a
  compose.yaml
  . The [docker compose commands](https://sshworkbench.com/cheatsheets/docker-compose) sheet covers the CLI and the file format.

### Manage Docker without the CLI gymnastics

SSH Workbench gives you a visual layer over Docker and Podman: start, stop, inspect, view logs without memorising flags.

[Try free for 7 days](https://sshworkbench.com/#install)

## Docker FAQ

### How do I run docker commands without sudo?

Add your user to the docker group with sudo usermod -aG docker \$USER, then log out and back in (or run newgrp docker) so the new group applies. The Docker socket at /var/run/docker.sock is owned by root:docker, so members of that group can talk to the daemon without sudo. Anyone in the docker group is effectively root on that machine, so only add accounts you would trust with root. If commands still fail with permission denied or cannot connect to the Docker daemon, the daemon is probably not running: check it with systemctl status docker.

### Where do I run docker commands on Windows?

In any terminal on the machine where Docker Desktop is installed. PowerShell, Command Prompt, Windows Terminal and a WSL shell all talk to the same engine, so docker ps lists the same containers in each. Docker Desktop has to be running first, because the CLI is only a client. On the WSL 2 backend, switch on Settings, Resources, WSL integration for your distro, or docker inside that distro reports command not found even though Desktop is up. The one thing that changes between shells is path syntax for bind mounts: -v \${PWD}:/app in PowerShell, -v %cd%:/app in Command Prompt, -v \$(pwd):/app in bash, WSL and macOS.

### What is the difference between CMD and ENTRYPOINT?

Both set what runs when the container starts. ENTRYPOINT is the fixed executable; CMD is the default arguments, and anything you put after the image name on docker run replaces CMD but not ENTRYPOINT. So ENTRYPOINT \["nginx"\] with CMD \["-g", "daemon off;"\] runs nginx with those flags by default, and docker run myimage -v runs nginx -v instead. An image with only a CMD is fully replaceable: docker run myimage sh runs a shell instead of the app. Override the entrypoint itself with docker run --entrypoint sh myimage. Use the JSON array form for both so no shell sits between Docker and your process and signals reach it directly.

### Why are docker commands hanging or not responding?

Nearly always the client cannot reach the daemon, or the daemon is busy. On Docker Desktop, check the whale icon: the engine may still be starting or need a restart. On Linux, run systemctl status docker and look at journalctl -u docker -n 50 for errors; a full disk (docker system df, df -h) stops the daemon from writing state and makes every command stall. A hanging docker ps with an otherwise healthy daemon usually points at a stuck containerd shim; systemctl restart docker clears it. If you get Cannot connect to the Docker daemon instead of a hang, the daemon is not running or your user cannot read the socket.

### Can I use docker commands with Podman?

Yes, for almost everything on this page. Podman's CLI copies Docker's, so podman run, podman ps, podman build and podman logs take the same flags, and many distros ship a podman-docker package that installs a docker command aliasing to podman. The differences show up at the edges: Podman runs rootless by default and has no daemon, so docker commands that talk to the daemon socket need podman.socket enabled for tools that expect one, and docker compose becomes podman compose (or docker compose pointed at the Podman socket). Volumes, networks and Dockerfiles behave the same.

---
Källa: https://sshworkbench.com/cheatsheets/docker
