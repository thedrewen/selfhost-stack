# redis

Redis instance that can be used as a global cache/queue by the other services of the stack.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. Start it: `docker compose up -d`.

## Behavior

- No password. Redis is only reachable from containers on the `shared` network (host `redis`, port `6379`) and from the server itself on `127.0.0.1:6379`. It is never exposed to the internet: do not change the port binding to `0.0.0.0`.
- Protected mode is disabled, otherwise Redis would refuse connections from other containers when no password is set.
- Persistence is enabled (append-only file) in `./data`. Back it up if the content matters.
- It is a single global instance: to avoid collisions between services, give each one its own database number (`/0` to `/15`) or key prefix.

## Usage

```
redis://redis:6379/0
```

From the server:

```
redis-cli -h 127.0.0.1
```
