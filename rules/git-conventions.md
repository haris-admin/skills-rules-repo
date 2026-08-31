# Git Conventions & Commit Guidelines

Standardized Git workflow, commit messages, and branch naming conventions for repositories.

## Commit Message Format (Conventional Commits)

Format: `<type>(<optional scope>): <description>`

### Types
- `feat`: A new feature or user-facing capability.
- `fix`: A bug fix.
- `docs`: Documentation only changes.
- `style`: Changes that do not affect the meaning of the code (formatting, white-space).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `build`: Changes that affect the build system or external dependencies (npm, pip, cargo).
- `ci`: Changes to CI configuration files and scripts.
- `chore`: Other changes that don't modify src or test files.

### Commit Rules
1. Use the imperative mood in the subject line (e.g. `feat: add user authentication endpoint` NOT `added user authentication`).
2. Do not end the subject line with a period.
3. Keep the subject line under 72 characters.
4. If breaking changes exist, append `!` before the colon (e.g. `feat(api)!: migrate to v2 payload format`) and explain in the commit body.

## Branch Naming Conventions

- `feature/<ticket-or-description>` (e.g. `feature/user-auth-flow`)
- `fix/<ticket-or-description>` (e.g. `fix/null-pointer-session`)
- `refactor/<description>` (e.g. `refactor/clean-database-pool`)
- `chore/<description>` (e.g. `chore/upgrade-dependencies`)
