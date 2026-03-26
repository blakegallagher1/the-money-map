"""Run an OpenAI deep research job against this repository and save the report."""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import (  # noqa: E402
    DEEP_RESEARCH_MAX_TOOL_CALLS,
    DEEP_RESEARCH_MODEL,
    RESEARCH_PROMPT_MODEL,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "research"
DEFAULT_GOAL = (
    "Assess this repository and determine the best path to turn it into a fully "
    "automated YouTube video creating machine with minimal human touch, using "
    "OpenAI where it creates clear leverage."
)
DEFAULT_CONTEXT_PATHS = [
    Path("README.md"),
    Path("config/settings.py"),
    Path("scripts/orchestrator.py"),
    Path("scripts/llm_script_writer.py"),
    Path("scripts/tts_generator.py"),
    Path("scripts/youtube_api_uploader.py"),
    Path("tasks/todo.md"),
]
MAX_CHARS_PER_FILE = 8_000
MAX_STATUS_WAIT_SECONDS = 45 * 60
POLL_INTERVAL_SECONDS = 15


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the deep research runner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal", default=DEFAULT_GOAL, help="Research objective.")
    parser.add_argument(
        "--response-id",
        help="Resume or poll an existing response ID instead of submitting a new job.",
    )
    parser.add_argument(
        "--context-file",
        action="append",
        default=[],
        help="Additional repo-relative file(s) to include in the prompt context.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for Markdown and JSON outputs.",
    )
    parser.add_argument(
        "--prompt-model",
        default=RESEARCH_PROMPT_MODEL,
        help="Model used to rewrite the seed brief into a richer research prompt.",
    )
    parser.add_argument(
        "--research-model",
        default=DEEP_RESEARCH_MODEL,
        help="Deep research model to execute.",
    )
    parser.add_argument(
        "--max-tool-calls",
        type=int,
        default=DEEP_RESEARCH_MAX_TOOL_CALLS,
        help="Upper bound for web-search tool calls during research.",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=POLL_INTERVAL_SECONDS,
        help="Seconds between background job polls.",
    )
    parser.add_argument(
        "--max-wait-seconds",
        type=int,
        default=MAX_STATUS_WAIT_SECONDS,
        help="Max seconds to wait for the background job before failing.",
    )
    parser.add_argument(
        "--skip-rewrite",
        action="store_true",
        help="Use the seed prompt directly without the GPT-5.4 rewrite step.",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    """Convert arbitrary text into a filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "deep-research"


def load_context_excerpt(path: Path, max_chars: int = MAX_CHARS_PER_FILE) -> str:
    """Load a bounded excerpt from a file for inclusion in the research prompt."""
    text = path.read_text()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated by deep research runner]..."


def selected_context_paths(extra_paths: list[str]) -> list[Path]:
    """Resolve and deduplicate the context files used to brief the model."""
    ordered_paths: list[Path] = []
    seen: set[Path] = set()
    for candidate in DEFAULT_CONTEXT_PATHS + [Path(item) for item in extra_paths]:
        resolved = (REPO_ROOT / candidate).resolve()
        if not resolved.exists() or resolved in seen:
            continue
        seen.add(resolved)
        ordered_paths.append(resolved)
    return ordered_paths


def build_repo_context(extra_paths: list[str]) -> str:
    """Render the selected repository files into a prompt-friendly context block."""
    blocks: list[str] = []
    for path in selected_context_paths(extra_paths):
        rel_path = path.relative_to(REPO_ROOT)
        blocks.append(
            textwrap.dedent(
                f"""
                FILE: {rel_path}
                ```text
                {load_context_excerpt(path)}
                ```
                """
            ).strip()
        )
    return "\n\n".join(blocks)


def build_seed_prompt(goal: str, repo_context: str) -> str:
    """Build the deterministic seed prompt sent into the prompt-rewrite step."""
    return textwrap.dedent(
        f"""
        The current date is March 25, 2026.

        User goal:
        {goal}

        Repository:
        - Name: The Money Map
        - Path: {REPO_ROOT}
        - Current positioning: automated macro-data YouTube video pipeline with script, voiceover,
          rendering, thumbnail, and YouTube upload steps.

        Research task:
        1. Assess what is already automated in this repository.
        2. Identify the missing systems required for a genuinely autonomous YouTube channel:
           topic selection, trend/context research, script quality control, asset generation,
           edit QA, upload metadata, scheduling, analytics feedback loops, and cost/reliability guardrails.
        3. Recommend the highest-leverage OpenAI-powered upgrades that fit this codebase right now.
        4. Separate recommendations into:
           - immediate repo-local changes
           - next-step operational automation
           - optional future improvements
        5. Call out where the repo is using older model choices or legacy API patterns.
        6. Return a citation-backed report with concrete implementation guidance, not generic advice.

        Output requirements for the final research report:
        - Start with an executive summary.
        - Include a "Current State" section.
        - Include a "Gaps To Full Automation" section.
        - Include a "Recommended Architecture" section with components and data flow.
        - Include a "Top 5 Repo Changes" section with file-level suggestions where possible.
        - Include a "90-Day Automation Roadmap" section.
        - Include a "Risks and Guardrails" section.
        - Cite all external claims inline.

        Repo context:
        {repo_context}
        """
    ).strip()


def rewrite_prompt(client: OpenAI, goal: str, repo_context: str, prompt_model: str) -> str:
    """Use GPT-5.4 to expand the seed brief into a better deep research prompt."""
    seed_prompt = build_seed_prompt(goal, repo_context)
    rewrite_response = client.responses.create(
        model=prompt_model,
        reasoning={"effort": "medium"},
        text={"verbosity": "high"},
        input=[
            {
                "role": "system",
                "content": (
                    "Rewrite the user's brief into a single deep-research prompt for "
                    "o3-deep-research. Do not answer the task. Produce only the rewritten "
                    "prompt text. Make the scope concrete, implementation-focused, and "
                    "citation-oriented."
                ),
            },
            {"role": "user", "content": seed_prompt},
        ],
    )
    prompt_text = rewrite_response.output_text.strip()
    if not prompt_text:
        raise RuntimeError("Prompt rewrite returned no text.")
    return prompt_text


def submit_research_job(
    client: OpenAI,
    research_model: str,
    prompt_text: str,
    max_tool_calls: int,
) -> tuple[Any, str]:
    """Submit the background deep-research request, retrying tool naming if needed."""
    tool_variants = ["web_search", "web_search_preview"]
    last_error: Exception | None = None
    for tool_type in tool_variants:
        try:
            response = client.responses.create(
                model=research_model,
                background=True,
                instructions=(
                    "You are a principal research analyst helping re-architect a Python "
                    "YouTube automation repository. Use the web aggressively, cite claims, "
                    "and prioritize concrete implementation guidance."
                ),
                input=prompt_text,
                max_tool_calls=max_tool_calls,
                tools=[{"type": tool_type, "search_context_size": "medium"}],
                store=True,
            )
            return response, tool_type
        except Exception as exc:  # pragma: no cover - exercised only on API mismatch
            last_error = exc
    raise RuntimeError(f"Failed to submit deep research job: {last_error}") from last_error


def wait_for_response(
    client: OpenAI,
    response_id: str,
    poll_interval: int,
    max_wait_seconds: int,
) -> Any:
    """Poll a background response until it completes or fails."""
    deadline = time.time() + max_wait_seconds
    last_status: str | None = None
    while time.time() < deadline:
        response = client.responses.retrieve(response_id)
        if response.status != last_status:
            print(f"[research] status={response.status}")
            last_status = response.status
        if response.status in {"completed", "failed", "cancelled", "incomplete"}:
            return response
        time.sleep(poll_interval)
    raise TimeoutError(f"Deep research job did not finish within {max_wait_seconds} seconds.")


def extract_citations(response_payload: dict[str, Any]) -> list[tuple[str, str]]:
    """Collect and deduplicate URL citations from a response payload."""
    citations: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for output_item in response_payload.get("output", []):
        for content in output_item.get("content", []) or []:
            for annotation in content.get("annotations", []) or []:
                url = annotation.get("url")
                title = annotation.get("title") or url
                pair = (title, url)
                if url and pair not in seen:
                    seen.add(pair)
                    citations.append(pair)
    return citations


def render_markdown_report(
    *,
    goal: str,
    prompt_text: str,
    response_payload: dict[str, Any],
    research_model: str,
    prompt_model: str,
    tool_type: str,
) -> str:
    """Render the final Markdown artifact from the raw response payload."""
    report_text = response_payload.get("output_text", "").strip()
    citations = extract_citations(response_payload)
    citation_block = ""
    if citations:
        lines = [f"- [{title}]({url})" for title, url in citations]
        citation_block = "\n## Sources\n\n" + "\n".join(lines)

    return textwrap.dedent(
        f"""
        # OpenAI Deep Research Report

        - Generated: {datetime.now().astimezone().isoformat(timespec="seconds")}
        - Goal: {goal}
        - Prompt model: `{prompt_model}`
        - Research model: `{research_model}`
        - Web tool: `{tool_type}`

        ## Expanded Prompt

        ```text
        {prompt_text}
        ```

        ## Report

        {report_text}
        """
    ).strip() + citation_block + "\n"


def save_artifacts(
    output_dir: Path,
    stem: str,
    markdown: str,
    response_payload: dict[str, Any],
) -> tuple[Path, Path]:
    """Persist the Markdown report and raw JSON payload to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    markdown_path.write_text(markdown)
    json_path.write_text(json.dumps(response_payload, indent=2))
    return markdown_path, json_path


def main() -> None:
    """Run the prompt rewrite, deep research job, and artifact persistence flow."""
    args = parse_args()
    client = OpenAI()
    if args.response_id:
        prompt_text = (
            f"Resumed existing response `{args.response_id}`. "
            "Original prompt text was not regenerated in this invocation."
        )
        tool_type = "resumed-response"
        prompt_model = "n/a (resume mode)"
        response_id = args.response_id
        print(f"[research] resuming response_id={response_id}")
    else:
        repo_context = build_repo_context(args.context_file)
        prompt_text = (
            build_seed_prompt(args.goal, repo_context)
            if args.skip_rewrite
            else rewrite_prompt(client, args.goal, repo_context, args.prompt_model)
        )
        response, tool_type = submit_research_job(
            client=client,
            research_model=args.research_model,
            prompt_text=prompt_text,
            max_tool_calls=args.max_tool_calls,
        )
        prompt_model = args.prompt_model
        response_id = response.id
        print(f"[research] response_id={response_id}")

    final_response = wait_for_response(
        client=client,
        response_id=response_id,
        poll_interval=args.poll_interval,
        max_wait_seconds=args.max_wait_seconds,
    )
    response_payload = final_response.model_dump(mode="json")
    response_payload["output_text"] = final_response.output_text

    if final_response.status != "completed":
        raise RuntimeError(f"Deep research job ended with status={final_response.status}")

    stem = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.goal)[:80]}"
    markdown = render_markdown_report(
        goal=args.goal,
        prompt_text=prompt_text,
        response_payload=response_payload,
        research_model=getattr(final_response, "model", None) or args.research_model,
        prompt_model=prompt_model,
        tool_type=tool_type,
    )
    markdown_path, json_path = save_artifacts(
        output_dir=Path(args.output_dir),
        stem=stem,
        markdown=markdown,
        response_payload=response_payload,
    )
    print(f"[research] markdown={markdown_path}")
    print(f"[research] json={json_path}")


if __name__ == "__main__":
    main()
