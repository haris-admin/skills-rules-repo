# Neuroinclusive UI Component Patterns

Accessible UI component patterns designed specifically for neurodivergent individuals (ADHD, Autism, Dyslexia, and Executive Dysfunction).

---

## 1. The Trimodal Disclosure Canvas

Different brains absorb complex information through different sensory channels. Simplifii-OS interfaces should offer **Trimodal Disclosure**:

1. **Spatial / Visual Mode**: High-level node maps, interactive concept graphs (Three.js / React-Three-Fiber), or card galleries.
2. **Sequential / Step Mode**: Numbered linear checklists with big check targets and zero visual clutter.
3. **Literal vs Metaphorical Mode**: A toggle allowing autistic or literal thinkers to view plain-English, unambiguous instructions without idioms or figurative expressions.

---

## 2. Forgiving Interaction Patterns

### A. The "Undo Over Confirmation" Pattern
- Traditional modal dialogs ("Are you sure you want to delete this?") disrupt dopamine momentum and create anxiety.
- Instead, execute actions immediately and display an accessible, persistent **Undo Toast** (active for 8–10 seconds).

### B. Auto-Save with Visual Assurance
- Every text input and state modification must auto-save instantly to IndexedDB / local cache.
- Display a subtle, non-intrusive indicator (e.g. soft green check: *"Saved locally"*), eradicating the fear of lost work.

### C. Shape + Color Dual Encoding
- Never convey state through color alone.
- Success: Soft green `#34d399` + Checkmark icon (`Lucide.CheckCircle`).
- Attention / In-Progress: Warm amber `#fbbf24` + Clock icon (`Lucide.Clock`).
- Blocker: Soft rose `#f87171` + Shield alert icon (`Lucide.AlertTriangle`).
