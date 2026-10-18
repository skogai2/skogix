# local-agents

local llms (8-16gb gpus, ~5 workstations) working 24/7 through a prompt-queue.

## bar

a use-case qualifies when the output is cheap to check and a bad result is no worse than `.`.

proven: llama3.2 writing commit messages via `wt` (see `.config/wt.toml`).

## use-cases

| use-case | input | output | wired |
|---|---|---|---|
| commit messages | staged diff | subject line | yes |
| branch summaries | branch diff | one line in `wt list` | `list.summary = true` |
| journal turn titles | journal entry | heading or tag | no |
| `.` / `WIP` backfill | old commit diff | suggested subject, as notes | no |
| type check hints | file + `dash-skogai/type/*.md` | "looks like a `<type>`" | no |

## queue

```
job    = { id, prompt, model, inputs: [path], out: path }
queue  : dir of job files, append-only, in git
worker : gpu -> job -> result   # pull, run, write out, commit
```
