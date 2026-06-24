# Unified Hosting Guide: Deploying to Render

To host this application entirely on **one platform**, we can use **Render's Blueprint feature**. By adding a `render.yaml` file to the project root, you can spin up the entire stack with a single click.

## Services Deployed
1. **PostgreSQL Database**: Free-tier cloud SQL instance to store your analysis history.
2. **FastAPI Backend (Docker)**: Automatically built using `backend/Dockerfile` (so system tools like `git` are available).
3. **Next.js Frontend (Node)**: Automatically built and hosted as a Node.js web service.

---

## One-Click Deployment Steps

### 1. Push Code to GitHub / GitLab
Make sure all your local files (including the newly created `render.yaml` and the database updates) are committed and pushed to your git repository.

### 2. Connect Blueprint to Render
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Blueprint**.
3. Select your git repository.
4. Render will read the `render.yaml` file and automatically configure:
   - The PostgreSQL database.
   - The FastAPI backend web service.
   - The Next.js frontend web service.
   - All connection links (the frontend will automatically point to the backend, and the backend will automatically connect to the database).
5. Click **Apply**.

Render will start building and deploying all three services sequentially. Once complete:
- Your frontend will be available at: `https://ai-trust-validator-frontend.onrender.com`
- Your backend will be available at: `https://ai-trust-validator-backend.onrender.com`
- Your database will be linked privately.
