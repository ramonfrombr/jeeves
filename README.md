## Commands

### Initialize migrations

`flask --app migrate_app:create_app db init`

### Create a migration

`flask --app migrate_app:create_app db migrate -m "initial"`

### Run the shell

Comment the lines

```
loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app())
```

Run the following commands

```
export QUART_APP=jeeves.shell:create_app_for_shell`
```

```
quart shell
```

### Run the application

```
export QUART_APP=jeeves quart run
```

or

```
hypercorn jeeves:app
```

### Run the application using Docker

Build the image.

```
docker build -t quart-app .
```

Run the container.

```
docker run -p 8000:8000 --env-file .env quart-app
```
