# Cloud Computing Homework — Docker, Docker Swarm, Docker Hub, AWS EC2

**Name:** Seng Kimoun
**Course:** Cloud Computing — Docker Compose & Docker Swarm
**Docker Hub repository:** https://hub.docker.com/repositories/unixquantum/myhwpython



---

## 1. The application

A two-service application:

| Service | Image | Role |
|---|---|---|
| `web` | built from `app/Dockerfile` (Python 3.12 + Flask + gunicorn) | Serves HTTP on port 5000, published as 8080 locally |
| `redis` | `redis:7-alpine` | Backing store holding a page-visit counter |

The web page shows a visit counter, the app version, and the container hostname
that served the request (useful for seeing Swarm load-balance across replicas).
The counter is stored in Redis with `appendonly yes`, and Redis's `/data`
directory is a **named volume** (`redis_data`), so the count survives restarts.

Files: https://hub.docker.com/repositories/unixquantum/myhwpython

```
.
├── app/
│   ├── app.py            # Flask application
│   ├── Dockerfile        # production image (non-root user, gunicorn, healthcheck)
│   ├── requirements.txt
│   └── .dockerignore
├── docker-compose.yml    # Part 1
├── stack.yml             # Part 2 (Swarm stack)
└── README.md
```

---

## 2. Part 1 — Running locally with Docker Compose

```bash
docker compose up -d --build
docker compose ps
```
- screenshots/path-1/path1-1-docker-compose-up.png

Open <http://localhost:8080>. Refresh a few times — the counter increases.
 - screenshots/path-1/path1-browser-port-8080.png

**Proving the named volume persists data:**
```bash
docker compose down          # containers removed, named volume kept
docker compose up -d
```
- screenshots/path-1/path1-2-docker-compose-down-and-up-again.png


Reload the page: the counter continues from where it left off instead of
restarting at 1. (`docker compose down -v` would delete the volume and reset it.)

**How the two services find each other:** both are attached to the custom
network `appnet`, so the app connects to the hostname `redis`, which Docker's
embedded DNS resolves to the Redis container.

---

## 3. Part 2 — Running as a Docker Swarm stack
```bash
docker compose down                       # free port 8080 first
docker swarm init                         # single-node Swarm
docker stack deploy -c stack.yml ccstack

docker stack services ccstack
docker service ls
docker service ps ccstack_web
```
- screenshots/path-2/path-2-first-run-docker-swarm-1replica.png

The application is still reachable at <http://localhost:8080>. 
- screenshots/path-2/path-2-first-browser-stack.png

**Scale to 3 replicas:**
```bash
docker service scale ccstack_web=3
docker service ps ccstack_web
docker stack services ccstack             # 3 tasks, all "Running"
```
- screenshots/path-2/path-2-scal-3-and-delete1con.png

**Self-healing:** kill one task's container directly and watch Swarm replace it
with no further command from me:

```bash
docker ps --filter name=ccstack_web       # pick one container ID
docker rm -f 750e360c39bb
docker service ps ccstack_web             # killed task = "Failed"/"Shutdown",
                                          # a new task is already "Running"
```
- screenshots/path-2/path-2-scal-3-and-delete1con.png
- screenshots/path-2/path-2-second-browser-stack.png.png

---

## 4. Part 3 — Publishing the image to Docker Hub

```bash
docker login

# v1.0.0
docker build -t unixquantum/myhwpython:v1.0.0 ./app
docker push unixquantum/myhwpython:v1.0.0
```
- screenshots/path-3/path-3-docker-login-and-build-imagev1.png
- screenshots/path-3/path-3-docker-push-v1.png

The repository was set to **Public** in Docker Hub → repository → *Settings* →
*Visibility*, then verified with a clean pull:

```bash
docker rmi unixquantum/myhwpython:v1.0.0
docker pull unixquantum/myhwpython:v1.0.0   # succeeds with no login
```
- screenshots/path-3/path-3-pull-image-from-dockerhub.png

**v2.0.0** — the change made for the second version was: _describe your change, e.g.
"the page title and the `X-App-Version` response header now read v2.0.0"_.

```bash
# after editing the app (or the APP_VERSION/PAGE_TITLE defaults in app.py)
docker build -t unixquantum/myhwpython:v2.0.0 ./app
docker push unixquantum/myhwpython:v2.0.0
```
- screenshots/path-3/path-3-docker-build-and-push-v2.png
- screenshots/path-3/path-3-images-all-2v-on-docker-hub.png
The repository's *Tags* page now lists both `v1.0.0` and `v2.0.0`.

---

## 5. Part 4 — Deploying to AWS EC2

**Instance:** `t3.micro`, Amazon Linux 2023, free-tier eligible, default VPC.

**Security group inbound rules:**

| Type | Port | Source | Why |
|---|---|---|---|
| SSH | 22 | My IP only (`x.x.x.x/32`) | Administration |
| HTTP | 80 | 0.0.0.0/0 | The application, reachable from any browser |

**On the instance:**

```bash
ssh -i my-key.pem ec2-user@<EC2-PUBLIC-IP>

sudo dnf install -y docker                 # Amazon Linux 2023
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user           # then log out and back in
```

**Run the published image:**

```bash
docker network create appnet
docker run -d --name redis --network appnet \
  redis:7-alpine redis-server --appendonly yes

docker pull unixquantum/myhwpython:v2.0.0
docker run -d --name web --network appnet -p 80:5000 \
  -e REDIS_HOST=redis -e APP_VERSION=v2.0.0 \
  -e PAGE_TITLE="Cloud Computing Homework - v2.0.0 (EC2)" \
  unixquantum/myhwpython:v2.0.0

docker ps
```

Container port 5000 is published as port 80 on the instance, which matches the
HTTP rule in the security group.

**Verification:** from my own laptop's browser (not from the instance), I opened
`http://<EC2-PUBLIC-IP>` and the application responded — see screenshot (d).

**Cleanup:** after capturing the evidence I stopped/terminated the instance so it
does not accrue charges.

---

## 6. Screenshots

| File | Shows |
|---|---|
| `screenshots/a-compose-local.png` | The application in a browser at `localhost:8080`, plus `docker compose ps` |
| `screenshots/b-swarm-3-replicas.png` | `docker service ps ccstack_web` with 3 running replicas |
| `screenshots/c-dockerhub-tags.png` | The Docker Hub repository page showing `v1.0.0` and `v2.0.0` |
| `screenshots/d-ec2-browser.png` | The application in a browser at the EC2 public IP |

---

## 7. Troubleshooting notes

- **Port 8080 already in use** — `docker compose down` before `docker stack deploy`; both publish the same port.
- **`docker stack deploy` says "image not found"** — on a single-node Swarm the locally built image is used; if the tag was never built or pushed, build it first.
- **Counter shows "Redis is not reachable"** — the app and Redis are not on the same network, or the Redis container is not running.
- **EC2 page does not load** — check the security group's HTTP rule, that `docker ps` shows the container up, and that you used the **public** IP.
