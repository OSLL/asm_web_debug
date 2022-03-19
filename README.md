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
- Bash
```
./manage.py run --port 8080
```
Will run in development mode with live reload enabled on port 8080.

To create an administrator user run:
```
./manage.py flask create-admin
```

# Tests
- For headless run:
```
./scripts/run_selenium.sh
```
- For run in Docker
```
docker exec -t asm_web_debug_web_1 ./scripts/run_selenium.sh
```
- For direct run:
```
cd src/tests/selenium
./scripts/run_tests.sh http://127.0.0.1:5100
```

# Deployment
Domain: asm.moevm.info
```bash
./scripts/start_deploy.sh ${branch}
```
