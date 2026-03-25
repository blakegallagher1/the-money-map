# The Money Map — Lessons Learned

<!--
Entry format (from CLAUDE.md §3 Self-Improvement Loop):

## [YYYY-MM-DD] Short description
- **Mistake**: What went wrong
- **Root cause**: Why it happened
- **Preventive rule**: How to avoid it next time
- **Concrete check**: Specific step to verify before closing a task

Categories: pipeline | rendering | data | scripting | infra | workflow
-->

## Quick-Reference Rules
<!-- Promoted from recurring lessons. Check these EVERY session. -->

| # | Rule | Source |
|---|------|--------|
| — | _(none yet — rules get promoted here after patterns emerge)_ | — |

## Session Log

<!-- Newest entries at the top -->

## [2026-03-25] Verify current product surface before browser automation
- **Mistake**: I pushed into a ChatGPT/Atlas/Playwright Sora browser flow before confirming the current end-user Sora entry point and whether it was still available in the authenticated UI.
- **Root cause**: I treated earlier Sora assumptions as still current and optimized for automation too early instead of validating the live product surface first.
- **Preventive rule**: Before asking the user to clear auth friction or interact with a gated browser flow, confirm the current product route and reachable UI surface with one direct verification step.
- **Concrete check**: For any browser-driven third-party workflow, verify the live destination, visible entry point, and current availability before requesting sign-in, CAPTCHA, or Cloudflare effort from the user.
