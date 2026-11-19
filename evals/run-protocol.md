# A/B run protocol

1. **Scaffold & Randomize Blind Labels:**
   Run `node evals/prepare-blind-eval.mjs --date YYYY-MM-DD` to create `evals/results/YYYY-MM-DD/<prompt>/{A,B}`, a randomized `blind-key.json`, and a blank human scoring sheet `blind-sheet.md`.
2. **Execute Both Conditions Fairly:**
   Run each fixed prompt in `evals/prompts/` twice with the same model, repository state, and time budget:
   - **A:** Baseline without this skill.
   - **B:** Treatment with this skill enabled.
   Store generated source, command logs, checker report, slop-scan report, and 375 / 820 / 1440 viewport screenshots inside `evals/results/YYYY-MM-DD/<prompt>/A` and `/B`.
3. **Blind Human Scoring:**
   Present the outputs to a human reviewer using the randomized `Candidate-1` / `Candidate-2` labels from `blind-sheet.md` without revealing `blind-key.json`.
4. **Unblind & Compare:**
   After human scoring is complete, record `score.json` in each `A` and `B` folder and run `node evals/compare.mjs`. Do not fabricate scores or report an aggregate before a human has completed the blind score sheet.
