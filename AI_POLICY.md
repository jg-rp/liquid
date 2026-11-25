# AI Usage Policy

We view AI as a useful tool, particularly for spotting bugs, uncovering edge cases, and identifying inefficient code. However, maintainer review time is limited, and unreviewed AI output creates significant overhead.

If you use AI tools when interacting with this repository, please follow these rules.

## Prefer Concise Issues Over AI-Generated PRs

- **File an issue first:** If you use AI to find a bug or performance bottleneck, **open a concise issue** rather than submitting an AI-generated pull request.

- **No drive-by AI PRs:** Unsolicited pull requests generated primarily by AI will be closed without review. If you want to submit a fix, discuss it in the issue first.

## Keep Descriptions Brief and Direct

- **No waffle:** Do not paste raw, long-winded LLM summaries into issues, pull requests, or comments. Get straight to the point.

- **Show, don't tell:** Keep issue descriptions short. Focus on minimal reproducible examples, stack traces, benchmarks, or specific lines of code rather than walls of generated prose.

## Human Verification & Accountability

- **Verify every finding:** LLMs frequently hallucinate bugs or suggest micro-optimizations that hurt readability without improving performance. Confirm that an issue actually exists in the current codebase before reporting it.

- **Own your contributions:** If you use AI to assist with an approved pull request, you must understand every line of code you submit, verify it passes our test suite and linters, and be able to answer review questions in your own words.

## Disclosure

- Please note if an issue or pull request was identified or assisted by an AI tool, along with how you verified the output.
