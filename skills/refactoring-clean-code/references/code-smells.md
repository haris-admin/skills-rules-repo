# Catalog of Common Code Smells & Remedies

1. **Long Method / Function**:
   - *Smell*: Functions exceeding 40-50 lines doing multiple unrelated tasks.
   - *Remedy*: Extract Method/Function; isolate sub-tasks into well-named private functions.

2. **Large Class / God Object**:
   - *Smell*: A class with dozens of fields and responsibilities handling business logic, networking, and UI.
   - *Remedy*: Extract Class; delegate duties to specialized services.

3. **Deeply Nested Conditionals (Arrow Anti-Pattern)**:
   - *Smell*: If/else nesting 4+ levels deep.
   - *Remedy*: Use Guard Clauses (early returns); invert condition checks to exit fast.

4. **Duplicated Code (DRY Violation)**:
   - *Smell*: Identical or near-identical code blocks repeated across modules.
   - *Remedy*: Extract common helper or shared utility function.

5. **Primitive Obsession**:
   - *Smell*: Passing strings/numbers everywhere instead of domain value objects (e.g. raw string for Email, raw number for Money).
   - *Remedy*: Introduce lightweight Value Objects or Branded Types.

6. **Feature Envy**:
   - *Smell*: A method accesses data of another object far more than its own.
   - *Remedy*: Move Method to the class that owns the data.
