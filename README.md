# TeamChile

Desert Dev Hackathon

## Development

Copy `template.env` to `.env` and set environment variables.

Run the docker container with

```
docker compose up
```

Note: If the Dockerfile has changed since you last ran the container, you may need to tell Docker to rebuild the image with the `--build` flag:

```
docker compose up --build
```

Then visit http://localhost:8000.

To bring the container down when you're done:

```
docker compose down
```

Some other docker commands that may be helpful:

- To see containers on your computer:

```
docker ps -a
```

- To delete a container:

```
docker rm <container_id_or_name>
```

- To see images on your computer:

```
docker image list
```

- To delete an image:

```
docker image rm <image_id_or_name>
```

- To clean up some of the artifacts that Docker leaves behind:

```
docker system prune
```
