# forgejo

Self-hosted Git forge ([Forgejo](https://forgejo.org/)), routed by Traefik. Its CI/CD workflows are executed by [forgejo-runner](../forgejo-runner/README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Traefik](../../routing/traefik/README.md) is running.
2. Copy `.env.example` to `.env` and set `FORGEJO_DOMAIN` (e.g. `git.example.com`).
3. Start it: `docker compose up -d`.
4. Open `https://<FORGEJO_DOMAIN>` and finish the installation wizard. Set the base URL to `https://<FORGEJO_DOMAIN>/` and the SSH port to `222`.

## Behavior

- The web interface is exposed by Traefik on `https://$FORGEJO_DOMAIN` with a Let's Encrypt certificate (container port `3000`).
- Git over SSH is published on port `222` of the server (port `22` is used by the server's own SSH): `git clone ssh://git@<FORGEJO_DOMAIN>:222/<user>/<repo>.git`. Open this port in your firewall.
- Data (repositories, database, configuration) is stored in `./forgejo`. Back it up. By default Forgejo uses SQLite; the global [Postgres](../../databases/postgres/README.md) can be selected in the wizard instead.
- The container runs as `1000:1000` (`USER_UID` / `USER_GID`); `./forgejo` must be writable by this user.
