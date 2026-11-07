# PM2 Commands

PM2 is the process manager most Node.js apps run under in production. This sheet covers the pm2 commands for starting and naming apps, reading logs, cluster mode, and making everything survive a reboot with save and startup.

## Start Processes

| Command | What it does |
|---|---|
| `pm2 start app.js` | Start application with default settings |
| `pm2 start app.js --name "api"` | Start and assign custom name |
| `pm2 start app.js -i max` | Start in cluster mode utilizing all CPU cores |
| `pm2 start npm --name "frontend" -- start` | Run npm start script under PM2 |
| `pm2 start "npm run dev" --name "dev"` | Run custom shell script command |

More than a couple of flags belongs in an ecosystem file rather than your shell history; the [PM2 ecosystem generator](https://sshworkbench.com/tools/pm2-ecosystem-generator) writes one from a form.

## List and Status

| Command | What it does |
|---|---|
| `pm2 list` or `pm2 ls` | Display tabular list of all managed applications |
| `pm2 show api` or `pm2 describe api` | Detailed info (memory, restarts, paths, env) |
| `pm2 jlist` | Output process list in raw JSON format |

The restart counter (↺ in the list) climbing on its own means the app is crash-looping; read the error log before anything else.

## Logs

PM2 captures each process's stdout and stderr to files under ~/.pm2/logs/.

| Command | What it does |
|---|---|
| `pm2 logs` | Stream combined real-time logs from all processes |
| `pm2 logs api` | Stream logs for specific application |
| `pm2 logs --lines 100` | Display last 100 log lines |
| `pm2 flush` | Empty and clear all current log files |

PM2 does not rotate logs on its own, and a chatty app fills a disk quietly. Install pm2-logrotate on every server the first time you set one up.

## Restart, Reload and Stop

| Command | What it does |
|---|---|
| `pm2 restart api` | Kill and restart process |
| `pm2 reload api` | Zero-downtime rolling restart (cluster mode) |
| `pm2 stop api` | Stop running process without deleting configuration |
| `pm2 delete api` | Stop and remove application from PM2 registry |
| `pm2 restart all` | Restart all managed applications |

stop keeps the entry (status stopped); delete forgets it. After any change you want back after a reboot, run pm2 save again.

## Cluster Mode

Cluster mode runs several instances of the same Node app behind PM2's built-in load balancer, one per core with max. The app needs no code changes as long as it does not keep local state.

| Command                 | What it does                                  |
|-------------------------|-----------------------------------------------|
| pm2 start app.js -i max | One instance per CPU core                     |
| pm2 start app.js -i 4   | Exactly four instances                        |
| pm2 start app.js -i -1  | All cores but one                             |
| pm2 scale api 8         | Resize a running cluster to 8 instances       |
| pm2 scale api +2        | Add two instances                             |
| pm2 reload api          | Roll through the instances with zero downtime |

Cluster mode is Node-only, since it uses the Node cluster module. Sticky sessions and anything held in process memory (in-memory sessions, local caches) break across instances; move that state to Redis or the database first.

## Save, Startup and Resurrect

Surviving a reboot is a two-step dance, and skipping the second step is the classic mistake.

| Command | What it does |
|---|---|
| `pm2 save` | Save current application list to dump file |
| `pm2 startup` | Generate and configure systemd service for boot autostart |
| `pm2 resurrect` | Restore saved applications after system reboot |
| `pm2 unstartup` | Remove system boot service configuration |

So the full sequence is: pm2 startup, run the command it printed, get your apps running the way you want, then pm2 save. The hook restores whatever the last pm2 save captured, so rerun it after adding, deleting or renaming processes.

## Windows

pm2 startup only knows Linux and macOS init systems. On Windows it prints nothing useful, so PM2 has to be installed as a Windows service instead.

| Tool / Command | Purpose |
|---|---|
| `npm install -g pm2-windows-service` | Install PM2 wrapper as a native Windows Service |
| `pm2-service-install` | Register background Windows service |

The other option is pm2-installer, which registers PM2 itself as a Windows service so it starts before anyone logs in. Either way pm2 save is still what decides which apps come back. Everything else (list, logs, restart, monit, ecosystem files) behaves the same; paths in an ecosystem file want forward slashes or escaped backslashes.

## Environment Variables

| Command / Flag | Purpose |
|---|---|
| `pm2 start app.js --env production` | Load production environment configuration |
| `pm2 restart app.js --update-env` | Apply modified environment variables to running process |

PM2 snapshots the environment when a process first starts and reuses it on every restart. Changing a variable in the shell or in .bashrc does nothing until you restart with --update-env or delete and start fresh. This surprises everyone once.

## Node Version and Interpreter

The PM2 daemon keeps the Node version it was started with. Switching versions with nvm changes your shell, not the daemon, so apps keep running on the old binary until you reload the daemon.

| Command | What it does |
|---|---|
| `pm2 start app.py --interpreter python3` | Run Python script under PM2 daemon |
| `pm2 start app.ts --interpreter ts-node` | Run TypeScript file directly |
| `pm2 start app.js --node-args="--max-old-space-size=4096"` | Pass V8 engine runtime flags |

In an ecosystem file the same settings are the interpreter and interpreter_args fields, which is the sane place to pin a version per app:

```
{
  name: "api",
  script: "./server.js",
  interpreter: "/home/deploy/.nvm/versions/node/v22.11.0/bin/node",
}
```

After an nvm upgrade, pm2 update is only half the job: the boot hook installed by pm2 startup has the old PATH written into it, so run pm2 unstartup, pm2 startup, the command it prints, then pm2 save again. PM2 no longer bundles ts-node, so TypeScript needs npm i -g ts-node typescript (or a local install plus npx); compiling to JavaScript first and running the output is steadier in production.

## Ecosystem File

ecosystem.config.js holds everything the start flags express, in a file you can commit. pm2 init writes a sample, or the [PM2 ecosystem generator](https://sshworkbench.com/tools/pm2-ecosystem-generator) builds one from a form.

```
module.exports = {
  apps: [{
    name: "api",
    script: "./server.js",
    instances: "max",
    exec_mode: "cluster",
    max_memory_restart: "300M",
    args: "--port 3000",
    env: { NODE_ENV: "development" },
    env_production: { NODE_ENV: "production" },
  }],
};
```

| Command | What it does |
|---|---|
| `pm2 init simple` | Generate sample `ecosystem.config.js` configuration file |
| `pm2 start ecosystem.config.js` | Launch all applications declared in ecosystem file |
| `pm2 start ecosystem.config.js --env production` | Launch with production profile |

## Monitoring

| Command | What it does |
|---|---|
| `pm2 monit` | Terminal dashboard monitoring CPU, memory, and logs in real time |
| `pm2 plus` | Connect process instance to web-based monitoring dashboard |

pm2 monit is the fastest answer to "which process is eating the CPU". For alerting and history, PM2's hosted monitoring (pm2 plus) exists, but plain pm2 monit over SSH covers day-to-day checks.

## Install and Upgrade

| Command | Action |
|---|---|
| `npm install -g pm2` | Install PM2 globally via npm |
| `pm2 update` | Upgrade in-memory daemon to match installed package version |

Upgrading the npm package alone changes nothing for running apps, since the old daemon stays in memory. pm2 update is what swaps it. Under nvm, PM2 is installed per Node version, so a new Node version means installing PM2 again.

## Deployment

| Command | What it does |
|----|----|
| pm2 deploy production setup | First-time setup of the deploy target defined in the ecosystem file |
| pm2 deploy production | Pull, install and reload on the target servers |

pm2 deploy reads a deploy section in the ecosystem file (host, repo, path, post-deploy command) and works fine for simple git-based deploys. Teams that outgrow it usually move to CI plus pm2 reload over SSH.

If you would rather have the init system own the process, with proper dependencies and journald logging, the [pm2 to systemd converter](https://sshworkbench.com/tools/pm2-to-systemd) turns an ecosystem file into unit files, and the [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl) covers managing them.

## Gotchas

- pm2 startup alone does nothing at boot. It prints a command; run that command, then pm2 save. The saved dump is what gets restored, so save again after every change to the list.
- pm2 reload is only zero-downtime in cluster mode with two or more instances. In fork mode it is just a restart with a friendlier name.
- Restarts keep the environment from the first start. New or changed variables need pm2 restart api --update-env, or a delete and a fresh start.
- Logs are never rotated by default. pm2 install pm2-logrotate before the disk fills, and pm2 flush when it already has.
- --watch in production causes restart loops when the app writes into its own directory (logs, uploads). Use --ignore-watch, or better, no watch at all outside development.
- pm2: command not found in cron, CI or GitHub Actions usually means npm's global bin is not on that context's PATH; use the absolute path to the binary.
- Switching Node with nvm does not move the apps. The daemon holds the old version until pm2 update, and the boot hook holds the old PATH until you rerun pm2 startup and pm2 save.
- pm2 kill takes down the daemon and every app with it. To remove one app, pm2 delete api.

## PM2 FAQ

### How do I make PM2 start on boot?

Two commands, and people routinely stop after the first. pm2 startup does not enable anything itself: it detects your init system and prints a command, usually starting with sudo env PATH=..., which you copy, paste and run once to install the boot hook. Then pm2 save writes the list of processes currently running to ~/.pm2/dump.pm2, and that file is what gets restored at boot. Skip pm2 save and the server comes back up running nothing. Rerun pm2 save whenever the process list changes, and pm2 unstartup removes the hook. On Windows pm2 startup does nothing at all, since there is no init system for it to detect; install PM2 as a service with pm2-installer instead, then pm2 save as usual. If you would rather let systemd own the app directly, the pm2 to systemd converter on this site turns an ecosystem file into unit files.

### How do I check which Node version PM2 is using?

pm2 describe api prints the interpreter path and Node version for one process, and pm2 report shows the version the PM2 daemon itself is running. They can disagree, and that is the whole problem: the daemon keeps the node that was on PATH when it first started, so after nvm install 22 your apps carry on with the old binary no matter how many times you restart them. pm2 update fixes it by reloading the daemon in place on the current node and bringing the processes back. Two follow-ups get missed. The boot hook from pm2 startup has the old PATH baked into it, so rerun pm2 unstartup, pm2 startup and pm2 save after switching versions. And when different apps need different versions, pin each one with --interpreter and an absolute path to that node binary.

### How do I stop a PM2 process for good?

pm2 stop api halts the process but keeps the entry, so it still appears in pm2 list as stopped and pm2 restart api brings it back. pm2 delete api removes the entry. pm2 kill stops the daemon and everything under it. The step people forget is pm2 save: the boot hook restores whatever the last save captured, so anything you stopped or deleted is back after the next reboot unless you save again. If a process starts up again the moment you stop it, check pm2 list for a duplicate entry under a different name, and check whether it was started with --watch and something is writing into its directory.

### How do I run npm start with PM2?

Point PM2 at the npm binary and pass the script name after a double dash: pm2 start npm --name web -- start. Everything after the bare -- goes to npm, so pm2 start npm --name web -- run dev runs npm run dev the same way. This works but adds an npm process in front of node, so for production the cleaner move is to check what npm start actually runs in package.json and start that file directly: pm2 start ./server.js --name web. For scripts that need build tools or watchers, keep them out of PM2 entirely and reserve it for the long-running server.

### Is PM2 only for Node?

No. --interpreter runs anything with a shebang or a runtime: pm2 start app.py --interpreter python3, pm2 start run.sh --interpreter bash, pm2 start app.rb --interpreter ruby. Restarts, logs, monitoring and boot persistence all work the same. Compiled binaries need no interpreter at all: pm2 start ./mybinary --name svc. What is Node-only is cluster mode, because -i uses Node's own cluster module to share one listening socket between instances. For a Python or Ruby service, run several named copies on different ports behind nginx, or use that runtime's worker model (gunicorn, puma) and let PM2 supervise the one master process.

---
Source: https://sshworkbench.com/cheatsheets/pm2
