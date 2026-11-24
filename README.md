# selfhost-stack

Production-ready base for any VPS/VDS: a server hardening script plus a modular Docker Compose infrastructure. Run one script on a fresh server, then start only the services you need.

## Features

### Server setup (`install.sh`)

- System update and handy tools: `btop`, `neofetch`, `fastfetch`, `eza`, `zsh` with Oh My Zsh.
- `ls` is replaced by [eza](https://github.com/eza-community/eza) for the new user (`home/.oh-my-zsh/custom/eza.zsh`, loaded by Oh My Zsh): long listing with hidden files by default, and the usual `ls` options keep working (`-t` and `-S` are translated, as eza gives them another meaning).
- Docker installed from the official repository (Engine, Buildx, Compose plugin).
- Dedicated user with `sudo` and `docker` groups, authorized by SSH key.
- SSH hardening: key authentication only, password authentication disabled, config checked with `sshd -t` before restarting to avoid locking you out.
- The `shared` Docker network is created for the whole stack.
- The content of `home/` is copied into the new user's home directory.

### Services (`home/internal/`)

Each service lives in its own folder with a `compose.yaml`, an `.env.example` when needed, and a README. Delete the ones you do not need.

| Category | Service | Description |
| --- | --- | --- |
| Routing | [Traefik](home/internal/routing/traefik/README.md) | Reverse proxy with automatic Let's Encrypt certificates |
| Git | [Forgejo](home/internal/git/forgejo/README.md) | Self-hosted Git forge |
| Git | [Forgejo Runner](home/internal/git/forgejo-runner/README.md) | CI/CD runner for Forgejo Actions, with its own Docker-in-Docker |
| Databases | [Postgres](home/internal/databases/postgres/README.md) | Global PostgreSQL database for every service |
| Databases | [Redis](home/internal/databases/redis/README.md) | Global cache/queue for every service |
| Monitoring | [Grafana](home/internal/monitoring/grafana/README.md) | Dashboards with pre-provisioned data sources and dashboards |
| Monitoring | [Prometheus](home/internal/monitoring/grafana/prometheus/README.md) | Metrics storage |
| Monitoring | [node-exporter](home/internal/monitoring/grafana/node-exporter/README.md) / [cAdvisor](home/internal/monitoring/grafana/cadvisor/README.md) / [postgres-exporter](home/internal/monitoring/grafana/postgres-exporter/README.md) / [redis-exporter](home/internal/monitoring/grafana/redis-exporter/README.md) | VPS, per-container, Postgres and Redis metrics |
| Monitoring | [blackbox-exporter](home/internal/monitoring/grafana/blackbox-exporter/README.md) | Availability and TLS certificate expiry of your public sites |
| Monitoring | [Loki](home/internal/monitoring/grafana/loki/README.md) / [Alloy](home/internal/monitoring/grafana/alloy/README.md) | Centralized logs of every container |
| Mail | [Stalwart](home/internal/mail/stalwart/README.md) | Mail server |
| Games | [Inari](home/internal/games/inari/README.md) | Proximity voice chat for game servers |

Databases and exporters are only reachable on the internal `shared` network; web services are exposed through Traefik over HTTPS.

## Compatibility

Debian 13 only.

## Quick start

1. Clone the repository on the server.
2. Copy `.env.example` to `.env` and fill in the variables:
   - `USERNAME`: name of the user created by the script.
   - `PASSWORD`: password of that user.
   - `PUBLIC_KEY`: public SSH key authorized for that user.
3. Run `./install.sh`.
4. **Before closing the session**, open a new terminal and check that you can log in as the new user with your SSH key.
5. Log in as that user, then for each service you want: go to `internal/<category>/<service>/`, copy `.env.example` to `.env`, fill it in and run `docker compose up -d`. Start [Traefik](home/internal/routing/traefik/README.md) first, as other web services depend on it.

## Layout

The content of `home/` is the content of the user home directory created at the end of the server setup (it is copied as-is into that user's home).

```
.
├── install.sh          # Server setup script
├── home/
│   ├── .claude/        # Claude Code instructions (only if used locally)
│   ├── .oh-my-zsh/     # Oh My Zsh custom files (eza alias for ls)
│   ├── dev/            # Your development workspace, one folder per project
│   ├── internal/       # Infrastructure services, one folder per category
│   │   ├── routing/    # Traefik
│   │   ├── git/        # Forgejo, Forgejo Runner
│   │   ├── databases/  # Postgres, Redis
│   │   ├── monitoring/ # Grafana, Prometheus, Loki…
│   │   ├── mail/       # Stalwart
│   │   └── games/      # Inari
│   └── prod/           # Your deployed programs and game servers
└── scripts/            # Hardening scripts (to come)
```

- [`home/dev/`](home/dev/README.md): workspace where you develop.
- [`home/internal/`](home/internal/README.md): internal services, not developed by you. You can delete or add configurations according to your needs.
- [`home/prod/`](home/prod/README.md): programs and websites subject to automatic deployment (e.g. a Forgejo/GitHub/Gitea action), plus game server folders such as Minecraft.
- `home/.claude/CLAUDE.md`: a copy of the maintainer's global Claude Code instructions, only relevant if Claude Code is installed locally.

## Networking

`install.sh` creates a Docker bridge network named `shared`. It is the internal network of the stack: services that need to talk to each other (or be routed by Traefik) must join it. Compose files declare it as external:

```yaml
networks:
  shared:
    name: shared
    external: true
```

## License

See [LICENSE](LICENSE).
