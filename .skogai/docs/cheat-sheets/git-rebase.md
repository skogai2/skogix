# Git Rebase Cheat Sheet

git rebase replays your commits on top of another branch, which keeps a feature branch current and its history clean. This sheet covers the commands with short worked examples: interactive rebase, squash and fixup, conflicts, --onto, and how to undo a rebase.

Last updated September 11, 2026

On this page

- [Rebase onto main or master](#rebase-onto-main-or-master)
- [Rebase After a Pull](#rebase-after-a-pull)
- [Interactive Rebase](#interactive-rebase)
- [Rebase Editor](#rebase-editor)
- [Fixup, Squash & Reword](#fixup-squash-reword)
- [Squash Commits](#squash-commits)
- [With Conflicts](#with-conflicts)
- [Abort, Continue, Skip](#abort-continue-skip)
- [Ours vs Theirs](#ours-vs-theirs)
- [Rebase --onto](#rebase---onto)
- [Edit a Commit](#edit-a-commit)
- [Exec](#exec)
- [Rebase vs Merge](#rebase-vs-merge)
- [Rebase on GitHub](#rebase-on-github)
- [Cherry-pick vs Rebase](#cherry-pick-vs-rebase)
- [Undo a Rebase](#undo-a-rebase)
- [Gotchas](#gotchas)

## Rebase onto main or master

Run rebase from the branch you want to move. It replays that branch's commits on top of the target.

| Command | What it does |
|----|----|
| git rebase main | Replay the current branch's commits on top of main |
| git rebase master | Same, on repos whose default branch is master |
| git fetch origin | Update the remote-tracking branches first |
| git rebase origin/main | Rebase onto the remote's latest main, no local checkout of main needed |
| git rebase main feature | Check out feature, then rebase it onto main |
| git pull --rebase | Pull, replaying your local commits on top instead of merging |
| git config --global pull.rebase true | Make every pull a rebase by default |
| git rebase --autostash main | Stash uncommitted changes first, restore them after |
| git rebase --update-refs main | Move stacked branches along with this one (Git 2.38+) |
| git push --force-with-lease | Push the rewritten branch; refuses if the remote grew new commits |
| git rebase --abort | Stop and put the branch back exactly as it was |

The full update loop, step by step:

```
git switch feature
git fetch origin
git rebase origin/main        # if it stops on a conflict: fix, git add, git rebase --continue
git push --force-with-lease   # the commits were rewritten, so a plain push is rejected
```

Copy

## Rebase After a Pull

When your branch and its remote have both moved, Git stops with "You have divergent branches and need to specify how to reconcile them". Rebasing puts your local commits back on top instead of making a merge commit.

[TABLE]

```
# hint: You have divergent branches and need to specify how to reconcile them.
git config --global pull.rebase true   # set it once
git pull                               # now rebases instead of merging
```

Copy

After someone squash-merges your pull request, the branch's old commits no longer match anything upstream, so a plain rebase replays them as duplicates. Move only the commits you added since then:

```
git rebase --onto origin/main <last-commit-that-got-squashed> feature
```

Copy

## Interactive Rebase

git rebase -i opens a todo list of commits, oldest first. Change the word in front of a commit to change what happens to it; reorder the lines to reorder the commits.

| Command | What it does |
|----|----|
| git rebase -i HEAD~5 | Edit the last 5 commits |
| git rebase -i main | Edit every commit on this branch that main does not have |
| git rebase -i abc1234^ | Edit from commit abc1234 (included) up to HEAD |
| git rebase -i --root | Edit every commit on the branch, including the very first one |
| git rebase -i --rebase-merges main | Replay the branch's merge commits instead of flattening them |
| git rebase --edit-todo | Reopen the todo list mid-rebase |
| git log --oneline main.. | Preview which commits the todo will contain |

[TABLE]

A typical cleanup todo before opening a pull request:

```
pick a1b2c3d Add login endpoint
fixup e4f5a6b fix typo
reword 7c8d9e0 Add rate limiting
drop f0a1b2c WIP
```

Copy

## Rebase Editor

The todo list opens in your sequence editor, which defaults to core.editor and then to vim. Saving an empty todo, or quitting with an error, cancels the rebase.

| Command | What it does |
|----|----|
| git config --global core.editor "code --wait" | Use VS Code for commit messages and the todo list |
| git config --global sequence.editor "code --wait" | Use a different editor for the todo list only |
| git config --global core.editor "nano" | Swap vim for nano everywhere |
| GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash main | Accept the todo as generated, with no editor at all |
| :wq | In vim: save the todo and start the rebase |
| :cq | In vim: quit with an error, which cancels the rebase |

--wait is not optional for a GUI editor. Without it the command returns immediately, Git sees an unchanged todo, and the rebase runs before you have edited anything.

## Fixup, Squash & Reword

Mark a commit as a fix the moment you make it, and --autosquash files it under its target in the todo for you.

[TABLE]

```
# Fix a typo that lives three commits back
git add src/auth.js
git commit --fixup=abc1234
git rebase -i --autosquash main   # the fixup line is already in place; save and quit
```

Copy

## Squash Commits

To squash the last N commits into one, rebase over them interactively and keep only the first pick.

[TABLE]

```
git rebase -i HEAD~3
```

Copy

```
pick a1b2c3d Add password reset
fixup e4f5a6b fix failing test
fixup 7c8d9e0 review feedback
```

Copy

The reset route gets the same result without touching the rebase machinery:

```
git reset --soft HEAD~3
git commit -m "Add password reset"
```

Copy

## With Conflicts

A rebase replays commits one at a time, so it can stop on any of them. Fix the files, stage them, continue. Never run git commit yourself mid-rebase; --continue commits for you.

| Command | What it does |
|----|----|
| git status | List the conflicted files ("both modified") |
| git diff --name-only --diff-filter=U | Just the paths still unresolved |
| git diff | Show the remaining conflict markers |
| git add file.js | Mark a fixed file as resolved |
| git rebase --continue | Commit the resolution and replay the next commit |
| git mergetool | Walk the conflicts in your configured merge tool |
| git rebase --show-current-patch | Show the commit the rebase is stuck on |
| git checkout --conflict=diff3 file.js | Redo the markers with the common ancestor shown between them |

The whole loop:

```
git rebase main
# CONFLICT (content): Merge conflict in src/app.js
vim src/app.js                # remove the <<<<<<< ======= >>>>>>> markers
git add src/app.js
git rebase --continue         # repeat until "Successfully rebased"
```

Copy

## Abort, Continue, Skip

--continue after staging fixes, --skip when the commit is already upstream, --abort when the whole thing went sideways.

[TABLE]

If --continue says there is nothing to commit, the resolution made the commit empty, usually because the change already exists upstream. That is what --skip is for.

## Ours vs Theirs

During a rebase, ours and theirs are the reverse of what most people expect. Rebase checks out the branch you are rebasing onto and replays your commits against it, so --ours is that base branch (main) and --theirs is your own commit.

| Command | What it does |
|----|----|
| git checkout --ours file.js | Take the version from the branch you are rebasing onto |
| git checkout --theirs file.js | Take your own branch's version |
| git checkout --theirs -- . | Accept your version of every file conflicted at this stop |
| git checkout --ours -- . | Accept the base branch's version of every conflicted file |
| git rebase -X ours main | Auto-resolve every conflict in favor of main |
| git rebase -X theirs main | Auto-resolve every conflict in favor of your commits |

Editors rename the same two sides. In VS Code's conflict view during a rebase, "Current Change" is the base branch and "Incoming Change" is the commit of yours being replayed.

After a --ours/--theirs checkout, the file still needs git add and git rebase --continue.

```
# Keep your version of the lock file for every conflict in this rebase
git rebase -X theirs main

# Or decide per file, mid-conflict
git checkout --theirs -- package-lock.json
git add package-lock.json
git rebase --continue
```

Copy

## Rebase --onto

--onto moves a range of commits to a new base: git rebase --onto \<new-base\> \<old-base\> \<branch\>. Read it as "take the commits after old-base up to branch, and replay them on new-base".

| Command | What it does |
|----|----|
| git rebase --onto main old-base feature | Move feature's own commits from old-base onto main |
| git rebase --onto main featureA featureB | Re-parent featureB from featureA onto main |
| git rebase --onto origin/main origin/develop feature | Move a branch started from the wrong base |
| git rebase --onto HEAD~4 HEAD~2 | Drop the two commits between HEAD~~4 and HEAD~~2 |

```
# You branched featureB off featureA, and featureA just merged.
# Replay only featureB's own commits onto main:
git rebase --onto main featureA featureB
```

Copy

## Edit a Commit

Mark a commit edit in the todo and the rebase stops right after applying it, with the commit as HEAD.

[TABLE]

```
# Change a file inside an older commit
git rebase -i abc1234^        # change "pick abc1234" to "edit abc1234"
vim src/config.js
git add src/config.js
git commit --amend --no-edit
git rebase --continue
```

Copy

To split it instead: git reset HEAD^ at the stop, then stage and commit the pieces separately before --continue.

## Exec

exec runs a command after a commit is applied and stops the rebase if it fails, which pinpoints the commit that broke things.

| Command | What it does |
|----|----|
| git rebase -x "npm test" main | Run the tests after replaying each commit |
| x npm test | The same as a hand-placed todo line |
| git rebase -i -x "make" HEAD~10 | Combine a test run with normal todo editing |

```
# Find the commit that broke the tests while rebasing a branch
git rebase -x "npm test" main
# stops at the first failing commit: fix it, git commit --amend, git rebase --continue
```

Copy

## Rebase vs Merge

Both integrate one branch into another; they leave different history behind.

[TABLE]

Rule of thumb: rebase your own feature branch to keep it current, merge to land finished work into a branch other people use. The [git cheat sheet](https://sshworkbench.com/cheatsheets/git) covers the merge side in full.

## Rebase on GitHub

GitHub's "Rebase and merge" button replays a pull request's commits onto the base branch with no merge commit, rewriting them with new SHAs. Both it and the "Update branch" dropdown need a clean replay; on a conflict you do it locally and push.

| Command | What it does |
|----|----|
| git fetch origin | Pick up the base branch before updating the PR |
| git rebase origin/main | The local equivalent of GitHub's "Update with rebase" |
| git push --force-with-lease | Update the open pull request with the rebased commits |
| gh pr checkout 123 | Check out someone else's PR branch to rebase it |
| git rebase -i origin/main | Tidy the PR's commits before asking for review |

```
# "This branch is out-of-date with the base branch" on a PR with conflicts
git fetch origin
git rebase origin/main        # fix, git add, git rebase --continue
git push --force-with-lease   # the PR updates in place, review comments stay
```

Copy

Force-pushing a rebased branch keeps the pull request and its conversation; only the diffs of individual commits become unreachable, so old review comments may show as outdated.

## Cherry-pick vs Rebase

cherry-pick copies commits and leaves the originals alone, so the change exists in two places. Rebase moves a range onto a new base and abandons the originals. See the [git cheat sheet](https://sshworkbench.com/cheatsheets/git) for the rest of cherry-pick.

| Command | What it does |
|----|----|
| git cherry-pick abc1234 | Copy one commit onto the current branch |
| git cherry-pick abc1234^..def5678 | Copy a range of commits, both ends included |
| git cherry-pick -n abc1234 | Copy the changes but stop before committing |
| git cherry-pick --continue | Same conflict loop as a rebase |
| git rebase --onto main old-base feature | Move a whole range instead of copying it commit by commit |

```
# One fix belongs on the release branch too: copy it
git switch release-2.1
git cherry-pick abc1234

# The whole branch started from the wrong base: move it
git rebase --onto main old-base feature
```

Copy

## Undo a Rebase

The old commits are not gone after a rebase; the reflog still points at them for about 90 days.

| Command | What it does |
|----|----|
| git rebase --abort | Mid-rebase: stop and restore everything |
| git reflog | Every position HEAD has held, rebased-away commits included |
| git reset --hard HEAD@{7} | Move the branch back to reflog entry 7 |
| git reset --hard ORIG_HEAD | Jump straight back, if nothing has overwritten ORIG_HEAD since |
| git reflog show feature | The same history, scoped to one branch |

```
git reflog
# a1b2c3d HEAD@{0}: rebase (finish): returning to refs/heads/feature
# ...
# 9f8e7d6 HEAD@{7}: commit: the tip before the rebase started
git reset --hard HEAD@{7}
```

Copy

Pick the entry just below the first rebase (start) line: that was the branch tip before anything was rewritten.

## Gotchas

- Never rebase commits other people have already pulled. Rewriting a shared branch forces everyone else into a painful recovery; merge on shared branches, rebase on your own.
- After any rebase, a plain
  git push
  is rejected. Use
  git push --force-with-lease
  , never bare
  --force
  : with-lease fails safely if a teammate pushed in the meantime.
- Ours and theirs swap meaning during a rebase.
  --ours
  is the branch you are rebasing onto,
  --theirs
  is your own commit.
  -X ours
  and
  -X theirs
  swap the same way.
- Do not
  git commit
  after fixing a conflict;
  git add
  then
  git rebase --continue
  is the whole move. Committing by hand mid-rebase leads to duplicated or empty commits.
- Rebase refuses to start over uncommitted changes. Commit them, stash them, or pass
  --autostash
  (or set
  rebase.autostash true
  once).

### Your servers deserve the same care as your repo

SSH Workbench turns every server into a dashboard over plain SSH: deploys, services, logs, files, and cron, with a real terminal when you want one.

[Try free for 7 days](https://sshworkbench.com/#install)

## git rebase FAQ

### Is git rebase dangerous?

It is safe on commits only you have, and risky on commits other people have already pulled. Rebase does not edit commits, it makes new ones with new hashes, so anyone who had the old ones ends up with both copies and a messy recovery. On your own branch the worst case is recoverable: git rebase --abort restores everything mid-rebase, and after it finishes git reflog still lists the old tip for about 90 days, so git reset --hard HEAD@{n} puts it back. The one habit that matters is pushing with git push --force-with-lease instead of --force, since with-lease refuses if a teammate pushed while you were rebasing.

### How do you properly use git rebase?

The normal loop is git fetch origin, then git rebase origin/main from your feature branch, then git push --force-with-lease. Rebase before you open a pull request and before you merge, not in the middle of a review that people are commenting on. Keep the work in small commits while you build, then clean them up in one git rebase -i pass at the end rather than amending constantly. Two settings make it smoother: rebase.autosquash true so git commit --fixup lines sort themselves, and rebase.autostash true so an uncommitted file does not block the start.

### Does git rebase rewrite history?

Yes. Rebase does not move your commits, it builds new ones with the same changes and a new parent, so every replayed commit gets a new hash even when its content is identical. The author name and author date carry over, but the committer date is set to now, which is why a rebased branch can look freshly written in some tools; git rebase --committer-date-is-author-date keeps the original timestamps. Because the hashes changed, the remote no longer recognises your branch as a fast-forward, so the push needs --force-with-lease. Anything that referenced the old hashes, such as a link in an issue, now points at commits only the reflog can still reach.

### Will git rebase overwrite my local changes?

Committed work is not overwritten. Rebase refuses to start with a dirty tree, so uncommitted edits are the real risk: you get "cannot rebase: You have unstaged changes" and nothing happens until you commit, stash, or pass --autostash. Set rebase.autostash true once and Git stashes and restores around every rebase for you. Conflicts do not lose anything either, since the rebase pauses and waits for you. The one way to actually drop work is resolving a conflict by taking one side wholesale, with git checkout --ours or -X ours, which silently discards the other side.

### In a git rebase conflict, which side is theirs?

Theirs is your own commit, which catches almost everyone out. Rebase checks out the branch you are rebasing onto and replays your commits against it, so from Git's point of view that base branch is ours and each commit of yours arriving on top is theirs. Editors make it worse by using different words: in VS Code, "Current Change" is the base branch and "Incoming Change" is your commit. To keep your own version of every file conflicted at this stop, run git checkout --theirs -- . then git add -A and git rebase --continue; to take that side for the whole rebase, restart it as git rebase -X theirs main. Save that for lock files and generated output, not source.

---
Källa: https://sshworkbench.com/cheatsheets/git-rebase
