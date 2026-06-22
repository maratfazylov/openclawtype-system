# SWE Resolution

Use this skill for repository-level bug fixes, feature requests, and issue
resolution.

## Workflow

1. Restate the target behavior in one sentence.
2. Locate entry points, tests, and nearby implementation.
3. Prefer a failing or focused test before patching when practical.
4. Make the smallest coherent code change.
5. Run the focused verification command and report the result.

## Review Checklist

- The patch addresses the observed root cause.
- Tests cover the behavior rather than implementation trivia.
- Public APIs and user-visible behavior are intentional.
- No unrelated formatting or metadata churn was introduced.
