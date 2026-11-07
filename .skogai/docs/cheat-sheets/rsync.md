# rsync Commands

rsync copies files locally or over SSH and only sends the parts that changed, which makes it the tool for backups, deployments, and moving a server. Read the trailing slash section first, because that one character decides what every other command here does.

Last updated September 11, 2026

On this page

- [Basic Copy](#basic-copy)
- [Trailing Slash](#trailing-slash)
- [Over SSH](#over-ssh)
- [Flags Explained](#flags-explained)
- [Dry Run](#dry-run)
- [Exclude and Include](#exclude-and-include)
- [Delete and Mirror](#delete-and-mirror)
- [Progress and Resume](#progress-and-resume)
- [Speed and Large Transfers](#speed-and-large-transfers)
- [Compare and Verify](#compare-and-verify)
- [Permissions and Ownership](#permissions-and-ownership)
- [Backups and Snapshots](#backups-and-snapshots)
- [Cron and Logging](#cron-and-logging)
- [Daemon Mode](#daemon-mode)
- [Common Recipes](#common-recipes)
- [Windows and macOS](#windows-and-macos)
- [rsync vs scp](#rsync-vs-scp)
- [Exit Codes](#exit-codes)
- [Gotchas](#gotchas)

## Basic Copy

-a (archive) is the flag you almost always want: recursive, keeps permissions, times, owner, group, symlinks, and devices. The [rsync command builder](https://sshworkbench.com/tools/rsync-command-builder) assembles one of these interactively.

[TABLE]

rsync -a with no -v prints nothing on success, which is what you want in cron.

## Trailing Slash

The one thing about rsync that catches everyone, and the reason behind most "it copied into the wrong folder" and "--delete wiped my directory" reports. A trailing slash on the source path means "the contents of this directory". No slash means "this directory itself". The slash on the destination changes nothing at all.

[TABLE]

Read src/ as src/\* including hidden files, and src as "put a copy of this directory in there". Three consequences worth knowing before you run anything else on this page:

- With
  --delete
  ,
  src/ dest/
  prunes everything in
  dest
  , while
  src dest/
  only prunes
  dest/src
  and leaves the rest of
  dest
  alone. Getting that backwards is how people empty a directory.
- Tab completion appends the slash for you, so the command you typed and the command you tabbed are not the same command. Check the source path before pressing Enter, and dry run with
  -n
  .
- src/
  is not the same as
  src/\*
  . The glob is expanded by the shell, which skips dotfiles, so
  rsync -av src/\* dest/
  silently leaves out
  .env
  and
  .htaccess
  .

## Over SSH

Remote paths are user@host:/path. rsync must be installed at both ends. It runs over SSH by default, so keys, ~/.ssh/config aliases, and agent forwarding all apply; see the [SSH cheat sheet](https://sshworkbench.com/cheatsheets/ssh).

[TABLE]

Copy between two remote servers: rsync cannot take two remote paths in one command. Log into one and push to the other, or forward your agent so the first server can authenticate to the second.

```
ssh -A user@server1 'rsync -avz /var/www/ user@server2:/var/www/'
```

Copy

A connection that fails with exit code 255 is an SSH problem, not an rsync one. See [Connection refused](https://sshworkbench.com/fix/ssh-connection-refused) and [Permission denied (publickey)](https://sshworkbench.com/fix/ssh-permission-denied-publickey).

## Flags Explained

Paste any command into the [rsync flag explainer](https://sshworkbench.com/tools/rsync-flag-explainer) to decode it.

[TABLE]

-avz is the standard remote copy, -avh the standard local one, and -avzP when the link might drop.

## Dry Run

Run every new rsync command with -n first, and always before --delete.

[TABLE]

In itemized output, \>f is a file being sent, cd a directory being created, \*deleting a deletion, and the dots after the type mark which attributes changed (s size, t time, p permissions, o owner).

## Exclude and Include

Patterns match relative to the top of the transfer. A trailing / matches directories only, a leading / anchors the pattern to the transfer root, and \* does not cross a / (\*\* does).

[TABLE]

Include and exclude rules are checked in order and the first match wins, which is why --include comes before --exclude '\*'. An exclude that "does not work" is almost always anchored wrong: --exclude 'src/node_modules' does not match when the transfer root is src/, but --exclude '/node_modules' does.

## Delete and Mirror

--delete makes the destination match the source exactly, including removing files. Combined with a wrong path or a missing trailing slash it can empty a directory, so dry run first.

[TABLE]

--delete only deletes inside directories that are part of the transfer. rsync -av --delete src dest/ (no trailing slash) syncs dest/src/ and never touches the rest of dest.

## Progress and Resume

| Command | What it does |
|----|----|
| rsync -avP src/ dest/ | Keep partial files and show per-file progress |
| rsync -avh --info=progress2 src/ dest/ | One overall percentage, speed, and time remaining |
| rsync -av --partial --partial-dir=.rsync-partial src/ dest/ | Keep partials in a hidden directory rather than in place |
| rsync -avP src/ dest/ | Run again after an interruption; partial files continue from where they stopped |
| rsync -av --append-verify big.iso user@host:/path/ | Append to a partially transferred file and checksum the result; for single large files only |
| rsync -av --bwlimit=5000 src/ user@host:/path/ | Cap at about 5 MB/s so you do not saturate the link |
| rsync -av --bwlimit=50m src/ user@host:/path/ | Cap at 50 MiB/s |
| rsync -av --timeout=120 src/ user@host:/path/ | Abort if the transfer stalls for two minutes |
| nohup rsync -avz src/ user@host:/path/ \> rsync.log 2\>&1 & | Run in the background and survive logout |

For a transfer that takes hours, start it inside tmux or screen so a dropped SSH session does not kill it; see the [tmux cheat sheet](https://sshworkbench.com/cheatsheets/tmux). If the SSH session itself keeps dropping, see [Broken pipe](https://sshworkbench.com/fix/ssh-broken-pipe).

## Speed and Large Transfers

One rsync run is single-threaded and uses one SSH connection, so the way to go faster is usually to do less work or to run several transfers at once.

[TABLE]

On trees with hundreds of thousands of small files, building and comparing the file list costs more than the transfer, and no flag fixes that. Split the tree and run several rsyncs, or tar the directory and copy one stream.

## Compare and Verify

rsync decides what to send from size and modification time, not from file contents. These commands compare without copying, or force a content comparison.

[TABLE]

rsync already checksums every file it transfers and retries any that fails, so a run that exits 0 wrote correct data. -c is about deciding what to send, not about verifying what arrived.

## Permissions and Ownership

| Command | What it does |
|----|----|
| rsync -av src/ dest/ | Preserve permissions, times, group; owner too when running as root |
| rsync -av --chown=www-data:www-data src/ dest/ | Set a fixed owner and group on everything copied (needs root at the destination) |
| rsync -av --chmod=D755,F644 src/ dest/ | Set directories to 755 and files to 644 as they land |
| rsync -av --no-perms --no-owner --no-group src/ dest/ | Copy without permission or ownership bits (exFAT, SMB shares) |
| rsync -av --no-o --no-g src/ dest/ | Same for owner and group only, keeping permissions |
| rsync -rltv src/ dest/ | Recursive, links, and times, but no permissions or ownership at all |
| rsync -av --numeric-ids src/ dest/ | Keep UID and GID numbers instead of mapping names (full system copies) |
| rsync -avAX src/ dest/ | Also copy ACLs and extended attributes |
| rsync -av --size-only src/ dest/ | Compare by size only, for filesystems that cannot store exact times |
| rsync -av --modify-window=1 src/ dest/ | Treat times within one second as equal (FAT stores 2-second stamps) |

Preserving owner means rsync on the receiving end runs as root, either because you are root or via --rsync-path="sudo rsync". Otherwise files are owned by the connecting user and rsync prints nothing about it.

## Backups and Snapshots

--link-dest is what turns rsync into a backup tool: each run is a full dated tree, but files that did not change are hard links to the previous run and cost no extra disk. The [rsync command builder](https://sshworkbench.com/tools/rsync-command-builder) has a link-dest field if you would rather assemble the command than type it.

| Command | What it does |
|----|----|
| rsync -aAXv --delete src/ /backup/current/ | A plain mirror backup, ACLs and extended attributes included |
| rsync -av --link-dest=/backup/latest src/ /backup/\$(date +%F)/ | Dated snapshot; unchanged files are hard links to the previous one |
| rsync -av --backup --backup-dir=/backup/old/\$(date +%F) src/ dest/ | Keep the previous version of anything overwritten or deleted |
| rsync -av --backup --suffix=.bak src/ dest/ | Rename replaced files in place instead of moving them aside |
| rsync -avz --delete src/ user@host:/backup/ | Offsite copy over SSH |
| rsync -av --exclude-from=/etc/backup-excludes src/ /backup/ | Keep the exclusion list in a file you can version |
| rsync -av --delete --max-delete=500 src/ /backup/ | Abort rather than mirror a source that has gone missing |

A hard-linked snapshot set shares inodes, so every snapshot of an unchanged file is the same blocks on the same disk. It protects against deleting a file, not against the drive dying. Keep one copy on another machine.

## Cron and Logging

In cron there is no terminal, no ssh-agent, and a minimal PATH, which is where nearly every "works by hand, fails in cron" report comes from.

| Command | What it does |
|----|----|
| rsync -a --log-file=/var/log/rsync.log src/ dest/ | Write a full transfer log |
| rsync -a --log-file-format="%t %o %f %l" src/ dest/ | Choose what each log line holds (time, operation, file, length) |
| rsync -a -e "ssh -i /root/.ssh/backup_key -o BatchMode=yes" src/ user@host:/b/ | Fixed key, and fail instead of prompting for a password |
| flock -n /var/lock/backup.lock rsync -a src/ dest/ | Skip this run if the last one is still going |
| ionice -c3 nice -n19 rsync -a src/ dest/ | Run at the lowest disk and CPU priority |
| rsync -a --out-format="%i %n" src/ dest/ \>\> /var/log/rsync.log | Itemized change log without full verbosity |

```
# /etc/cron.d/backup
0 3 * * * root /usr/bin/flock -n /var/lock/backup.lock /usr/bin/rsync -a --delete \
  -e "ssh -i /root/.ssh/backup_key -o BatchMode=yes" /srv/ backup@host:/srv/ \
  >> /var/log/backup.log 2>&1
```

Copy

Use absolute paths, a key with no passphrase (or a systemd timer with the agent available), and check \$? rather than the output: rsync -a prints nothing on success, so a silent cron job and a failed one look the same. BatchMode=yes turns a password prompt into an immediate exit 255, which is the behaviour you want when nobody is watching.

## Daemon Mode

rsync can also run as its own service on TCP 873, with no SSH and no encryption. Remote paths then use a double colon or an rsync:// URL, and the first component is a module name from rsyncd.conf, not a filesystem path.

[TABLE]

```
# /etc/rsyncd.conf
[backup]
path = /srv/backup
read only = false
auth users = deploy
secrets file = /etc/rsyncd.secrets
hosts allow = 10.0.0.0/24
```

Copy

One colon means SSH, two colons mean the daemon. Mixing them up gives unexpected remote arg or a hang on port 873. Daemon traffic is plaintext and the passwords are not SSH keys, so keep it on a private network and use the default SSH transport over the internet.

## Common Recipes

Back up a home directory to an external drive:

```
rsync -avh --delete --exclude '.cache/' --exclude 'node_modules/' ~/ /Volumes/Backup/home/
```

Copy

Mirror a website from a server, keeping a rotating set of dated snapshots that share unchanged files via hard links:

```
rsync -avz --delete --link-dest=/backup/www/latest user@host:/var/www/ /backup/www/$(date +%F)/
ln -sfn /backup/www/$(date +%F) /backup/www/latest
```

Copy

Deploy a build, excluding what should not ship, then reload:

```
rsync -avz --delete --exclude '.git' --exclude '.env' --exclude 'node_modules' \
  ./dist/ deploy@host:/var/www/app/ && ssh deploy@host 'sudo systemctl reload nginx'
```

Copy

Copy only files changed in the last day:

```
find src -type f -mtime -1 -printf '%P\n' | rsync -av --files-from=- src/ dest/
```

Copy

Sync two directories both ways (run once in each direction; rsync is one-way, --update keeps the newer copy):

```
rsync -avu a/ b/ && rsync -avu b/ a/
```

Copy

Move a whole server's data directory to a new host over a slow link, resumable:

```
rsync -avzP --bwlimit=20m -e "ssh -p 2222" /srv/data/ root@newhost:/srv/data/
```

Copy

Clone a disk or root filesystem to another mounted volume, staying off /proc, /sys, and other mounts:

```
sudo rsync -aAXHvx --numeric-ids --exclude={'/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} / /mnt/newdisk/
```

Copy

## Windows and macOS

rsync is a Unix program. Windows has no native version, and the one Apple ships is not the rsync the manual describes.

[TABLE]

Check which one you have with rsync --version. Under WSL, a copy from /mnt/c cannot preserve Unix permissions, so expect -a to warn and use --no-perms --no-owner --no-group there too.

## rsync vs scp

[TABLE]

OpenSSH's scp has used the SFTP protocol under the hood since 9.0, which fixed its security problems but did not add any of the above.

Two other comparisons come up often. rclone is the tool when one side is cloud storage (S3, Google Drive, OneDrive, Backblaze), which rsync cannot speak at all. robocopy is the Windows built-in that mirrors local and SMB paths with /MIR, but has no SSH transport and no delta algorithm.

## Exit Codes

rsync reports its result in the exit code (echo \$? right after it runs), which is what a cron job or a script should check.

[TABLE]

## Gotchas

- --delete
  with the wrong trailing slash or a mistyped destination removes real files.
  -n
  first, every time.
- rsync must exist on the remote host.
  bash: rsync: command not found
  from the far end and exit code 12 or 127 mean
  apt install rsync
  there, not here.
- A
  .bashrc
  on the remote that prints something (a banner, a
  echo
  , an unguarded
  neofetch
  ) corrupts the protocol stream and gives
  protocol version mismatch
  or code 12. Guard it with
  \[\[ \$- != \*i\* \]\] && return
  at the top.
- macOS ships an old rsync 2.6.9, and macOS 15 replaced it with openrsync, which lacks flags such as
  --info=progress2
  .
  brew install rsync
  gives you 3.x; on Windows, rsync comes with WSL, Cygwin, or MSYS2, not with Git Bash by default.
- -z
  slows down a LAN copy and does nothing for files that are already compressed (images, video, archives). Use it over the internet, drop it locally.
- Copying to a drive formatted exFAT, FAT32, or NTFS from Linux recopies everything each run because the filesystem cannot store the same times and permissions. Add
  --no-perms --no-owner --no-group --modify-window=1
  or
  --size-only
  .
- rsync -av src/\*.jpg dest/
  dies in zsh with
  zsh: no matches found
  when nothing matches, because zsh refuses an unmatched glob instead of passing it through the way bash does. Pick files with
  --include '\*.jpg' --exclude '\*'
  rather than a shell glob. On a remote source the glob is expanded by the remote shell, so it has to be quoted:
  rsync -av 'user@host:/var/log/\*.gz' ./
  .
- unexpected remote arg
  means the remote path is missing its colon (
  user@host/path
  instead of
  user@host:/path
  ) or you gave two remote paths in one command.
- Changing only a file's permissions or owner does not change its size or time, so a plain
  -av
  run does not resend it but does update the attributes. Content edits that keep the same size and time (rare, but
  touch -r
  and some build tools do it) need
  -c
  to be noticed.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## rsync FAQ

### Does rsync copy or move files?

It copies. The source is untouched after a run, and running the same command again sends only what changed since. To get a move, add --remove-source-files, which deletes each file from the source after it has been transferred and verified. That flag leaves the now-empty directories behind, so follow it with find src -type d -empty -delete if you want them gone. There is no flag that removes source directories in one step.

### When should you use a trailing slash with rsync?

On the source, whenever you want the contents of that directory rather than the directory itself. rsync -av src/ dest/ gives you dest/file1. rsync -av src dest/ gives you dest/src/file1. The slash on the destination makes no difference either way. Two things make this worse than it sounds. Shell tab completion appends the slash for you, so a path you tabbed and the same path typed by hand are not the same command. And the slash decides what --delete removes: src/ dest/ prunes the whole of dest, while src dest/ only prunes dest/src. Dry run with -n before any --delete.

### Does rsync overwrite existing files?

Yes, silently, whenever the source file differs in size or modification time, and that includes overwriting a destination copy that is newer. It never asks. The write itself is safe: rsync builds a temporary file in the destination directory and renames it into place at the end, so nothing ever reads a half-written file and an interrupted transfer leaves the old version intact. Use --update to skip anything newer on the destination, --ignore-existing to leave files that are already there alone, or --backup --backup-dir=DIR to keep the old copy. --inplace turns off the temporary-file step, which saves disk space on large images but leaves a corrupt file behind if the run dies.

### Does rsync delete files in the destination?

Only when you pass --delete. A normal run adds and updates, and removes nothing. Even with --delete, rsync only prunes directories that are part of the transfer, so rsync -av --delete src dest/ (no slash on the source) cannot touch anything outside dest/src. Files matched by an --exclude are protected unless you also pass --delete-excluded. The guard worth putting in any scripted mirror is --max-delete=N, which makes rsync stop and exit 25 rather than remove more than N files. That is what saves you on the morning the source drive fails to mount and looks empty.

### Why is rsync faster than scp?

On a repeat copy, because it sends only what changed. rsync compares size and modification time, skips the files that match, and for a file that does differ sends just the blocks that differ, so re-syncing a 50 GB tree after one edit moves a few megabytes. On a first copy of new data there is nothing to skip and rsync can be the slower of the two: it builds a file list before it starts, which hurts on trees with hundreds of thousands of small files, and -z burns CPU on data that is often already compressed. Between two local disks, add -W to skip the delta calculation entirely.

---
Källa: https://sshworkbench.com/cheatsheets/rsync
