# stalwart

Mail server ([Stalwart](https://stalw.art/)), routed by Traefik for its web interface.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Traefik](../../routing/traefik/README.md) is running.
2. Copy `.env.example` to `.env` and set `MAIL_HOSTNAME` (e.g. `mail.example.com`).
3. Start it: `docker compose up -d`.

## Behavior

- Published ports: `25` (SMTP), `465` (SMTPS) and `993` (IMAPS). Open them in your firewall; many hosting providers block outbound port `25` by default.
- The web interface (container port `8080`) is exposed by Traefik on `https://$MAIL_HOSTNAME` with a Let's Encrypt certificate.
- Configuration is stored in `./etc` and data (mailboxes) in `./data`. Back up both.

## Storage

Stalwart can use the global [Postgres](../../databases/postgres/README.md) and [Redis](../../databases/redis/README.md) of the stack (host `postgres` / `redis` on the `shared` network) instead of its embedded storage. Create a dedicated database and user for it in Postgres first.

## DNS

The hostname must have a DNS record pointing to the server. For reliable delivery you will also need the usual mail records (MX, SPF, DKIM, DMARC) and a reverse DNS (PTR) matching `MAIL_HOSTNAME`; see the Stalwart documentation.
