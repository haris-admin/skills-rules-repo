# TypeScript Style Guide & Standards

Best practices and rules for modern, type-safe TypeScript codebases.

## Core Directives

1. **Strict Type Safety**:
   - Enable `strict: true` in `tsconfig.json`.
   - Disallow `any`. Use `unknown` with type guards or `never` for exhaustive type checking.
   - Prefer type inference where obvious, but explicitly type exported function signatures and interfaces.

2. **Types vs Interfaces**:
   - Use `interface` for public API contracts and extensible object definitions.
   - Use `type` for unions, intersections, mapped types, and utility transformations.

3. **Immutability & Const**:
   - Prefer `const` over `let`. Avoid `var` entirely.
   - Use `readonly` arrays/properties where data should not be mutated in place.

4. **Async / Await**:
   - Prefer `async`/`await` over raw `.then()/.catch()` promise chaining.
   - Always handle promise rejections.

5. **Modern ECMAScript**:
   - Use optional chaining (`?.`) and nullish coalescing (`??`) instead of verbose ternary checks.
   - Use ES modules (`import`/`export`) over CommonJS (`require`).
