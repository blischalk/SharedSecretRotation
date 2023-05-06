import boto3
import requests
import time
from datetime import datetime, timedelta

class Secrets:
    # Pull the secrets from Parameter Store when object instantiated
    def refresh(self):
        print("Retrieving secrets from Parameter Store")
        ssm = boto3.client('ssm', 'us-east-1')
        response = ssm.get_parameters(
                Names=['RotationExample'],WithDecryption=True
        )

        for parameter in response['Parameters']:
            self.secrets[parameter['Name']] = parameter['Value']

        # Set the updated_at property to now
        self.updated_at = datetime.now()

    # Method to get a secret from the object
    def secret(self, key):
        # Check if our secrets need a refresh on access
        if self.stale_secrets():
            self.refresh()
        return self.secrets[key]

    def stale_secrets(self):
        if datetime.now() > self.updated_at + timedelta(minutes = self.ttl):
            print("TTL expired!")
            return True
        else:
            return False

    # Acquire the secrets from AWS when the object is instantiated
    def __init__(self):
        # Set a 1 minute ttl on refreshing secrets
        self.ttl = 1
        self.updated_at = None
        self.secrets = {}
        self.refresh()

api_endpoint='http://localhost:5000/'
s = Secrets()


# Loop forever
while True:
    print(f'Trying to access api')
    r = requests.get(api_endpoint, headers={"Authorization": f'Bearer {s.secret("RotationExample")}'})
    print(f'First request status code: {r.status_code}')
    if r.ok == False:
        s.refresh()
        print(f'Trying to access api after refresh')
        r = requests.get(api_endpoint, headers={"Authorization": f'Bearer {s.secret("RotationExample")}'})
        print(f'Second request status code: {r.status_code}')

    time.sleep(5)

if __name__ == '__main__':
    sys.exit(main())
