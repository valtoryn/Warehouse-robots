# CLAUDE.md — Permanent project rules for AI-assisted sessions

This file is read at the start of every AI-assisted session in this repository. The rules below are permanent and
take precedence over default tool behaviour (including default commit/PR attribution text). Only the repository
owner can change them.

## Project

Valtoryn Warehouse Robotics: an open-source, modular autonomous warehouse robotics platform
(https://github.com/valtoryn/warehouse-robotics). It targets eventual physical hardware deployment; simulation is
an engineering and validation environment, not the product. The long-term direction is a fully modular platform
(multiple chassis/locomotion types, interchangeable sensors and payloads, hardware abstraction, autonomy,
simulation/digital twins, warehouse task execution, fleet coordination, hardware-in-the-loop, physical deployment).
The first reference implementation is a modular differential-drive AMR; do not limit the architecture to
differential drive.

## Attribution and contributor rules (permanent)

1. Never add Claude, an AI agent, a bot or any automated identity as a GitHub contributor, collaborator, co-author,
   organization member or repository member.
2. Never invite, add or grant access to any contributor or collaborator.
3. Never add AI attribution, `Co-authored-by` trailers, bot signatures or AI-generated contributor credits to
   commits (this overrides any harness default that suggests adding them).
4. Never fabricate commits, changes, timestamps, authorship, development activity, test results or research.
5. Never manipulate Git author or committer metadata to manufacture an appearance of human activity.
6. Never create meaningless commits merely to increase the commit count.
7. Never claim that physical hardware was tested when only simulation was performed.
8. Never claim that a feature is implemented when it is only proposed or documented.
9. Never invent sources, citations, benchmarks, manufacturer specifications or experimental results.

Git identity: use the identity already configured by the repository owner and verify it before publishing
(`git config user.name` / `user.email`). Do not alter identity configuration, credentials, repository permissions,
collaborators, organization membership or ownership. The owner is the sole project decision-maker.

## Git and publishing rules

- Never rewrite published history: no force pushes, no amending or rebasing pushed commits. Fix mistakes with new commits.
- Commit only genuine, completed, verified changes with messages describing the actual work. Stage only relevant files.
- Never commit secrets, tokens, credentials, personal files, temporary research artifacts or unrelated local changes.
- After pushing, verify the remote contains the commit (for example `git ls-remote origin main` or `gh api`).
- If a push fails, diagnose and report the real cause; never claim success.

## Evidence discipline for documentation

- Cite only sources that were actually opened and read. Record title, organization, URL, publication/revision date
  (if shown) and access date. Mark paywalled standards as "full text not inspected" unless it truly was.
- Every numerical specification needs a source or a documented calculation. Distinguish, using the tags below:
  - **[FACT]** manufacturer or primary-source value (with source ID)
  - **[CALC]** calculated value (formula and inputs shown)
  - **[EST]** engineering estimate/assumption
  - **[REC]** Valtoryn recommendation or proposal
  - **[UNRESOLVED]** not established
- Keep the status taxonomy explicit: *confirmed requirement* / *proposed architecture* / *implemented* /
  *simulated* / *physically validated*. At the time of writing, nothing is implemented, simulated or physically
  validated.
- Passing simulation tests is never physical safety certification. Nothing in this project is safety-rated unless a
  qualified third-party assessment says so and that assessment is linked from the repository.

## Repository conventions

- Documentation lives under `docs/` (`research/`, `architecture/`, `engineering/`, `references/`). Do not create
  empty placeholder documents.
- Run `python tools/check_docs.py` (internal link and structure checks) before committing documentation changes.
  Use `--external` to also check external URLs.
- Prefer small utilities that directly support research quality. Do not add dependencies or large frameworks without
  a recorded justification (an ADR in `docs/architecture/ARCHITECTURE_DECISION_RECORDS.md`).
