# Supabase Setup

The app uses Supabase Postgres for mood history, profiles, activity/streaks, community memes and jokes, comments/reactions, community chat, moderation reports, and game scores. The overview includes aggregated mood trends, daily active users, game activity, and the most-reacted community posts. Meme image files are stored in Supabase Storage, while their titles, captions, and storage paths are stored in Postgres. If Supabase is not configured, the app still starts in session-only mode; use **Presentation demo mode** on the welcome screen to preview illustrative analytics and local-only interactions.

## Create the Supabase project

1. Create a project at [Supabase](https://supabase.com/) and wait for it to finish provisioning.
2. Open **SQL Editor**, paste the contents of [`supabase_schema.sql`](supabase_schema.sql), and run it. The script is safe to rerun on an existing project: it creates the new profile/activity/comment/reaction/score/report tables and adds visibility fields to existing community tables. It also creates the public-read `community-memes` bucket.
3. Open **Project Settings > API**. Copy the Project URL and the `service_role` secret key. Keep the service-role key private; it bypasses row-level security and must only be used by the Streamlit server.

Re-run the schema on existing projects to add the `mood_label` column used by meme-based mood check-ins, the Mood Garden, and the Sad/Hopeless support threshold, as well as the shared `chat_messages` table.

## Configure Streamlit Community Cloud

Open the deployed app's **Settings > Secrets** and add:

```toml
SUPABASE_URL = "https://<project-ref>.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "<service-role-key>"
SUPABASE_MEME_BUCKET = "community-memes"
SUPABASE_CHAT_BUCKET = "community-chat"
APP_ADMIN_PASSWORD = "<choose-a-long-unique-password>"
COUNSELING_CENTER_NAME = "<your college counseling center>"
COUNSELING_CENTER_PHONE = "<verified counseling center phone number>"
```

Replace the Supabase placeholders with the values from your project, use a long, unique owner password, and set the verified counseling contact details. Save the secrets, then reboot the Streamlit app. Never put the service-role key in GitHub, browser JavaScript, or a public message.

Use the college's verified counseling contact details. After a user records Sad or Hopeless check-ins at least three times in the trailing seven days, the Mood tab shows a supportive banner with the configured number. Without a configured number, the banner encourages reaching out but does not invent contact details.

The service-role key is used only in the server-side Python app. The schema enables RLS on the tables and does not grant table access to anonymous users. The Storage bucket is public-read so uploaded community meme images can be displayed to visitors; writes and deletes are performed server-side with the service-role key and owner controls.

## Owner controls

Open the app sidebar, expand **Owner controls**, and enter `APP_ADMIN_PASSWORD` to edit or delete uploaded memes and jokes, review user reports, dismiss reports, or hide reported posts for everyone. This password is separate from the public nickname login. Demo mode never writes demo content or moderation actions to Supabase.

Meme uploads are limited to 5 MB and PNG, JPG, or WebP. Chat attachments accept PNG, JPG, WebP, PDF, or UTF-8 TXT files up to 1 MB. The schema creates a private `community-chat` Storage bucket; attachment links are signed and expire after one hour. Community chat is shared between app sessions only when Supabase is configured; otherwise messages and files remain in the current Streamlit session. Chat retains the latest messages, limits message length, refreshes automatically, and allows the app owner to hide messages. Chat messages and uploaded files may be examined by community moderators for safety. Nickname login is not authentication, so do not post personal or sensitive information. The app also includes more than 200 India-focused general-knowledge questions and 50 timed riddles. The Anonymous Campus Pulse refreshes every minute and uses coarse aggregates only when at least five distinct pseudonyms have checked in during the last week; otherwise the app shows clearly labeled illustrative sample data. Live totals represent this app's shared database, not a campus-wide census. The Mood Garden plants one mood-matched flower per check-in day; breaks pause growth without removing plants. Leaderboards offer all-time and last-seven-days views. Rock-Paper-Scissors scores are recorded automatically. Other arcade leaderboard scores are explicitly **self-reported and unverified**. Profiles and mood history use a hashed nickname, not a verified account; anyone who knows a nickname can impersonate it. Do not use this demo to store sensitive information. Mood history can be downloaded as CSV or deleted by its owner from the Mood tab. Existing MongoDB data is not migrated automatically; this integration starts using the Supabase tables after setup.

For local installation, deployment, and test commands, see [`DEPLOYMENT.md`](DEPLOYMENT.md).