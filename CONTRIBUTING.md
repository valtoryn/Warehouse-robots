# Contributing to Valtoryn Warehouse Robotics

Thank you for your interest. The project is in an early research and architecture phase, so most contributions are
currently documentation, research review and architecture feedback.

Project decisions are made by the repository owner. Access, roles and repository permissions are managed only by the
owner; contributions are made through forks and pull requests or through issues.

## Ground rules

- Be accurate before being impressive. Do not describe a feature as implemented when it is only proposed, and do not
  describe something as tested on hardware when it was only simulated.
- Do not invent sources, specifications, benchmarks or results. If something is unknown, say it is unresolved.
- Do not include secrets, credentials, personal data or files you do not have the right to publish.
- Contributions are accepted under the project licence, [Apache License 2.0](LICENSE) (section 5 of the licence
  applies to contributions you intentionally submit).
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Authorship metadata must be truthful: commit under your own identity, and do not fabricate or alter author,
  committer or timestamp information.

## Documentation evidence standard

Technical documents under `docs/` use these inline tags:

| Tag | Meaning |
|---|---|
| **[FACT]** | Established by a cited source that you actually read; followed by a source ID such as `[R03-S07]` |
| **[CALC]** | Derived by a calculation shown in the document, with each input's provenance |
| **[EST]** | Engineering estimate or assumption, with its basis |
| **[REC]** | Recommendation or proposal (engineering judgement, not established fact) |
| **[UNRESOLVED]** | Could not be established; say what would resolve it |

Every research source is recorded in the Sources table of its research document (title, organisation, URL,
publication or revision date, access date, and what it supports). Cite only sources you opened and read. For paywalled
standards, cite only what is publicly visible and say the full text was not inspected.

## Before opening a pull request

```bash
python tools/check_docs.py
```

The checker validates relative links and heading anchors, verifies that every cited source ID has a Sources-table
row, and checks research-document structure. `python tools/check_docs.py --external` additionally checks that source
URLs respond (some sites block automated clients; those are reported as warnings to verify by hand).

## Commits

- One logical, completed change per commit, with a message describing the actual change
  (for example `research: compare robotics simulation frameworks`).
- Do not rewrite history that has been pushed. Correct mistakes with a new commit.

## Safety

This project is not safety-certified. Do not contribute text that implies a component, configuration or software
module is safe for use around people unless a referenced, qualified assessment supports it. See
[SECURITY.md](SECURITY.md).
