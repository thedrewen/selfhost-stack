# selfhost-stack
Production-ready base for any VPS/VDS: server hardening script plus a modular Docker Compose infrastructure.

## Layout

The content of `home/` is the content of the user home directory created at the end of the server setup (it is copied as-is into that user's home).

- `home/.claude/CLAUDE.md`: global Claude Code instructions, only relevant if Claude Code is installed locally on the machine. It is a copy of the maintainer's global `~/.claude/CLAUDE.md`.
- `home/dev/`: see [home/dev/README.md](home/dev/README.md)
- `home/internal/`: see [home/internal/README.md](home/internal/README.md)
- `home/prod/`: see [home/prod/README.md](home/prod/README.md)
