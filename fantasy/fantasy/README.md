## 🏈 Fantasy Football Draft Companion

This project provides a companion application to assist with your Fantasy
Football draft, specifically designed to integrate with the Sleeper platform.

### ✨ Features

*   **Sleeper Integration:** Connects directly to your live Sleeper draft using
    your League ID, Draft ID, and User ID.
*   **Independent Data Ingestion:** Uses a dedicated service (`ingestion`)
    suitable for **scheduled runs (cron jobs)** to maintain a fresh, up-to-date
    player database.
*   **Real-time Assistance:** Provides draft recommendations and insights via
    the running server/middleware.
*   **Audio Support:** Optimized for better user experience when sharing your
    screen with the companion.

--------------------------------------------------------------------------------

### 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker**
*   **Docker Compose**

Additionally, set up the `commentary-extension` by uploading the extension
locally.

### ⚙️ Setup and Configuration

#### 1\. Environment Variables

Create a file named `.env` in the root directory of the project and fill in the
following variables:

```bash
# Your Google Gemini API Key for AI assistance/analysis
GEMINI_API_KEY="API_KEY_HERE"

# Database paths for Docker setup
# Path *inside* the Docker container where the database will reside
DB_PATH_IN_CONTAINER="/app/db/fantasy_ingestion.sqlite"
# Local path on your *host machine* where the database will be stored
DB_PATH_ON_HOST="/home/lpabon/test/db/fantasy_ingestion.sqlite"

# Note the middleware address needs to be manually changed in the extension.
PORT=5000
```

> **Note:** Replace `/home/lpabon/test/db/fantasy_ingestion.sqlite` with your
> actual desired local directory path.

#### 2\. Obtain Sleeper IDs

You will need the following crucial IDs from your Sleeper draft setup:

ID            | How to Find
:------------ | :----------
**Draft ID**  | It is the unique number found in the URL of your live draft page.
**League ID** | See the official Sleeper guide: [How do I find my League ID?](https://support.sleeper.com/en/articles/4121798-how-do-i-find-my-league-id)
**User ID**   | The most reliable method is to use the Sleeper API: Navigate to https://api.sleeper.app/v1/league/{your_league_id}/users (replacing {your_league_id}). This will return a JSON list of all user objects in the league. Find your own username and copy the corresponding user_id value.

--------------------------------------------------------------------------------

### 🚀 Running the Services

The application uses two separate services: `ingestion` (for data population)
and `server` (for live draft assistance).

#### 1\. Data Ingestion (Database Preparation)

The `ingestion` service is designed to be run **independently** to populate and
update the SQLite database. It should be run at least once before starting the
server.

*   **Manual Update:** Run this command to manually update the database:

    ```bash
    sudo docker compose up ingestion --build --force-recreate
    ```

    > The service will run until data population is complete and then stop.

*   **Automated Updates:** To keep your data fresh, this service is ideal for
    scheduling with a **cron job**.

#### 2\. Start the Middleware/Server (Live Draft Companion)

This starts the main application server that the Sleeper extension connects to
during your draft.

```bash
sudo docker compose up server --build --force-recreate
```

> **Important:** Keep this terminal window open and the server running
> throughout your draft session.

--------------------------------------------------------------------------------

### 🔌 Connecting the Sleeper Extension

1.  Open your **Sleeper Draft Tab** in your browser.
2.  Ensure the server is running (`Step 2` above).
3.  Enter your **Draft ID**, **League ID**, and **User ID** into the extension
    settings.
4.  Click **Connect** (or the equivalent button) within the extension.
