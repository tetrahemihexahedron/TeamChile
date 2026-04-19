# Team Chile

[Desert Dev Hackathon](https://www.nmtechtalks.com/desert-dev-lab)

## Food Connect

...

## Development

Copy `template.env` to `.env` and set environment variables there.

To connect to the database on Supabase, use the host, database and user listed on Supabase for the 'Session pooler' connection method (which were written on the board earlier, along with the password).

Generally, instead of connecting to Supabase, you'll want to connect to a database running locally for development, so changes aren't persisted. To do that, you can use the same environment variables as for Supabase, except change `DB_HOST` to `db`, which is the name of the Docker service (defined in [compose.yml](compose.yml)) for the local database:

```
DB_HOST=db
```

Run the Docker containers with

```
docker compose up
```

This will start first a container running postgres and then a container running the Django app. When running them for the first time, a database will be created and populated with data.

:exclamation: Note: If the Dockerfile, [entrypoint script](entrypoint.sh), or python dependencies have changed since you last ran the container, you may need to tell Docker to rebuild the image with the `--build` flag:

```
docker compose up --build
```

Then visit http://localhost:8000.

To bring the container down when you're done:

```
docker compose down
```

This will preserve the database and any changes that you may have made to it, so that the next time you run `docker compose up`, the state of the app should be the same.

If instead you want to delete the database, so that you can reset it to its initial state, use the `-v` flag:

```
docker compose down -v
```

Then the next time you run `docker compose up`, you should get a fresh copy of the database.

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

### Viewing the local database

If you wish, you can connect a database viewer, like [DBeaver](https://dbeaver.io), to port 5432 on localhost to inspect changes to the database running in the postgres container.
