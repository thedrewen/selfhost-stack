# Global working rules

## Meta

- These rules apply to all projects. In every project, always copy them into the current project's `CLAUDE.md` ("Working rules" section), then add the project-specific rules (stack, commands, architecture). If the project's `CLAUDE.md` does not exist, create it.

## Git

- `develop` is the main development branch; `main` is for production only.
- One task at a time, on a dedicated branch created from `develop` (`feat/<topic>`, `fix/<topic>`, `chore/<topic>`). Never commit directly to `develop` or `main`.
- Once a task is validated: **squash** merge into `develop` (one commit per task), then delete the branch locally and on the remote.
- Commits follow Conventional Commits (`feat:`, `fix:`, `refactor:`…).

## Process

1. The user gives a task; I create the branch and develop it with tests.
2. The user tests and gives feedback, which I apply on the same branch.
3. Never merge or delete the branch before explicit validation from the user.

## Release

- **Fast-forward** merge of `develop` into `main` (`git merge --ff-only develop`), then a semver tag `vX.Y.Z` on that `main` commit. A tag never points to `develop`.
- Update the project version (`package.json` + `package-lock.json`, `Cargo.toml`…) to match the tag (`X.Y.Z` without `v`).
- Strict semver: `PATCH` for fixes, `MINOR` for backward-compatible features, `MAJOR` for breaking changes.
- Never push, tag or merge without an explicit request from the user.

## Quality

- Add tests with new code; update existing ones when behavior changes.
- Run the project checks before considering a task done.
- Readable code: small functions, explicit names, no clever tricks; comment the "why", not the "what".
- Validate all user input on the server side.
- No new dependency unless necessary.

## Behavior

- Do not hesitate to push back if a request looks risky or inconsistent with the architecture: say so and propose an alternative instead of blindly complying.
- For visual work, do not set up anything complex (headless browsers, system libs): reason from the code, then ask for a screenshot or a validation.
- Keep a `PLAN.md` up to date (what remains to be done, with enough context to resume): tick/remove what is done, add new tasks.

## Language

- Everything written in the repository is in English: technical identifiers, code comments, commit messages, `CLAUDE.md`, `PLAN.md`, READMEs, plans and any other docs.
- Text displayed to the application's end users is in the user's current language (i18n, no hard-coded language).
- Conversation with the user is in the user's native language.
