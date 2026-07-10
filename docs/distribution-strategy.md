# Distribution Strategy

Three channels to make fuzzybee installable and discoverable.

## Channel 1: GitHub (primary)

**Repo**: `github.com/heyfuzzybee/fuzzybee`
**Install**: `git clone` or download release tarball.

## Channel 2: npm

```bash
npm install -g @heyfuzzybee/fuzzybee
fuzzybee health
```

Published via GitHub Actions on tag push (see `.github/workflows/release.yml`).

## Channel 3: Skills Hubs

| Platform | How |
|----------|-----|
| [SkillsMP](https://skillsmp.com) | GitHub repo → auto-indexed |
| [SkillsLLM](https://skillsllm.com) | Submit PR to registry |
| [LobeHub](https://lobehub.com/skills) | Community submission |

These are cross-tool compatible — Claude Code, Codex CLI, and Kimi Code CLI all read the same `SKILL.md` format.

## Channel 4: Kimi Cloud (Agent Mode)

Upload via "Document to Skill":
1. kimi.com → Agent Mode → Skills panel → "+" → "Document to Skill"
2. Upload `SKILL.md` + `references/skill-integration.md`
3. Describe: "Recursive verify skill with evidence gates for software execution"

Currently personal-use only (no public marketplace yet).

## Release automation

- Tag push → `release.yml` creates GitHub Release + npm publish
- `VERSION` file + `CHANGELOG.md` drive versioning
