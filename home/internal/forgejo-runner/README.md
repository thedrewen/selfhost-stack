# forgejo-runner

[Forgejo Runner](https://forgejo.org/docs/latest/admin/runner-installation/) that executes the CI/CD workflows (Forgejo Actions) of your Forgejo instance, for example the automatic deployments of `home/prod/`.

It runs two containers:

- `docker_dind`: a Docker-in-Docker daemon, in which the jobs run. Jobs are isolated from the host Docker.
- `runner`: the Forgejo runner, which talks to that daemon (`DOCKER_HOST=tcp://docker-in-docker:2375`).

## Setup

1. Make sure `./data` is writable by the user of the runner container (`1000:1000`): `sudo chown -R 1000:1000 data`.
2. Create a runner registration token in your Forgejo instance (Site/Organization/Repository settings > Actions > Runners).
3. Register the runner (creates `data/.runner`):

   ```
   docker compose run --rm runner forgejo-runner register --no-interactive \
     --instance https://<your-forgejo> --token <token> --name <runner-name> --config runner-config.yml
   ```

4. Start it: `docker compose up -d`.

## Configuration

`data/runner-config.yml` is the runner configuration. The main settings:

- `runner.capacity`: number of jobs run at the same time (`1`).
- `runner.timeout`: maximum duration of a job (`3h`).
- `runner.labels`: the labels the runner accepts, as `label:docker://image`. A workflow with `runs-on: ubuntu-latest` runs in the `catthehacker/ubuntu:act-latest` image. Add labels to offer other environments.

## Security

- `docker_dind` runs `privileged` and its API is exposed **without TLS** on port `2375`. The port is not published and is only reachable by the `runner` container: never publish it.
- Jobs run in the nested Docker, not on the host Docker, but anyone who can push a workflow to a repository served by this runner can run code on the server. Register it only on instances and repositories you trust.

## Known points to check

- `runner.envs.DOCKER_HOST` in `runner-config.yml` is `tcp://dind_container.docker.internal:2375` and `container.options` maps that name to the host (`host-gateway`). Since the DinD port is not published on the host, jobs that use Docker themselves (e.g. `docker build`) may fail to reach the daemon. Check this the first time a workflow builds an image.
