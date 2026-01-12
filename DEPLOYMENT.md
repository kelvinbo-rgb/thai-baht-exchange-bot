# Deployment Guide for Thai Baht Exchange Bot

Since you are using GitHub Desktop and the GCP Console, follow these steps to deploy the application.

## 1. Push Changes to GitHub
1. Open **GitHub Desktop**.
2. You should see new files: `Dockerfile`, `.dockerignore`, `deploy.ps1`.
3. Commit these changes with a message like "Add Docker configuration for GCP".
4. Click **Push origin** to send code to GitHub.

## 2. Deploy on Google Cloud Platform (GCP)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **Cloud Run**.
3. Click **CREATE SERVICE**.
4. **Source**: Select **Continuously deploy new revisions from a source repository**.
5. **SET UP CLOUD BUILD**:
   - **Provider**: GitHub.
   - **Repository**: Select your `thai-baht-exchange-bot` repository.
   - **Branch**: `main` (or `master`).
   - **Build Type**: Go, Node.js, Python, Java, .NET, Ruby, PHP, or **Dockerfile** (Choose **Dockerfile**).
   - **Source location**: `/` (default).
6. **Authentication**: Allow unauthenticated invocations (Check "Allow unauthenticated invocations").
7. **Container, Networking, Security**:
   - Expand this section.
   - **General** > **Container port**: `8080`.
   - **Variables & Secrets**: Add the following Environment Variables (copy values from your local `.env` file):
     - `LINE_CHANNEL_ACCESS_TOKEN`: (Your long token)
     - `LINE_CHANNEL_SECRET`: (Your secret)
     - `ADMIN_USER_IDS`: (Your admin IDs)
     - `RATE_UPDATE_INTERVAL`: `30`
     - `ALERT_CHECK_INTERVAL`: `30`
     - `TZ`: `Asia/Bangkok`
8. Click **CREATE**.

## 3. Verify Deployment
1. Wait for the build and deployment to finish (green checkmark).
2. Copy the **URL** provided by Cloud Run (e.g., `https://thai-baht-bot-xyz-uc.a.run.app`).
3. **Update LINE Webhook**:
   - Go to [LINE Developers Console](https://developers.line.biz/).
   - Select your channel.
   - Edit **Webhook settings**.
   - Paste the Cloud Run URL and append `/callback` (e.g., `https://thai-baht-bot-xyz-uc.a.run.app/callback`).
   - Click **Verify** (should return Success).
   - Enable **Use Webhook**.

## 4. Test
- Send "rate" to your LINE Bot.
- It should reply with the latest rates.
