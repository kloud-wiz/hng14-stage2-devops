# FIXES.md — Bug Report & Resolutions

All bugs found in the starter repository, documented with file, line number, issue, and fix applied.
Line numbers marked as (original) refer to the buggy starter code before fixes were applied.

---

## BUG 1 — Redis host hardcoded to `localhost` in API

- **File:** `api/main.py`
- **Line:** 7 (original)
- **Problem:** `redis.Redis(host="localhost", port=6379)` — inside Docker, `localhost` refers to the container itself, not the Redis service. The API would fail to connect to Redis entirely.
- **Fix:** Replaced with `host=os.getenv("REDIS_HOST", "redis")` so the host is read from an environment variable, defaulting to the Docker Compose service name `redis`. Now at line 10.

---

## BUG 2 — Redis password never used in API

- **File:** `api/main.py`
- **Line:** 7 (original)
- **Problem:** The `.env` file defined `REDIS_PASSWORD` but the Redis client in the API never passed a password. Any Redis instance configured with `requirepass` would reject all connections.
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD", "")` to the Redis client constructor. Now at line 12.

---

## BUG 3 — `os` module imported but never used in API

- **File:** `api/main.py`
- **Line:** 3 (original)
- **Problem:** `import os` was present but `os` was never referenced anywhere in the file.
- **Fix:** `os` is now actively used via `os.getenv()` calls for Redis configuration across lines 10–12.

---

## BUG 4 — Response bytes not decoded in API

- **File:** `api/main.py`
- **Line:** 22 (original)
- **Problem:** `status.decode()` was called manually to convert Redis bytes to string. With `decode_responses=True` set on the Redis client, responses are already strings — calling `.decode()` on a string raises `AttributeError: 'str' object has no attribute 'decode'`, causing a 500 error on every job status request.
- **Fix:** Added `decode_responses=True` to the Redis client constructor at line 13. Removed the manual `.decode()` call.

---

## BUG 5 — Queue key inconsistency between API and Worker

- **File:** `api/main.py`, `worker/worker.py`
- **Line:** `api/main.py` line 10 (original), `worker/worker.py` line 16 (original)
- **Problem:** The queue key was named `"job"` (singular) in one service and `"jobs"` in another — the API and worker were pushing to and popping from different keys, meaning jobs were never actually processed.
- **Fix:** Standardised to `"jobs"` in both files. Now at `api/main.py` line 20 and `worker/worker.py` line 30.

---

## BUG 6 — Redis host hardcoded to `localhost` in Worker

- **File:** `worker/worker.py`
- **Line:** 5 (original)
- **Problem:** Same issue as BUG 1 — `redis.Redis(host="localhost", port=6379)` fails inside Docker because `localhost` resolves to the worker container itself, not the Redis service.
- **Fix:** Replaced with `host=os.getenv("REDIS_HOST", "redis")`. Now at line 8.

---

## BUG 7 — Redis password never used in Worker

- **File:** `worker/worker.py`
- **Line:** 5 (original)
- **Problem:** Same issue as BUG 2 — Redis client had no password, causing connection rejection when Redis is configured with `requirepass`.
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD", "")` to the Redis client constructor. Now at line 10.

---

## BUG 8 — Worker response bytes decoded manually

- **File:** `worker/worker.py`
- **Line:** 18 (original)
- **Problem:** `job_id.decode()` was called manually on the value returned from `brpop`. Same fragile pattern as BUG 4 — with `decode_responses=True` this raises `AttributeError`.
- **Fix:** Added `decode_responses=True` to the Redis client at line 11. Removed the manual `.decode()` call. `brpop` result is unpacked directly at line 32.

---

## BUG 9 — No graceful shutdown handling in Worker

- **File:** `worker/worker.py`
- **Line:** (missing in original)
- **Problem:** The worker had no signal handlers. When Docker stops a container it sends `SIGTERM` — without a handler the worker would be killed mid-job, potentially leaving a job permanently stuck in `queued` state.
- **Fix:** Added `signal.signal(signal.SIGTERM, handle_shutdown)` and `signal.signal(signal.SIGINT, handle_shutdown)` with a clean exit handler. Now at lines 14–19.

---

## BUG 10 — API URL hardcoded to `localhost` in Frontend

- **File:** `frontend/app.js`
- **Line:** 5 (original)
- **Problem:** `const API_URL = "http://localhost:8000"` — inside Docker, the frontend container cannot reach the API via `localhost`. Each container is an isolated network namespace.
- **Fix:** Replaced with `process.env.API_URL || "http://api:8000"`. Now at line 6.

---

## BUG 11 — Frontend port hardcoded

- **File:** `frontend/app.js`
- **Line:** 21 (original)
- **Problem:** `app.listen(3000)` hardcoded the port. Passing `FRONTEND_PORT` as an environment variable into the container caused the app to listen on the wrong port, breaking Docker's port mapping.
- **Fix:** App now listens on `process.env.PORT || 3000` internally at line 37. `FRONTEND_PORT` is only used for the host-side port mapping in `docker-compose.yml` line 85.

---

## BUG 12 — `console.error` placed in wrong scope in Frontend status route

- **File:** `frontend/app.js`
- **Line:** 16 (original)
- **Problem:** `console.error("Error fetching status:", err.message)` was inside the `try` block where `err` does not exist. `err` is only defined in the `catch` block. This caused a `ReferenceError: err is not defined` on every call to `/status/:id`, crashing the response before any data was returned to the browser.
- **Fix:** Moved `console.error` into the `catch (err)` block. Now correctly at line 27. Submit route catch block also has proper error logging at line 17.

---

## BUG 13 — Python dependencies unpinned in API

- **File:** `api/requirements.txt`
- **Lines:** 1–3 (original)
- **Problem:** `fastapi`, `uvicorn`, and `redis` had no version pins. Future builds could silently install breaking versions, making builds non-reproducible.
- **Fix:** Pinned to `fastapi==0.111.0`, `uvicorn==0.29.0`, `redis==5.0.4`.

---

## BUG 14 — Python dependency unpinned in Worker

- **File:** `worker/requirements.txt`
- **Line:** 1 (original)
- **Problem:** `redis` had no version pin. Same reproducibility risk as BUG 13.
- **Fix:** Pinned to `redis==5.0.4`.

---

## BUG 15 — No newline at end of `worker/requirements.txt`

- **File:** `worker/requirements.txt`
- **Line:** 1 (original)
- **Problem:** File had no trailing newline, which violates POSIX text file standards and can cause issues with some tooling.
- **Fix:** Added trailing newline.

---

## BUG 16 — Real secret committed to repository

- **File:** `.env`
- **Line:** 3 (original)
- **Problem:** `REDIS_PASSWORD=supersecretpassword123` was committed directly in the repository. This is a critical security violation — secrets in git history are permanently exposed.
- **Fix:** Added `.env` and `*.env` to `.gitignore`. Created `.env.example` with placeholder values. The `.env` file is never committed.

---

## BUG 17 — No `.gitignore` present

- **File:** (missing in original)
- **Problem:** No `.gitignore` existed, meaning `node_modules/`, `.env` files, `__pycache__/`, and other unwanted artifacts could be accidentally committed.
- **Fix:** Created `.gitignore` covering `.env`, `*.env`, `__pycache__/`, `*.pyc`, `node_modules/`, and `.DS_Store`.

---

## BUG 18 — No health check endpoints in API or Frontend

- **File:** `api/main.py`, `frontend/app.js`
- **Line:** (missing in original)
- **Problem:** Neither service exposed a `/health` endpoint. Docker HEALTHCHECK instructions and `depends_on: condition: service_healthy` in Compose require a reliable endpoint to probe.
- **Fix:** Added `GET /health` to API at lines 32–39 — it pings Redis and returns 503 if unavailable. Added `GET /health` to Frontend at lines 32–35 returning `{"status": "ok"}`.

---

## BUG 19 — Wrong HTTP status code for missing job

- **File:** `api/main.py`
- **Line:** 19 (original)
- **Problem:** When a job ID was not found in Redis, the API returned `{"error": "not found"}` with a **200 OK** status code. A missing resource should return **404 Not Found**. This breaks any client or integration test that checks HTTP status codes.
- **Fix:** Imported `HTTPException` from FastAPI at line 1 and replaced the plain return with `raise HTTPException(status_code=404, detail="job not found")` at line 29.

---

## BUG 20 — Redis healthcheck variable substitution failure

- **File:** `docker-compose.yml`
- **Line:** 11 (original)
- **Problem:** The Redis healthcheck used exec form `["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]`. Exec form does not invoke a shell, so `${REDIS_PASSWORD}` was passed as a literal string instead of being expanded. Redis received the text `${REDIS_PASSWORD}` as the password, causing every healthcheck to fail. Since the API and worker depend on Redis being healthy via `condition: service_healthy`, neither service ever started.
- **Fix:** Switched to `["CMD-SHELL", "redis-cli -a $$REDIS_PASSWORD ping"]` at line 11. `CMD-SHELL` runs through `/bin/sh` enabling variable expansion. `$$REDIS_PASSWORD` uses double `$$` so Docker Compose passes a literal `$` to the shell rather than substituting it at parse time.

---

## BUG 21 — Worker crashes on job processing error

- **File:** `worker/worker.py`
- **Line:** 24 (original)
- **Problem:** The main processing loop had no error handling. If any exception occurred during `process_job` — such as a Redis connection drop or unexpected data — the entire worker process would crash and stop processing jobs permanently.
- **Fix:** Wrapped the loop body in a `try/except Exception` block at lines 29–35. Errors are logged and the worker sleeps 1 second before continuing, ensuring a single failure does not kill the worker.

---

## BUG 22 — Redis connection created at module level with no error handling in API

- **File:** `api/main.py`
- **Line:** 6 (original)
- **Problem:** The Redis client was instantiated once at module load time. If Redis was not fully ready at startup the API crashed. If Redis went down and recovered, the stale client had no reconnection logic. The `/health` endpoint also returned `{"status": "ok"}` unconditionally without actually verifying Redis connectivity, making the Docker healthcheck meaningless.
- **Fix:** Moved Redis instantiation into a `get_redis()` factory function at lines 8–14, called fresh per request. Updated `/health` at lines 32–39 to call `r.ping()` and return HTTP 503 if Redis is unreachable.

---

## BUG 23 — Worker logs not visible due to Python output buffering

- **File:** `docker-compose.yml`
- **Line:** 54 (original worker environment block)
- **Problem:** Python buffers stdout/stderr when not writing to a real terminal. Inside a container there is no TTY, so all `print()` output was buffered and never flushed to Docker's log collector. The worker appeared completely silent with no way to confirm it was processing jobs.
- **Fix:** Added `PYTHONUNBUFFERED=1` to the worker service environment at line 58. This disables Python's output buffering, ensuring all print statements are immediately visible in `docker logs`.
