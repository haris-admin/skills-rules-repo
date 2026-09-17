# CRAP Score Analysis (Change Risk Anti-Patterns)

Calculate and reduce Change Risk Anti-Patterns (CRAP) by measuring cyclomatic complexity against automated test coverage across Python and JavaScript/TypeScript codebases. Use when auditing monolithic components, deciding whether methods need strangler-fig refactoring, or reviewing change risk.

## 1. Formula & Theoretical Foundation (Savoia / Evans, 2007)

$$\text{CRAP}(m) = \text{comp}(m)^2 \times (1 - \text{cov}(m))^3 + \text{comp}(m)$$

Where:
- `comp(m)` is the McCabe Cyclomatic Complexity (decision points: `if`, `else if`, `for`, `while`, `catch`, `&&`, `||`, `? :`).
- `cov(m)` is the automated test coverage of method `m` ($0.0$ to $1.0$).

### Risk Classification
| CRAP Score | Risk Category | Action Required |
|:---|:---|:---|
| **$\le 8$** | Low Risk | Well-tested, clean, modular code. |
| **$\le 15$** | Acceptable | Standard production logic. |
| **$\le 25$** | Moderate Risk | Consider path tests or extracting helpers. |
| **$> 25$** | High Risk | Refactor before modifying; add regression tests. |
| **$> 30$** | Critical CRAP | **Violates Clean Code Standard.** Even 100% coverage cannot make high CC safe. |

---

## 2. Multi-Ecosystem Scanners

### A. JavaScript / TypeScript AST Scanner (Node, React, Next.js)
In frontend and Node.js repositories (e.g. Simplifii-OS), use the Babel AST parser:
```bash
# Scan full repository
node scripts/crap_score.js

# Scan specific file or component
node scripts/crap_score.js src/frontend/CanvasScreen.jsx
```

### B. Python AST Scanner (FastAPI, Django)
In backend Python repositories, use the Python AST parser:
```bash
# Pessimistic 0% coverage audit (upper bound on risk)
python3 scripts/crap_score.py --root backend/app --top 25

# With coverage JSON report
pytest --cov=app --cov-report=json:coverage.json
python3 scripts/crap_score.py --root backend/app --coverage coverage.json
```

---

## 3. The Strangler-Fig Refactoring Pattern
When faced with a giant monolithic component (e.g. CC > 500, CRAP > 100,000):
1. **Never attempt a full rewrite**: Rewrites introduce catastrophic regressions and break subtle contracts.
2. **Carve out independent sub-surfaces**: Extract isolated UI sections, drawers, and accordions into standalone components (e.g. `RubricPanel.jsx`, `StudyTimer.jsx`, `AIChatDrawer.jsx`).
3. **Strict TDD Unit Tests**: Create dedicated unit test files mocking only external boundaries, asserting controlled and uncontrolled states.
4. **Mount cleanly**: Replace inline blocks with component mounts and remove obsolete imports from the parent.
5. **Re-scan and record**: Re-run `crap_score` to measure verified reduction in CC and CRAP score.
