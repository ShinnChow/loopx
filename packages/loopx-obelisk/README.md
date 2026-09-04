# loopx-obelisk

`loopx-obelisk` is an optional advisory context provider for LoopX
`decision-context`. It lets an explicitly configured Decision Context profile
search one historical Codex task selected by a LoopX-normalized host-session
scope.

The provider does not parse Codex deep links. LoopX Core parses the link once
and returns `context_scope_ref=host-session:codex:<thread-id>` from:

```bash
loopx --format json resolve-agent-thread \
  --thread-link 'codex://threads/<thread-id>'
```

Copy that normalized scope into an ignored, owner-local Decision Context
profile. The context-provider section is:

```json
{
  "provider": "extension",
  "namespace": "peer-session",
  "scope_ref": "host-session:codex:<thread-id>",
  "max_results": 4,
  "timeout_seconds": 10,
  "config": {
    "extension_id": "loopx-obelisk"
  }
}
```

## Install and activate

Obelisk is a separate AGPL-3.0 application. This Apache-2.0 provider does not
copy its implementation or read its SQLite schema; it invokes the installed
public CLI through the `obelisk --version` and `obelisk --query` boundary.
Install Obelisk separately, then install and activate this package in the same
Python environment as LoopX:

```bash
npm install --global @obelisk-apps/cli
python3 -m pip install packages/loopx-obelisk
loopx extension install \
  --manifest packages/loopx-obelisk/extension.toml \
  --execute --format json
loopx extension doctor loopx-obelisk --execute --format json
```

If the project uses a non-default LoopX runtime root, pass the same global
`--runtime-root <path>` option to the extension lifecycle commands and the
Decision Context command. The provider is resolved from that exact lifecycle
state; it is never discovered from an unrelated default runtime.

Run a read-only Decision Context preview with the owner-local profile:

```bash
loopx decision-context prepare-evidence \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --profile <ignored-private-profile.json> \
  --decision-id <decision-id> \
  --format json
```

Disable the provider, remove the owner-local profile binding, and uninstall its
Python distribution when it is no longer needed:

```bash
loopx extension disable loopx-obelisk --execute --format json
python3 -m pip uninstall loopx-obelisk
```

LoopX v0 intentionally has no extension-state deletion command. The disabled
registration remains as non-ready lifecycle history; it is not callable.

## Authority and privacy boundary

The deep link is a non-authoritative locator. Enabling the extension grants no
Goal, Agent, claim, lease, permission, workspace, lifecycle, amendment, or
write authority. Retrieved text remains in-process advisory evidence. The
public Decision Context packet retains only a compact summary, score, and
hashed provider reference; it does not contain raw transcript text or Obelisk
resource ids. A fact becomes durable only through an existing LoopX owner such
as Todo evidence, the Agent evidence log, registered material, or a governed
amendment.

The provider never invokes `obelisk --build` or `obelisk --attune`. Obelisk may
refresh its provider-owned local search index as part of `--query`; the query
is read-only with respect to the source task and LoopX state. Failure,
disablement, ambiguous provider selection, or stale
doctor state fails open inside Decision Context and does not block unrelated
authority sources.

See [CONTRACT.md](CONTRACT.md) for the wire contract and validation commands.
