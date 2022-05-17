# asm_web_debug

# Prepare

Build an image used for running user code:

```
docker build -t asm_web_debug_executor -f docker/executor.dockerfile .
```

Initialize the database:

```
./manage.py flask db upgrade
```

# Run

```
./manage.py run --port 8080
```
Will run in development mode with live reload enabled on port 8080.

To create an administrator user run:
```
./manage.py flask create-admin
```

# Stress tests

First start the system in test mode so that it creates a new database and populates it with
the necessary data:

```
./manage.py run -t
```

To run the stress tests use something like this:

```
poetry run ./tests/interactive_debugger/run.py -n 100 --arch avr5 --profile SingleStep
```
