# AgentForge Deployment Smoke Checklist

Use after each deployment.

- `/health` returns `{"status":"ok"}`.
- `/ready` shows the target configured and `evidence_environment=deployed`.
- `/ready` shows `operator_auth_configured=true`.
- Unauthenticated `GET /operator/status` returns 401.
- Authenticated `GET /operator/status` returns model and target metadata.
- `POST /operator/campaigns` rejects unknown fields such as `target_url`.
- A one-case campaign writes `evals/results/<run-id>.json`.
- High-severity findings appear in `needs_approval`.
- Approval writes `evals/regression/<finding-id>.json`.
- Artifact retrieval requires operator auth.
- Langfuse outage or disabled config does not fail the campaign.
- Budget `0.0` skips target execution.
