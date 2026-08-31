# Git Workflow & Version Control Hygiene

Guidelines for clean commit histories, branching strategies, and repository cleanliness.

## Git Standards

1. **Conventional Commits**:
   - Write clear, standardized commit messages:
     - `feat: add user profile editing endpoint`
     - `fix: resolve race condition in token refresh`
     - `docs: update API setup instructions in README`
     - `refactor: extract date formatting utility`
     - `test: add unit tests for discount calculator`

2. **Branching Strategy**:
   - Branch off `main` or `develop` with descriptive names: `feat/<name>`, `fix/<issue>`, `chore/<task>`.
   - Keep branches short-lived and pull updates frequently to minimize merge conflicts.

3. **Clean Commit History**:
   - Avoid committing build artifacts, temporary test files, OS metadata (`.DS_Store`), or logs.
   - Review `git status` and `git diff` before staging and committing.
