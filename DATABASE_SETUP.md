# Supabase Setup

The app uses Supabase Postgres for mood history, community memes, and community jokes. Meme image files are stored in Supabase Storage, while their titles, captions, and storage paths are stored in Postgres. If Supabase is not configured, the app still starts, but posts only last for that browser session.

## Create the Supabase project

1. Create a project at [Supabase](https://supabase.com/) and wait for it to finish provisioning.
2. Open **SQL Editor**, paste the contents of [`supabase_schema.sql`](supabase_schema.sql), and run it. This creates the tables and the public-read `community-memes` bucket.
3. Open **Project Settings > API**. Copy the Project URL and the `service_role` secret key. Keep the service-role key private; it bypasses row-level security and must only be used by the Streamlit server.

## Configure Streamlit Community Cloud

Open the deployed app's **Settings > Secrets** and add:

```toml
SUPABASE_URL = "https://<project-ref>.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "<service-role-key>"
SUPABASE_MEME_BUCKET = "community-memes"
APP_ADMIN_PASSWORD = "<choose-a-long-unique-password>"
```

Replace the first two placeholders with the values from Supabase. Set a long, unique owner password. Save the secrets, then reboot the Streamlit app. Never put the service-role key in GitHub, browser JavaScript, or a public message.

The service-role key is used only in the server-side Python app. The schema enables RLS on the tables and does not grant table access to anonymous users. The Storage bucket is public-read so uploaded community meme images can be displayed to visitors; writes and deletes are performed server-side with the service-role key and owner controls.

## Owner controls

Open the app sidebar, expand **Owner controls**, and enter `APP_ADMIN_PASSWORD` to edit or delete uploaded memes and jokes for everyone. This password is separate from the public nickname login.

Meme uploads are limited to 5 MB and PNG, JPG, or WebP. Existing MongoDB data is not migrated automatically; this integration starts using the Supabase tables after setup.