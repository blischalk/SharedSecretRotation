# Zero Downtime API Shared Secret Rotation

## Setup

1. Create a AWS parameter
2. Update `client.py` and `server.py` with the AWS region the parameter is in and the name of the parameter
3. Start up the client and server

## Startup

In a terminal run:

```
export FLASK_APP=server
export FLASK_ENV=development
flask run
```

In another terminal run:

```
python3 client.py
```

4. Change the secret in AWS parameter store
5. Observe the client and server terminal windows gracefully handle the secret rotation

