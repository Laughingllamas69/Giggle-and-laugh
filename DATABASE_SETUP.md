# MongoDB Atlas Setup

The app can use MongoDB Atlas for mood history, community memes, and community jokes. When no database is configured, it continues to run, but new contributions only last for the current session.

## Create an Atlas database

1. Create a MongoDB Atlas account and a free shared cluster.
2. In **Database Access**, create a database user with read/write access to the `giggle_laugh` database. Use a unique, strong password.
3. In **Network Access**, allow your current IP for local testing. For a hosted app, use the hosting provider's current networking guidance; avoid broad network access unless you understand the exposure and have restricted the database user appropriately.
4. Select **Connect** then **Drivers**, choose Python, and copy the connection string. Replace the username, password, and cluster host. URL-encode special characters in the password.

## Run locally

Create `.streamlit/secrets.toml` using `.streamlit/secrets.toml.example` as a template, then put your real Atlas URI in it. That real secrets file is excluded by `.gitignore`; do not commit it or share the URI.

Set `APP_ADMIN_PASSWORD` in the same file to a long, unique password that only you know. Open the app's sidebar, expand **Owner controls**, and enter that password to unlock the community content manager. From there you can edit or delete uploaded memes and jokes for everyone. The password is never the public nickname used to enter the app.

Restart Streamlit after changing `secrets.toml` so the app loads the new password.

Start the app with:

```sh
streamlit run app.py
```

When the app connects, the MongoDB warning disappears. Collections and indexes are created automatically for mood logs, memes, and jokes.

## Deploy with Streamlit Community Cloud

In the deployed app's **Settings > Secrets**, add the same TOML values:

```toml
MONGODB_URI = "mongodb+srv://..."
MONGO_DB_NAME = "giggle_laugh"
APP_ADMIN_PASSWORD = "choose-a-long-unique-password"
```

Keep the URI and owner password in the hosting provider's secret settings, never in source code. Atlas network access must also allow the deployed app's outbound connections.

On a shared deployment, anyone who can access the sidebar can see the owner login, but only someone with `APP_ADMIN_PASSWORD` can edit or delete community uploads. Use a strong password and rotate it if it is exposed.

Meme image files are stored in MongoDB with a 5 MB upload limit. For a larger public gallery, move image files to object storage and keep only their URLs and captions in MongoDB.