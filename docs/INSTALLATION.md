# Installation and migration

## Requirements

Node.js 22+ and npm/npx. GitHub installs require Git and permission to read the repository. No account token is collected by the CLI.

The installed instruction package has no npm runtime dependencies. Browser audits are optional and require separately available Playwright/Chromium.

## GitHub command

From the target project, run:

```sh
npx --yes github:Crelami-Dev/atlas-skill
```

A terminal menu asks you to choose Agents (`.agents/skills/atlas`) or Claude Code (`.claude/skills/atlas`). Enter 1 or 2. No global installation occurs. Agents is a shared folder convention for compatible tools, not a promise that every AI tool discovers it. Use Ctrl+C to cancel before any writes. For automation pass `install --agent agents` or `install --agent claude`; without a target, a noninteractive run exits with guidance instead of guessing. This uses GitHub, not an npm registry publication. For a private repository, authenticate Git using your existing trusted workflow first. Do not paste credentials into command URLs.

Use a reviewed commit fragment (#<commit-sha>) for reproducibility. Re-run using a newer reviewed source revision when updating; the CLI installs the package npx actually downloaded, not a separately fetched remote payload.

## Commands

- no command: opens the interactive installer.
- install: installs into an empty, dedicated skill folder.
- update: replaces a managed Atlas installation after backing up the entire old folder.
- doctor: checks recorded file integrity and reports installed/installer versions.
- list: shows bundled module names and default project paths.
- --version: prints the installer/package version.
- --dry-run: with install/update validates source and prints the planned target without writing it.
- --dir PATH: explicitly chooses a different skill directory.
- --agent agents|claude: chooses the project-local target without a menu. codex and antigravity remain aliases for agents.
- update and doctor also show the target menu when no --agent or --dir is supplied.

Example using a local clone from a different project directory:

```sh
node /path/to/atlas-skill/bin/atlas-skill.mjs install --agent claude --dry-run
node /path/to/atlas-skill/bin/atlas-skill.mjs install --agent claude
```

Do not install the source checkout recursively into itself. Use a separate target project or explicit dedicated directory.

## Agent paths

Claude Code project skills use .claude/skills/<name>. The Agents option uses .agents/skills/<name> for tools supporting that convention, including Codex and the current shared Antigravity default. These destinations are project-local. Other AI tools may require their own paths; use --dir and check their discovery rules.

Antigravity has multiple surfaces and supports legacy paths. Use --dir if your environment requires another location rather than assuming every version has identical discovery rules.

Primary references checked during release:
- [Claude skills](https://code.claude.com/docs/en/skills)
- [Antigravity skills](https://antigravity.google/docs/skills)

The CLI does not change agent configuration or grant tool permissions. A restart/reload may be needed. Explicitly ask the agent to read and use Atlas after installation.

## Updating managed installations

Update recognizes its own .atlas-install.json record. Source validation completes before replacement.

If bundled files are unchanged, update reports current. Otherwise it stages the new package and renames the full previous directory into .atlas-skill-backups in the working project. Modified files are identified in the output; extra local files are preserved in the complete backup.

Backups are outside skill discovery folders. Keep them until you have checked the new installation. The installer never recursively deletes old content.

If the final rename fails, it attempts to restore the old installation. Any leftover staging path is reported for inspection.

## Legacy or manually installed Atlas

An unmanaged folder is not overwritten, even if its name is atlas.

1. Inspect the existing location and any local modifications.
2. Keep the old copy as a backup outside the agent's discovery folders.
3. Install into a new empty dedicated destination.
4. Verify with doctor and the installed package validator.
5. Reload the agent and check which copy it discovers.

Do not leave two discoverable Atlas copies and assume the newest will win.

## Recovery

The update output gives the exact backup path. To roll back, stop using the new skill, keep its copy separately if needed, and restore the backup to the original skill location using normal filesystem tools.

Doctor proves file integrity against its install record. It does not certify the content, current web research or whether an agent used it.

## Deliberate limits

No automatic npm publishing, global configuration edits, remote telemetry, arbitrary package installation, symlink/junction installation, uninstall command or force-overwrite option.

Use --dir for explicit nonstandard locations. Project roots, drive roots, the installer source and unsafe linked paths are rejected.
