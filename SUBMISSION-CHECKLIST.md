# Submission Checklist — Docker & Docker Swarm Homework

**Name:** _YOUR NAME_  **Date:** _____________
**Docker Hub repository:** https://hub.docker.com/r/unixquantum/myhwpython
**EC2 public IP used for the demo:** _____________

> Only tick a box after you have actually performed and verified that step.

| ✔ | Item | Evidence |
|---|---|---|
| ☑ | `docker-compose.yml` defines two correctly connected services with a named volume | `docker-compose.yml`, screenshot (a) |
| ☐ | Application was confirmed reachable locally with `docker compose up` | screenshot (a) |
| ☐ | The application was deployed as a Swarm stack with `docker stack deploy` | `stack.yml`, `docker stack services` output |
| ☐ | The application service was scaled to 3 replicas, confirmed with `docker service ps` | screenshot (b) |
| ☐ | A killed task was confirmed to be automatically replaced by Swarm | `docker service ps` output in README §3 |
| ☐ | The image was built, tagged with my Docker Hub username, and pushed as v1 and v2 | screenshot (c) |
| ☐ | The Docker Hub repository is Public and was pulled after a local `docker rmi` | README §4 |
| ☐ | An EC2 instance is running Docker with a security group allowing HTTP on the application's port | README §5 |
| ☐ | The application was confirmed reachable from a browser at the EC2 public IP | screenshot (d) |
| ☐ | The EC2 instance was stopped or terminated after capturing evidence | — |
| ☐ | All required screenshots and the README are included in the submission | `screenshots/`, `README.md` |
