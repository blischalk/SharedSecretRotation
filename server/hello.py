import boto3
from flask import Flask
from flask_httpauth import HTTPTokenAuth

class Secrets:
    # Pull the secrets from Parameter Store when object instantiated
    def refresh(self):
        print("Retrieving secrets from Parameter Store")

        # Get current and previous versions of each secret
        for key in self.secrets:
            self.secrets[key] = self.get_secret_versions(key)

    # Looks up current and previous version for a secret
    def get_secret_versions(self, key):
        values = {'Current': None, 'Previous': None}

        ssm = boto3.client('ssm', 'us-east-1')

        response = ssm.get_parameter(
                Name=key,WithDecryption=True
        )

        if response and response['Parameter']['Value']:
            values['Current'] = response['Parameter']['Value']

            # Parameter store increments the version each time a secret is
            # updated and it starts with 1 for the first secret
            # Because of this we only lookup a previous version if the secret is
            # the second version or more
            if response['Parameter']['Version'] > 1:
                response = ssm.get_parameter(
                        Name=f'{key}:{(response["Parameter"]["Version"]-1)} ',
                        WithDecryption=True
                )

                if response and response['Parameter']['Value']:
                    values['Previous'] = response['Parameter']['Value']

        return values

    # Method to get a secret from the object
    def secret(self, key, version='Current'):
        return self.secrets[key][version]

    # Acquire the secrets from AWS when the object is instantiated
    def __init__(self, keys):
        self.secrets = {}
        for key in keys:
            self.secrets[key] = {}
        self.refresh()

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
api_token_key='RotationExample'

# Load up our secrets on boot
s = Secrets([api_token_key])

@auth.verify_token
def verify_token(token):
    # Try the most current secret we have in memory
    if token == s.secret(api_token_key):
        print(f'Current token match!')
        return True
    elif token == s.secret(api_toekn_key, 'Previous'):
        print(f'Previous token match!')
        return True
    else:
        # If current and previous fail, go refresh secrets from Parameter Store
        print(f'Token mis-match. Refreshing token')
        s.refresh()
        if token == s.secret(api_token_key):
            return True
    return False

@app.route('/')
@auth.login_required
def hello():
    return 'Hello, World!'
