# Python Style Guide & Best Practices

Standards and conventions for writing clean, Pythonic, and type-hinted code.

## Core Directives

1. **PEP 8 and Formatting**:
   - Follow PEP 8 guidelines for formatting (line length <= 88/100 characters).
   - Use automated formatters and linters (`ruff` or `black` + `flake8`).

2. **Type Annotations (PEP 484 / PEP 585 / PEP 604)**:
   - Type hint all public function signatures, parameters, and return types.
   - Use built-in generics (e.g. `list[str]`, `dict[str, int]`, `str | None`) rather than legacy `typing` constructs where Python 3.10+ is supported.

3. **Virtual Environments & Dependencies**:
   - Always run inside a virtual environment (`venv`, `poetry`, or `uv`).
   - Explicitly declare pinned dependencies in `pyproject.toml` or `requirements.txt`.

4. **Context Managers**:
   - Always use `with` statements for managing files, sockets, database connections, and locks to guarantee resource cleanup.

5. **Docstrings & Comments**:
   - Use Google-style or NumPy-style docstrings on all public modules, classes, and functions.
   - Document arguments (`Args:`), return values (`Returns:`), and potential exceptions (`Raises:`).
