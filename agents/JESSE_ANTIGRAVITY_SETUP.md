# Setup: Docker Jesse + Google Antigravity on your PC (2026-10-17)

Goal: a second, different-lab AI agent (Gemini in Antigravity) with its own backtest engine (Jesse), used as a **blind
checker** of our strategy specs. Its first task comes later (Claude writes it when you ask).

Do this on a PC that is **not** the MultiCharts trading PC, or only outside market hours. Docker and agent runs use a lot of
CPU / memory and update-restarts; Monday 10/12's miss was a dropped connection.

## 1. Docker Desktop (Windows)

1. Download and install Docker Desktop: https://www.docker.com/products/docker-desktop/
   - Accept the **WSL 2** option when it asks (Jesse's project-file tools and research scripts need Docker or WSL on Windows).
   - Restart the PC if asked.
2. Open Docker Desktop once and wait until it says **Engine running**.
3. Settings → Resources: give it at least 4 GB memory (8 GB if you have 16 GB+).
4. Settings → General: turn **off** "Start Docker Desktop when you sign in" if this is also the trading PC.
5. Install Git for Windows if you don't have it: https://git-scm.com/download/win

## 2. A Jesse project in its own folder

Never inside the `thebeginning` repo: on every start Jesse writes its own agent rules into the project folder
(`AGENTS.md` / `CLAUDE.md` / `mcp-rules.md`), which would mix with our working rules.

Open **PowerShell**:

```powershell
cd $HOME
git clone https://github.com/jesse-ai/project-template jesse-bot
cd jesse-bot
copy .env.example .env
notepad .env
```

In `.env`:
- `PASSWORD=` a password of your own (the dashboard login; the AI connection token is made from it). Don't reuse an
  account password, and never paste it into any chat.
- Leave `APP_PORT=9000` unless something else uses port 9000.
- Leave the Postgres / Redis lines as they are for Docker.

Start it:

```powershell
cd docker
docker compose up -d
```

The first start downloads the images (a few minutes). Then open http://localhost:9000 and log in with your PASSWORD.

- Stop: `docker compose stop` (from `jesse-bot\docker`). Start again: `docker compose up -d`.
- Logs if something is wrong: `docker compose logs -f`.

## 3. A free Jesse account (for the runs)

In the dashboard, log in / sign up for a free jesse.trade account. Without one, the AI can't run backtests
(guests: 0 runs a day); free: 100 backtest / Monte Carlo / significance / optimization runs a day; reading files and
candles is unlimited. No paid plan needed for our use.

## 4. Google Antigravity

1. Download and install: https://antigravity.google/ ; sign in with your Google account.
2. **File → Open Folder → `jesse-bot`** (the Jesse project, not our repo).
3. Agent settings: set it to **ask before running terminal commands** (review-driven), not "always proceed".

## 5. Connect Antigravity to Jesse (MCP)

1. In the Jesse dashboard: **⋮ (More options) → AI Assistants**. If Antigravity is listed, copy its setup. If not, use
   **Manual connection details** and **Copy token**:
   - Address: `http://localhost:9000/mcp`
   - Header: `Authorization: Bearer <token>`
2. In Antigravity: the **⋯** menu at the top of the Agent panel → **MCP Servers → Manage MCP Servers → View raw config**,
   and add (paste your token; keep any servers already there):

   ```json
   {
     "mcpServers": {
       "jesse": {
         "serverUrl": "http://localhost:9000/mcp",
         "headers": { "Authorization": "Bearer PASTE_TOKEN_HERE" }
       }
     }
   }
   ```

   Save, then refresh the MCP list; `jesse` should show its tools (run_backtest, import custom candle CSV, ...).
   If it doesn't connect, check Antigravity's MCP help page for the current field names (they have changed between
   versions) and send Claude a screenshot.
3. Test: ask the agent *"List the Jesse MCP tools you can see and the candles stored."* It should answer from Jesse,
   not guess.
4. If you change the Jesse PASSWORD, copy the token again (the old one stops working: error 401). "502 / MCP not running"
   = Jesse isn't running; `docker compose up -d`.

## 6. Ground rules for the Antigravity agent (paste as its first message, or into its rules)

```
You are a blind checker for an NQ / ES / CL futures research project. You only rebuild rules from the written spec you
are given, in Jesse, and report what you get. Do not look for or use any other code or results for the rule.
Do not optimise or change parameters. Set Jesse's fees to 0 and report raw points per trade; costs are applied elsewhere.
Data are 1-minute bars in US Central time; convert to UTC with daylight saving handled. Output: one CSV row per trade
(date, entry time + price, exit time + price, exit reason, points) and a short report (count, average points, win rate,
anything ambiguous in the spec and how you resolved it). Never touch broker, exchange or live-trading settings.
```

Results come back to Claude through you: save the CSV + report and upload them, or commit them to a branch of
`thebeginning` named `antigravity/<task>` (never to the `claude/...` branches).

## Fixes found during the first install (2026-10-17, done and working)

- **Password with a `$`** gets cut short by Docker (warning `The "j" variable is not set`): use letters, numbers, `!`, `_`, `-`.
- **`ports are not available ... 9001`** (Windows reserves that port): in `jesse-bot\docker\docker-compose.yml` delete the
  two lines `# LSP Port` and `- "9001:9001"` (editor code hints only; not needed), then `docker compose down` and
  `docker compose up -d`.
- **Two different tokens:** `LICENSE_API_TOKEN` in `.env` = the jesse.trade account token (https://jesse.trade/user/api-tokens);
  the token in Antigravity's config = the dashboard **MCP token** (Connect an assistant → Manual connection details →
  Copy token). The wrong one gives `Unauthorized`.
- **Antigravity (this version):** Customizations → MCP Servers → the 'copy config file path' icon; open that path in
  Notepad (`notepad <path>`), paste the JSON from section 5, save, restart Antigravity. The store (+) has no Jesse entry.
- Don't use 'Fix with Agent' or paste tokens into the Antigravity chat: that sends them to Google's servers.
- Docker Desktop's 'Gordon' assistant isn't needed; reject its requests.

## 7. What not to do

- No live trading or exchange API keys in Jesse (it trades crypto exchanges only; our trading stays in MultiCharts / Apex).
- Don't let it edit `thebeginning` strategy files or plan docs.
- Don't share keys (Alpha Vantage, OpenAI, Jesse token) in any chat.
