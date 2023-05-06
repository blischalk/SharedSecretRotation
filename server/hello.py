import boto3
from flask import Flask
from flask_httpauth import HTTPTokenAuth

class Secrets:
    # Pull the secrets from Parameter Store when object instantiated
    def refresh(self):
        print("Retrieving secrets from Parameter Store")
        ssm = boto3.client('ssm', 'us-east-1')
        response = ssm.get_parameters(
                Name=['RotationExample'],WithDecryption=True
        )

        for parameter in response['Parameters']:
            self.secrets[parameter['Name']] = parameter['Value']

    # Method to get a secret from the object
    def secret(self, key):
        return self.secrets[key]

    # Acquire the secrets from AWS when the object is instantiated
    def __init__(self):
        self.secrets = {}
        self.refresh()

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
s = Secrets()

@auth.verify_token
def verify_token(token):
    # Try the secret we have in memory
    if token == s.secret('RotationExample'):
        print(f'Token match!')
        return True
    else:
    # If it fails, go refresh secrets from Parameter Store
        print(f'Token mis-match. Refreshing token')
        s.refresh()
        if token == s.secret('RotationExample'):
            return True
    return False

@app.route('/')
@auth.login_required
def hello():
    return 'Hello, World!'
