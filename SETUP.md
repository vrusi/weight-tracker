# Setup: weight auto-logging from Apple Health

Weight flows automatically: Xiaomi scale → Apple Health → iOS Shortcut → GitHub Action → log.csv → dashboard. No typing.

## Pieces
- **iOS Shortcut "Log weight"** — reads latest Apple Health weight, POSTs a repository_dispatch to GitHub.
- **GitHub token** — fine-grained, `vrusi/weight-tracker` only, Contents: Read+Write. Stored only in the Shortcut.
- **Action** `.github/workflows/log-weight.yml` + `scripts/log_weight.py` — upserts the weight into today's row of log.csv (preserves calories/protein/notes already logged), commits, pushes.

## The Shortcut (iOS Shortcuts app)
1. **Find Health Samples** — Type: Weight, Sort: Start Date, Order: Latest First, Limit: 1. (A "start date in last 7 days" filter is fine.)
2. **Get Numbers from Input** — input = Health Samples → extracts the kg number.
3. **Get Contents of URL**
   - URL: `https://api.github.com/repos/vrusi/weight-tracker/dispatches`
   - Method: POST
   - Headers: `Authorization: Bearer <TOKEN>`, `Accept: application/vnd.github+json`
   - Request Body: JSON
     - `event_type` (Text) = `log-weight`
     - `client_payload` (**Dictionary**) → `weight` (Number) = the Numbers variable
   - Success = empty body / HTTP 204 ("Zero KB").

## Automate (optional)
Shortcuts → Automation → Time of Day (e.g. 9:00) → run the shortcut, "Ask Before Running" off. Weigh in the morning; it self-logs.

## Manual test / backfill
Trigger the Action directly (no Shortcut):
`gh workflow run log-weight.yml -f weight=79.95 -f date=2026-07-21`

## Notes
- Health must report kg. If it's in lb, convert in the Shortcut before sending.
- If a scale weigh-in is skipped, nothing is logged that run — harmless.
- Food/calories/protein are logged separately by messaging Claude (see LOGGING.md).
