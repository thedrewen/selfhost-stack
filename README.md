# selfhost-stack
Production-ready base for any VPS/VDS: server hardening script plus a modular Docker Compose infrastructure.

## Compatibility

Only compatible with Debian 13.

## Layout

The content of `home/` is the content of the user home directory created at the end of the server setup (it is copied as-is into that user's home).

- `home/.claude/CLAUDE.md`: global Claude Code instructions, only relevant if Claude Code is installed locally on the machine. It is a copy of the maintainer's global `~/.claude/CLAUDE.md`.
- `home/dev/`: see [home/dev/README.md](home/dev/README.md)
- `home/internal/`: Docker Compose configurations of the internal services. The list of available configurations is in [home/internal/README.md](home/internal/README.md); you can delete or add configurations according to your needs.
- `home/prod/`: see [home/prod/README.md](home/prod/README.md)

## Configuration

Copy `.env.example` to `.env` and fill in the variables before running `install.sh`:

- `USERNAME`: name of the user created by the script.
- `PASSWORD`: password of that user.
- `PUBLIC_KEY`: public SSH key authorized for that user.

## Networking

`install.sh` creates a Docker bridge network named `shared`. It is the internal network of the stack: services that need to talk to each other (or be routed by Traefik) must join it. Compose files declare it as external:

```yaml
networks:
  shared:
    name: shared
    external: true
```
