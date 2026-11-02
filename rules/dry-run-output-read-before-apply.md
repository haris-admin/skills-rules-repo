# Read the dry-run output before any apply, as a separate step

Applies to deploy scripts, Terraform, DNS and any "dry run by default, apply on a flag" tool.

## Why this exists

**2 Nov 2026, handledispute.** Chaining `./deploy.sh && ./deploy.sh --apply` in one command was blocked by the Claude Code auto-mode classifier as a "Blind Apply": the apply would run without anyone reading what the dry run printed. Separately, `terraform apply` was blocked as protected-scope infrastructure. Both blocks were right.

## Core Directives

1. **Run the dry run alone, read its output, then run the apply as its own command.** Never chain them.
2. **State what the dry run showed** (counts, targets, what will not be touched) before applying.
3. **Terraform:** produce a saved plan with `terraform plan -out`, show the summary (adds, changes, destroys; any replace is a stop), then give the human a short script that applies that exact plan file. Do not try to route around the classifier.
4. **The plan must be read-only safe:** `-lock=false` only when you are the sole operator and say so; `AWS_PROFILE` explicit on every command.
5. **Gate destructive steps on proof, not on time.** A swap that removes the old service runs only after a public check proves the new path serves (for example a response header only the new edge sets), and it falls back by itself when its own final check fails.
6. **Do not `rm -rf` inside `bash -c`.** The safety check cannot inspect the inner script and blocks it. Use explicit paths, no cleanup, or leave temp folders to the OS.

## Verification

The transcript shows the dry run, a sentence reading its result, and the apply as separate steps.
