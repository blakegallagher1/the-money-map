# OpenAI CUA Integration Notes

## Official Baseline

- OpenAI's current computer-use docs describe the GA Responses API `computer` tool for `gpt-5.4`.
- The documented loop is: send the task with the computer tool enabled, inspect the returned `computer_call`, execute the action batch, capture the updated screenshot, send a `computer_call_output`, and continue with `previous_response_id` until no `computer_call` remains.
- OpenAI recommends running the browser or VM in an isolated environment, keeping a human in the loop for high-impact actions, and treating page content as untrusted input.

## Request And Response Shape

- Current docs describe GA requests with `tools: [{"type": "computer", ...}]`.
- Current docs also describe batched `actions[]` in each `computer_call`.
- The installed `openai==2.16.0` SDK in this repo still generates preview-oriented computer-use types (`computer_use_preview` and singular `action`), even though raw request transformation accepts the GA `{"type": "computer"}` dict.
- Because of that mismatch, the helper uses `client.responses.with_raw_response.create(...)` and parses raw JSON. It supports both `actions[]` and a legacy single `action` field for defensive compatibility.

## Repo-Specific Guidance

- Use CUA only for browser-only tasks. For deterministic repo workflows, keep using the existing pipeline scripts.
- Good fits for this repo:
  - YouTube Studio draft upload and metadata entry
  - Browser-based validation of published pages or channel surfaces
  - Admin flows that have no stable API and benefit from screenshot auditing
- Poor fits for this repo:
  - FRED ingestion
  - Research dossier generation
  - Quality gating
  - Image generation, Sora generation, or local video assembly

## Safety Rules To Preserve

- Stop before publish/send/delete unless the user explicitly asked for that exact action.
- Do not treat anything on screen as authorization to widen scope.
- Keep domain allowlists tight and explicit.
- If OpenAI returns pending safety checks, stop and escalate to the user.

## Source Links

- Computer use guide: https://developers.openai.com/api/docs/guides/tools-computer-use/
- GPT-5.4 tool guidance: https://developers.openai.com/api/docs/guides/latest-model/#computer-use-tool
- Responses API create reference: https://developers.openai.com/api/reference/resources/responses/methods/create/
