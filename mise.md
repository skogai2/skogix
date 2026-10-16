- **`mise daemons`** keeps long-running processes (a dev server, `postgres`,
  `redis`) alive with readiness checks, using pitchfork.

## From a bare OS to a working machine

`mise bootstrap` reads the same config and applies everything a machine
needs. It is declarative and idempotent: parts that already match are left
alone, so it is safe to rerun.

### The flow on a fresh install

```sh
curl -fsSL https://mise.run | sh                      # installs ~/.local/bin/mise
~/.local/bin/mise bootstrap --adopt OWNER/REPO --dry-run
~/.local/bin/mise bootstrap --adopt OWNER/REPO
```

- `--adopt <url|OWNER/REPO>` clones a repo of global mise config into
  `~/.config/mise` (or restores a dotfile-history repo) and applies it.
- `--from <url>` clones a self-contained bootstrap project (a repo with a
  `mise.toml`) into a separate checkout and applies that.
- `mise generate install-script` produces a script that downloads a pinned
  mise version, for when "latest" isn't acceptable.

### What it can declare

| Section | Manages |
|---|---|
| `[bootstrap.packages]`, `[bootstrap.plugins]` | OS packages: apt, dnf, pacman, AUR helpers, apk, zypper, nix, Homebrew, Flatpak, mas, WinGet, scoop |
| `[bootstrap.users]`, `[bootstrap.groups]` | Linux users and groups |
| `[bootstrap.files]`, `[bootstrap.directories]` | System files with content, owner and permissions |
| `[bootstrap.secrets]` | Secret inputs that file and dotfile templates can read |
| `[bootstrap.services]` | User services, and existing Linux system services |
| `[bootstrap.linux.firewall]` | Host firewall policy and rules |
| `[bootstrap.linux.systemd.units]` | systemd user units |
| `[bootstrap.compose]` | Docker Compose projects |
| `[bootstrap.repos]` | Git repos to clone |
| `[dotfiles]`, `[dotfile_groups]` | Dotfiles (see below) |
| `[bootstrap.mise_shell_activate]`, `[bootstrap.user]` | Shell activation lines, login shell |
| `[bootstrap.macos.*]` | `defaults write` preferences, LaunchAgents |
| `[tools]` | The same tools `mise install` installs |
| `[bootstrap.hooks]`, `[tasks.bootstrap]` | Escape hatches for everything else |

```toml
[bootstrap.packages]
"apt:build-essential" = "latest"            # "latest" = any installed version is fine
"apt:curl" = "8.5.0-2ubuntu10"              # pinned, in the manager's own format
"brew-cask:1password" = { os = "macos" }
"brew-cask:slack" = { env = "work" }        # only when MISE_ENV=work
"pacman:libreoffice-fresh" = { state = "absent" }

[bootstrap.mise_shell_activate]
fish = true

[bootstrap.hooks]
final = "mise exec -- gh auth status"

[tasks.bootstrap]
run = "node --version"
```

### Order of a run

1. Resolve secret inputs and render templates. A missing value stops the run before anything changes.
2. Accounts, package plugins, then OS packages
3. System files, services, firewall, Compose
4. Repos, then dotfiles
5. Shell activation, macOS defaults, systemd units, login shell
6. Tools
7. The `bootstrap` task, then the `final` hook

`--only <part>` and `--skip <part>` select parts by those names.

### Inspecting before applying

| Command | Shows |
|---|---|
| `mise bootstrap --dry-run` | What a run would do. Hooks and the task are printed, not run. |
| `mise bootstrap status` | The state of every part. `--missing` sets the exit code for CI. |
| `mise bootstrap plan` | Resource-level changes for packages, files, services, firewall, Compose |
| `mise bootstrap unapply` | Removes what a config environment's bootstrap sections created |

### Dotfiles

`mise dotfiles` (alias `mise dot`) has two modes that can be mixed:

- **Deploy**: a `[dotfiles]` entry puts a file in place from a source, by
  `symlink`, `copy` or `template`, or from inline `content`. `mise dot apply`,
  `diff`, `status` and `unapply` work on these.
- **Track**: `mise dot track <path>` leaves the file where it is and saves
  checkpoints of it to a local Git history. `history`, `rollback` and `undo`
  browse and restore; `origin`, `sync` and `pull` share it between machines.
  A tracked file can have per-OS, per-environment or per-machine variants.

### Other machines

- `mise bootstrap remote` applies a config to hosts over SSH
  (`[bootstrap.remote]`).
- `mise ssh --github-relay-read-only` opens an SSH session where the remote
  host can clone and download from GitHub repos you allow, using this
  machine's credentials. The token is never copied to the host.
- `mise oci` builds a container image from a project's tools, one layer per
  tool version (*experimental*).
- `mise generate devcontainer` writes a devcontainer config that installs
  mise and the project's tools.

### Gotchas

- **Not a transaction.** If step 6 fails, steps 1 to 5 stay applied. Fix and rerun.
- **Hooks and the `bootstrap` task run every time**, so they must be safe to repeat.
- **`--only` doesn't pull in dependencies.** A file owned by a new user needs both `accounts` and `files`.
- **`--dry-run` still renders templates**, so an `exec()` inside one runs.
- **sudo**: apt, dnf, pacman, apk and zypper run through `sudo`, and each
  command is logged first. AUR helpers refuse to run as root and call sudo
  themselves. `system_packages.sudo = false` forbids elevation.
- **`"latest"` never upgrades** an installed package. Use
  `mise bootstrap packages upgrade` for that.
- **Removal** (`state = "absent"`) only works for pacman, scoop and zypper.

## What it replaces

| Job | Usual tool | mise |
|---|---|---|
| Language versions | nvm, pyenv, rbenv, asdf | `[tools]` |
| CLI tools from GitHub, npm, cargo, pipx | each ecosystem's installer | `[tools]` with a backend prefix |
| Per-directory env vars | direnv, dotenv | `[env]` |
| Secrets in env | sops plus wrapper scripts | `_.file` with SOPS, or fnox |
| Task runner | make, just, npm scripts | `[tasks]`, `mise-tasks/` |
| File watcher | watchexec, entr | `mise watch` |
| Dotfiles | chezmoi, stow, yadm | `[dotfiles]`, `mise dot` |
| Machine setup | Ansible, Brewfile, shell scripts | `mise bootstrap` |
| Dev services | docker-compose, overmind | `[daemons]` (*experimental*) |

## Not verified here

- The exact syntax for inline age-encrypted values. The secrets page names
  the feature but shows no example.
- A worked `aur:` or `flatpak:` package entry. The managers are listed, and
  the `"manager:package" = "version"` form is documented, but the docs page
  read here only showed a `pacman:` entry in its removal example.
- Entry syntax for `[bootstrap.repos]`, `[bootstrap.user]`,
  `[bootstrap.services]` and `[dotfiles]`. Their subpages weren't read.
- Nothing here was run against this machine beyond read-only commands
  (`--help`, `mise doctor`, `mise config ls`).

