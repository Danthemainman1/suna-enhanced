# Deploying Suna Ultra to GitHub Pages - Complete Guide

## Important Note About Architecture

GitHub Pages only hosts **static content**. Suna Ultra has two parts:
- **Frontend (Static)**: Can be deployed to GitHub Pages
- **Backend (Dynamic)**: Requires a separate hosting solution (Railway, Render, Fly.io, AWS, etc.)

This guide covers deploying the frontend to GitHub Pages and connecting it to your backend.

---

## Part 1: Prepare Your Next.js App for Static Export

### Step 1: Configure next.config.ts

Update `frontend/next.config.ts` for static export:

```typescript
import type { NextConfig } from 'next';

const nextConfig = (): NextConfig => ({
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  basePath: process.env.NODE_ENV === 'production' ? '/suna-enhanced' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/suna-enhanced/' : '',
  
  // Disable features not compatible with static export
  // experimental: {
  //   optimizePackageImports: [], // Keep if needed, but test thoroughly
  // },
});

export default nextConfig;
```

**Note**: Replace '/suna-enhanced' with your actual repository name.

### Step 2: Update Environment Variables

Create `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_WS_URL=wss://your-backend-url.com
NEXT_PUBLIC_BASE_PATH=/suna-enhanced
```

### Step 3: Handle Client-Side Routing

Create `frontend/public/404.html` for SPA routing:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Suna Ultra</title>
  <script type="text/javascript">
    var pathSegmentsToKeep = 1;
    var l = window.location;
    l.replace(
      l.protocol + '//' + l.hostname + (l.port ? ':' + l.port : '') +
      l.pathname.split('/').slice(0, 1 + pathSegmentsToKeep).join('/') + '/?/' +
      l.pathname.slice(1).split('/').slice(pathSegmentsToKeep).join('/').replace(/&/g, '~and~') +
      (l.search ? '&' + l.search.slice(1).replace(/&/g, '~and~') : '') +
      l.hash
    );
  </script>
</head>
<body>
</body>
</html>
```

### Step 4: Add .nojekyll File

Create an empty file at `frontend/public/.nojekyll` to prevent Jekyll processing:

```bash
touch frontend/public/.nojekyll
```

---

## Part 2: Set Up GitHub Actions for Automatic Deployment

### Step 1: Create the Workflow File

Create `.github/workflows/deploy-pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Build
        working-directory: ./frontend
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
          NEXT_PUBLIC_WS_URL: ${{ secrets.WS_URL }}

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./frontend/out

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## Part 3: Enable GitHub Pages in Repository Settings

### Step 1: Go to Repository Settings
1. Navigate to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" in the left sidebar

### Step 2: Configure Pages Source
1. Under "Build and deployment"
2. Set "Source" to "GitHub Actions"
3. Save

### Step 3: Add Repository Secrets
1. Go to Settings > Secrets and variables > Actions
2. Add the following secrets:
   - `API_URL`: Your backend API URL (e.g., https://api.suna-ultra.com)
   - `WS_URL`: Your WebSocket URL (e.g., wss://api.suna-ultra.com)

---

## Part 4: Manual Deployment (Alternative Method)

If you prefer manual deployment:

### Step 1: Build the Static Site

```bash
cd frontend
npm install
npm run build
```

### Step 2: Deploy Using gh-pages Package

Install gh-pages:

```bash
npm install -D gh-pages
```

Add to `frontend/package.json` scripts:

```json
"scripts": {
  "deploy": "gh-pages -d out -t true"
}
```

Run deployment:

```bash
npm run deploy
```

---

## Part 5: Deploy Backend Separately

### Option A: Railway (Recommended for Simplicity)

1. Go to railway.app and sign in with GitHub
2. Click "New Project" > "Deploy from GitHub repo"
3. Select your repository
4. Set root directory to `/backend`
5. Add environment variables in Railway dashboard
6. Railway will auto-detect Python/FastAPI and deploy

### Option B: Render

1. Go to render.com and sign in
2. Create new "Web Service"
3. Connect your GitHub repository
4. Set:
   - Root Directory: backend
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Option C: Fly.io

Create `backend/fly.toml`:

```toml
app = "suna-ultra-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
```

Deploy:

```bash
cd backend
fly launch
fly secrets set DATABASE_URL=your_db_url
fly deploy
```

### Option D: Self-Hosted with Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Part 6: Connect Frontend to Backend

### Update CORS Settings

In `backend/api.py` or `backend/core/api.py`, ensure CORS allows your GitHub Pages domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://danthemainman1.github.io",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Update Frontend API Configuration

In `frontend/src/lib/api.ts` (or create if doesn't exist):

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export const api = {
  baseUrl: API_URL,
  wsUrl: WS_URL,
};
```

---

## Part 7: Custom Domain (Optional)

### Step 1: Add Custom Domain in GitHub
1. Go to Settings > Pages
2. Under "Custom domain", enter your domain
3. Click Save

### Step 2: Configure DNS
Add these records at your DNS provider:

For apex domain (example.com):
- Type: A
- Name: @
- Value: 185.199.108.153
- Value: 185.199.109.153
- Value: 185.199.110.153
- Value: 185.199.111.153

For subdomain (www.example.com):
- Type: CNAME
- Name: www
- Value: yourusername.github.io

### Step 3: Enable HTTPS
1. Wait for DNS propagation (up to 24 hours)
2. In GitHub Pages settings, check "Enforce HTTPS"

### Step 4: Update next.config.ts for Custom Domain

```typescript
const nextConfig = (): NextConfig => ({
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // Remove basePath and assetPrefix for custom domain
});
```

---

## Part 8: Verify Deployment

### Checklist:
- [ ] Frontend loads at https://yourusername.github.io/suna-enhanced/
- [ ] All static assets load correctly
- [ ] Client-side routing works (refresh any page)
- [ ] API calls reach your backend
- [ ] WebSocket connections establish
- [ ] Authentication flows work
- [ ] No console errors related to CORS or mixed content

### Troubleshooting:

**404 on page refresh:**
- Ensure 404.html is in the out directory
- Check that .nojekyll file exists

**Assets not loading:**
- Verify basePath matches your repo name
- Check assetPrefix is set correctly

**API calls failing:**
- Check CORS configuration on backend
- Verify NEXT_PUBLIC_API_URL is set correctly
- Ensure backend is running and accessible

**WebSocket not connecting:**
- Confirm WSS (not WS) for production
- Check WebSocket URL in environment variables

---

## Part 9: Continuous Deployment

Every push to `main` branch will automatically:
1. Build the Next.js app
2. Export static files
3. Deploy to GitHub Pages

Monitor deployments:
1. Go to repository > Actions tab
2. Click on "Deploy to GitHub Pages" workflow
3. View build and deployment logs

---

## Quick Reference Commands

```bash
# Local development
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Preview production build
cd frontend && npx serve out

# Manual deploy to GitHub Pages
cd frontend && npm run deploy

# View deployment status
gh run list --workflow=deploy-pages.yml
```

---

## Summary

Your Suna Ultra deployment architecture:

```
┌─────────────────────────────────────────────────────────┐
│                      USERS                               │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              GitHub Pages (Frontend)                     │
│         https://yourusername.github.io/suna-enhanced     │
│                   Static Next.js App                     │
└─────────────────────────┬───────────────────────────────┘
                          │
                API Calls & WebSockets
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            Backend Host (Railway/Render/Fly.io)          │
│              https://api.suna-ultra.com                  │
│                    FastAPI Server                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Database & Redis                       │
│              (Supabase / Railway / etc.)                 │
└─────────────────────────────────────────────────────────┘
```

---

This concludes the GitHub Pages deployment guide. Your Suna Ultra frontend will be publicly accessible and automatically updated on every push to main!
