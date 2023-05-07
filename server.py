from flask import Flask
from flask_httpauth import HTTPTokenAuth
import secretscache as sc

# Initialize some globals
api_token_key = 'RotationExample'
aws_region    = 'us-east-1'

# Initialize a Flask app 
app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

# Load up our secrets on boot
s = sc.SecretsCache([api_token_key], aws_region)

@auth.verify_token
def verify_token(token):
    print(f'Using token: {token} for demonstration purposes only. Don\'t do this in production!')
    # Try the most current secret we have in memory
    if token == s.secret(api_token_key):
        print(f'Current token match!')
        return True
    elif token == s.secret(api_token_key, 'Previous'):
        print(f'Previous token match!')
        return True
    else:
        # If current and previous fail, go refresh secrets from Parameter Store
        # Retry current which may now be new if it was updated
        print(f'Token mis-match. Refreshing token')
        s.refresh()
        if token == s.secret(api_token_key):
            return True
    return False

@app.route('/')
@auth.login_required
def main():
    return 'Open Sesame!'
