# Git Commands

Git is the version control system behind almost every codebase. This sheet is a full git commands list with examples: starting a repo, the everyday commit and push loop, branching and merging, and the undo commands (reset, revert, restore) that get you out of trouble.

## Commit and Push

The everyday loop: check what changed, stage it, commit it, push it.

| Command | What it does |
|---|---|
| `git status` | Show status of working directory and staging area |
| `git diff` | Show changes in unstaged modified files |
| `git diff --staged` | Show changes staged for the next commit |
| `git add <file>` | Stage a specific file for commit |
| `git add .` | Stage all new and modified files in the repository |
| `git commit -m "message"` | Commit staged files with an inline commit message |
| `git commit -am "message"` | Stage tracked modified files and commit in one step |
| `git push` | Push committed changes to the upstream remote branch |
| `git push -u origin <branch>` | Push new branch to remote and set up tracking |

## Create a Branch

| Command | What it does |
|---|---|
| `git switch -c feature` | Create and switch to new branch (Git 2.23+) |
| `git checkout -b feature` | Create and switch to new branch (classic syntax) |
| `git branch feature` | Create branch without switching to it |
| `git branch -a` | List all local and remote-tracking branches |
| `git branch -d feature` | Delete local branch safely (refuses if unmerged) |
| `git branch -D feature` | Force delete local branch regardless of merge status |
| `git push origin --delete feature` | Delete branch on remote repository |

## Clone a Repo

| Command | What it does |
|----|----|
| git clone https://github.com/user/repo.git | Clone over HTTPS |
| git clone git@github.com:user/repo.git | Clone over SSH, using your SSH key |
| git clone <url> myfolder | Clone into a folder with a different name |
| git clone --depth 1 <url> | Shallow clone: latest commit only, much faster |
| git clone -b develop <url> | Clone and check out a specific branch |
| git clone --recurse-submodules <url> | Clone including submodules |
| git init | Turn the current folder into a new repo instead |

Permission denied (publickey) on an SSH clone means the server never saw a key it accepts; see [Permission denied (publickey)](https://sshworkbench.com/fix/ssh-permission-denied-publickey).

## Start a New Repo

| Command | What it does |
|---|---|
| `git init` | Initialize a new Git repository in current directory |
| `git init -b main` | Initialize repository with default branch named `main` |
| `git remote add origin <url>` | Attach a remote repository URL to name `origin` |
| `git remote -v` | List all configured remotes and their fetch/push URLs |

The whole sequence, from an empty folder to a pushed repo:

```bash
git init -b main
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:user/repo.git
git push -u origin main
```

## Switch Branches

git switch (Git 2.23+) only switches branches; git checkout also overwrites files, which is exactly how edits get lost by accident.

| Command | What it does |
|---|---|
| `git switch main` | Switch to branch `main` (Git 2.23+) |
| `git switch -` | Switch back to the previously active branch |
| `git checkout main` | Switch to branch `main` (classic syntax) |
| `git checkout -` | Switch back to the previous branch (classic syntax) |
| `git switch --detach <commit>` | Check out commit in detached HEAD state |

## Merge

Merge from the branch that should receive the changes: switch to main, then merge the feature in.

| Command | What it does |
|---|---|
| `git merge feature` | Fast-forward or merge branch `feature` into current branch |
| `git merge --no-ff feature` | Force creation of a merge commit even if fast-forward is possible |
| `git merge --squash feature` | Squash all commits from `feature` into staging without committing |
| `git merge --abort` | Abort a conflicted merge and restore pre-merge state |

## Rebase

Rebase replays your commits on top of another branch, so history stays a straight line. It rewrites commits, so keep it off branches other people pull from. The [git rebase cheat sheet](https://sshworkbench.com/cheatsheets/git-rebase) covers interactive rebase and conflicts step by step.

| Command | What it does |
|----|----|
| git rebase main | Replay this branch's commits on top of main |
| git rebase -i HEAD~3 | Interactive: squash, reword, reorder, or drop the last 3 commits |
| git rebase --continue | Carry on after fixing a conflict |
| git rebase --abort | Put everything back the way it was before the rebase |
| git rebase --skip | Drop the commit that conflicts and move on |
| git pull --rebase origin main | Update from main without a merge commit |

## Stash

| Command | What it does |
|---|---|
| `git stash` | Stash modified tracked files and revert working tree |
| `git stash -u` | Stash modified files including untracked files (`--include-untracked`) |
| `git stash pop` | Apply newest stashed state and remove it from stash list |
| `git stash apply` | Apply newest stashed state without deleting it |
| `git stash list` | List all saved stash entries (`stash@{0}`, etc.) |
| `git stash drop stash@{0}` | Discard a specific stashed change |
| `git stash clear` | Delete all stashes |

## Reset

Reset moves the branch pointer to another commit. The flag decides what happens to your files: --soft keeps changes staged, the default (mixed) keeps them unstaged, --hard deletes them.

| Command | What it does |
|----|----|
| git reset --soft HEAD~1 | Undo the last commit, keep the changes staged |
| git reset HEAD~1 | Undo the last commit, keep the changes unstaged |
| git reset --hard HEAD~1 | Undo the last commit and throw the changes away |
| git reset --hard origin/main | Make the branch match the remote exactly, dropping local work |
| git restore --staged file.txt | Unstage a file without losing the edit |
| git reflog | Every commit HEAD has pointed at, including ones you reset away |
| git reset --hard <hash> | Jump back to a commit found in the reflog |

## Revert

Revert undoes a commit by adding a new commit with the opposite change. History is untouched, which makes it the safe undo for anything already pushed.

| Command | What it does |
|----|----|
| git revert HEAD | Undo the last commit with a new commit |
| git revert <hash> | Undo any specific commit |
| git revert --no-commit <hash1> <hash2> | Undo several commits, then commit once |
| git revert -m 1 <merge-hash> | Revert a merge commit, keeping the main line's side |
| git revert --abort | Stop a revert that hit conflicts |

## Log and History

| Command | What it does |
|----|----|
| git log --oneline | One line per commit |
| git log --oneline --graph --all | Branch graph in the terminal |
| git log -p file.txt | Every change to one file, with the diffs |
| git log --author="ana" | Commits by one person |
| git log --since="2 weeks ago" | Recent commits only |
| git log --grep="login" | Search commit messages |
| git log -S "functionName" | Commits that added or removed a string anywhere in the code |
| git show <hash> | One commit in full: message, author, diff |
| git blame file.txt | Who last touched each line, and in which commit |
| git shortlog -sn | Commit count per author |
| git log main..origin/main | Commits on the remote you have not merged yet |

## Diff

| Command | What it does |
|----|----|
| git diff | Unstaged changes against the last commit |
| git diff --staged | What is about to be committed |
| git diff main..feature | Everything that differs between two branches |
| git diff <hash1> <hash2> | Between any two commits |
| git diff main -- file.txt | One file against another branch |
| git diff main origin/main | Compare a local branch with its remote counterpart |
| git diff --stat | Just file names and change counts |
| git diff --name-only | File names only |
| git diff HEAD~3 | Everything changed in the last 3 commits |

## Delete a Branch

| Command | What it does |
|----|----|
| git branch -d feature | Delete a local branch that is merged |
| git branch -D feature | Delete it even if unmerged (the work is gone with it) |
| git push origin --delete feature | Delete the branch on the remote |
| git fetch --prune | Drop local records of branches already deleted on the remote |
| git branch --merged main | List branches fully merged into main, safe to delete |

## Undo Changes

The undo command depends on where the change lives: unstaged, staged, committed, or pushed. Reset and Revert above handle the committed cases.

| Command | Context | What it does |
|---|---|---|
| `git restore <file>` | Unstaged | Discard unstaged working tree changes (Git 2.23+) |
| `git checkout -- <file>` | Unstaged | Discard unstaged changes (classic syntax) |
| `git restore --staged <file>` | Staged | Unstage file, keeping modifications in working tree |
| `git reset HEAD <file>` | Staged | Unstage file (classic syntax) |
| `git commit --amend` | Committed | Amend the most recent commit (message or staged files) |
| `git revert <commit>` | Committed | Create new commit that undoes changes of specified commit |
| `git reset --soft HEAD~1` | Committed | Undo last commit, keeping changes staged |
| `git reset --hard HEAD~1` | Committed | Undo last commit and destroy all changes in working copy |

## Remotes

SSH remotes (git@github.com:...) authenticate with your SSH key instead of a token; generate one with [ssh-keygen](https://sshworkbench.com/tools/ssh-keygen) and see the [SSH cheat sheet](https://sshworkbench.com/cheatsheets/ssh) for key handling.

| Command | What it does |
|----|----|
| git remote -v | List remotes and their URLs |
| git remote add origin git@github.com:user/repo.git | Connect a local repo to a remote |
| git remote set-url origin <url> | Change the URL, e.g. switch HTTPS to SSH |
| git fetch origin | Download remote commits without touching your files |
| git fetch --all --prune | Update every remote, drop deleted branches |
| git remote add upstream <url> | Track the original repo of a fork |
| git pull upstream main | Bring the original repo's changes into your fork |
| git branch -u origin/main | Set the current branch's upstream |
| git remote remove old | Disconnect a remote |

## Repo Info

| Command | What it does |
|----|----|
| git --version | Which Git version is installed |
| git branch --show-current | The branch you are on (Git 2.22+) |
| git rev-parse --abbrev-ref HEAD | Same, and it works on older Git |
| git rev-parse HEAD | Full hash of the current commit |
| git remote get-url origin | The repo's remote URL |
| git rev-parse --show-toplevel | Absolute path to the repo root |
| git status -sb | Short status, plus branch and ahead/behind counts |
| git config --get user.email | The email this repo commits with |
| git help -a | Every command this install has |

## Cherry-Pick

| Command | What it does |
|---|---|
| `git cherry-pick <commit>` | Apply changes introduced by a specific commit onto current branch |
| `git cherry-pick -n <commit>` | Apply changes to staging without creating a commit |
| `git cherry-pick --continue` | Continue cherry-pick process after resolving conflicts |
| `git cherry-pick --abort` | Cancel cherry-pick operation and return to prior state |

## Tags

| Command | What it does |
|---|---|
| `git tag v1.0.0` | Create a lightweight tag at current commit |
| `git tag -a v1.0.0 -m "Release 1.0.0"` | Create an annotated tag with metadata and message |
| `git tag -l` | List all tags in repository |
| `git push origin v1.0.0` | Push a single tag to remote |
| `git push origin --tags` | Push all local tags to remote |
| `git tag -d v1.0.0` | Delete tag from local repository |
| `git push origin --delete v1.0.0` | Delete tag from remote repository |

## Submodules

| Command | What it does |
|----|----|
| git submodule add <url> libs/tool | Put another repo inside this one at that path |
| git submodule update --init --recursive | Fetch submodule contents after a plain clone |
| git clone --recurse-submodules <url> | Clone and fetch submodules in one step |
| git submodule update --remote | Move submodules to their latest upstream commit |
| git submodule status | Which commit each submodule sits on |
| git submodule foreach git pull | Run a command inside every submodule |
| git rm libs/tool | Remove a submodule (then commit the removal) |

## Config

Set your name and email before the first commit; every commit records them permanently.

| Command | Scope | What it does |
|---|---|---|
| `git config --global user.name "Name"` | User (`~/.gitconfig`) | Set default author name |
| `git config --global user.email "email"` | User (`~/.gitconfig`) | Set default author email |
| `git config --global init.defaultBranch main` | User (`~/.gitconfig`) | Set default initial branch name |
| `git config --global core.editor "vim"` | User (`~/.gitconfig`) | Set default text editor |
| `git config --list --show-origin` | System/Global/Local | Show all active configuration settings and sources |

## Credentials

HTTPS remotes ask for a username and password on every push unless a credential helper stores them. GitHub and GitLab want a personal access token there, not your account password.

| Command | What it does |
|---|---|
| `git config --global credential.helper store` | Store passwords/tokens on disk in plaintext (`~/.git-credentials`) |
| `git config --global credential.helper cache` | Cache credentials in memory temporarily |
| `git config --global credential.helper 'cache --timeout=3600'` | Cache credentials in memory for 1 hour |
| `git credential-cache exit` | Flush cached credentials immediately from memory |

An SSH remote authenticates with your key instead; make one with [ssh-keygen](https://sshworkbench.com/tools/ssh-keygen).

## Gotchas

- Only two commands destroy work with no undo: git reset --hard on uncommitted changes, and git clean. Anything committed survives and git reflog finds it; anything never committed does not.
- Never force push a branch other people pull from. When a rebase makes a force push unavoidable, --force-with-lease at least refuses to overwrite commits you have not seen.
- git pull is git fetch plus git merge. If your history fills up with "Merge branch" commits, set pull.rebase true and it becomes fetch plus rebase.
- Commits with the wrong author email do not fix themselves when you correct the config. git commit --amend --reset-author fixes the last one; older ones need an interactive rebase.
- A "detached HEAD" is not an error, it just means no branch will record new commits. git switch -c rescue keeps them, git switch - walks away.
- git push does not push tags. Release tags need git push origin v1.4.0 or --tags.

## Git FAQ

### How do I go back to a previous commit in Git?

Three different things hide behind that question. To look at an old commit without changing anything, git checkout <hash> puts you in detached HEAD and git switch - brings you back. To move the branch itself back, git reset --hard <hash>, which throws away every local change after that point. To undo a commit that is already pushed, git revert <hash> adds a new commit with the opposite change and leaves history intact. If a reset went too far, git reflog lists every commit HEAD has pointed at for about 90 days, and git reset --hard with that hash restores it.

### Which Git command creates a new branch?

git branch feature creates it but leaves you where you are. git switch -c feature creates it and moves you onto it, which is usually what people want; git checkout -b feature is the older spelling of the same thing. A new branch starts from wherever HEAD is right now, so to branch off main while sitting somewhere else, name the start point: git switch -c hotfix main. Nothing exists on the remote until git push -u origin feature, which also sets the upstream so later pushes need no arguments.

### Which Git command initializes a new repository?

git init, run inside the folder you want tracked. It creates a .git directory and nothing else, so no files are tracked until you add and commit them. Git 2.28 and later accept git init -b main to name the first branch, or set it once with git config --global init.defaultBranch main. Running git init in a folder that already has files is fine, and running it twice does no harm. You never need it after git clone, which initializes the repo for you.

### Which Git commands need an internet connection?

Only the ones that talk to a remote: clone, fetch, pull, push, git remote update, git ls-remote, and submodule updates that fetch. Everything else runs locally, including commit, branch, merge, rebase, log, diff, stash, tag and reset, because your clone holds the full history. That is why you can keep committing on a plane and push the lot when you land. git pull is the one that catches people out offline, since it is fetch plus merge and dies at the fetch.

### What are Git porcelain and plumbing commands?

Porcelain commands are the ones meant for people: status, add, commit, branch, merge, log. Plumbing commands are the low-level ones they are built on, such as hash-object, cat-file, rev-parse, update-ref and rev-list, and they are what scripts should call. The naming trips people up in one place. git status --porcelain does the opposite of what it sounds like: it prints a stable, machine-readable format meant for scripts, and unlike normal status output it will not change between Git versions.

---
Source: https://sshworkbench.com/cheatsheets/git
