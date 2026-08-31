# Conventional Commits Reference

The Conventional Commits specification is a lightweight convention on top of commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types
- `feat`: Commits that add a new feature or capability.
- `fix`: Commits that fix a bug.
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `docs`: Documentation updates only.
- `perf`: Performance improvements.
- `test`: Adding or correcting tests.
- `style`: Formatting, missing semi colons, white-space changes.
- `build`: Changes to build systems, bundlers, package dependencies.
- `ci`: Changes to CI/CD workflows and scripts.
- `chore`: Maintenance tasks and configuration updates.

## Examples
- `feat(auth): support OAuth2 PKCE login flow`
- `fix(parser): handle empty markdown tables without throwing exception`
- `refactor(db): extract connection pooling into separate module`
- `docs(readme): add installation script usage examples`
