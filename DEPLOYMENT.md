# Run, test, and deploy

## Run locally

1. Use Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install the packages listed in `requirements.txt`:

   ```sh
   python -m pip install -r requirements.txt
   ```

4. Start the app:

   ```sh
   streamlit run app.py
   ```

Without Supabase secrets, the app starts in session-only mode. On the welcome screen, enable **Presentation demo mode** to see sample analytics (mood trends, daily active users, popular games, and top posts), demo posts, and local-only profile/activity/reaction/chat data. Demo mode does not require Supabase and never writes the sample content to the database. The Anonymous Campus Pulse clearly labels illustrative sample statistics when live aggregates are unavailable or the privacy threshold is not met. Chat is shared across app sessions only after Supabase is configured and the schema has been applied. Chat attachments are limited to PNG, JPG, WebP, PDF, or UTF-8 TXT files up to 1 MB; signed download links expire after one hour.

## Configure Supabase

Follow [`DATABASE_SETUP.md`](DATABASE_SETUP.md). Run `supabase_schema.sql` in the Supabase SQL Editor before adding the secrets. Re-run it on an existing project to add the mood-label column, shared chat table, and private chat-attachment bucket. Add the college counseling center name and verified phone number as `COUNSELING_CENTER_NAME` and `COUNSELING_CENTER_PHONE` secrets. The app checks for all required tables at startup; if the schema is incomplete, its shared database features remain unavailable.

Never commit the Supabase service-role key. For local development, place secrets in `.streamlit/secrets.toml`, which should remain untracked. In Streamlit Community Cloud, add the same values in the app's **Settings > Secrets**.

## Run tests

The helper tests use Python's standard library and need no test-only package:

```sh
python -m unittest -v test_app_helpers
```

Compile-check the app with:

```sh
python -m py_compile app.py app_helpers.py
```

## Deploy to Streamlit Community Cloud

1. Push the project to a GitHub repository without local secrets, virtual environments, or database files.
2. Create a Streamlit Community Cloud app and point it to `app.py`.
3. Add the Supabase settings and owner password from `DATABASE_SETUP.md` under **Settings > Secrets**.
4. Deploy and confirm the app starts without the Supabase schema warning.

The public nickname login is a pseudonym, not an account authentication system. Anyone who knows a nickname can reuse it, so avoid entering sensitive or identifying information in nicknames, jokes, memes, or mood notes. Non-RPS arcade scores are player-submitted and are not validated against the embedded games.
