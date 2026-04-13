# Deployment (enshaittify / agentic-web-sim)

## Production server

| Item | Value |
|------|--------|
| **Public URL** | `https://enshait.metakarma.org` (NGINX → Streamlit) |
| SSH host | `enshait.metakarma.org` (same machine as legacy `cmabot.app` if DNS points there) |
| User | `root` (SSH) |
| App directory | `/home/enshaittify` |
| Remote | `https://github.com/metakarma/enshaittify.git` |
| Process | Docker Compose service `simulation`, container `agentic-web-sim` |
| Published port | `127.0.0.1:8501:8501` (Streamlit; proxied by NGINX) |
| NGINX site file | `/etc/nginx/sites-available/enshait.metakarma.org` (also `enshait.cmabot.app` legacy) |

The **Dockerfile** copies `app/` and `.streamlit/` into the image at build time. After `git pull`, you must **rebuild** the image and **recreate** the container; a pull alone does not change what the running container executes.

## Manual deploy

```bash
ssh root@enshait.metakarma.org
cd /home/enshaittify
git pull origin main
docker compose build simulation
docker compose up -d simulation
```

One-liner:

```bash
ssh root@enshait.metakarma.org 'cd /home/enshaittify && git pull origin main && docker compose build simulation && docker compose up -d simulation'
```

## Automatic deploy (GitHub Actions)

On every **push to `main`**, the workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) connects over SSH and runs the same pull + build + up steps.

### One-time setup

1. On the server, ensure `/home/enshaittify` is a clone of this repo and `git pull` works (public repo or credentials on the host).
2. Generate an **SSH key pair** dedicated to deploys (no passphrase, or use a CI-friendly approach your team accepts):

   ```bash
   ssh-keygen -t ed25519 -f ./deploy_ci -C "github-actions-enshaittify" -N ""
   ```

3. Install the **public** key on the server for `root`:

   ```bash
   cat deploy_ci.pub >> /root/.ssh/authorized_keys
   ```

4. In GitHub: **Repository → Settings → Secrets and variables → Actions → New repository secret**
   - Name: `DEPLOY_SSH_KEY`
   - Value: full contents of the **private** key file (`deploy_ci`), including `BEGIN` / `END` lines.

Without `DEPLOY_SSH_KEY`, the workflow fails on the ssh-agent step.

### Skip deploy for one push

Put **`[skip deploy]`** in the **commit message** (e.g. `docs: tweak README [skip deploy]`).

### Disable automatic deploy

- Remove or disable the workflow, or
- Ask maintainers not to push auto-deploy changes, or
- Stop using the `DEPLOY_SSH_KEY` secret (workflow will fail until restored).

### Manual run

**Actions → Deploy → Run workflow** runs the same SSH deploy without a new commit.

## Policy (default)

**Deploy on every push to `main`** unless a commit is explicitly marked with `[skip deploy]` or you are told not to deploy for a change.
