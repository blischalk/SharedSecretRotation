import boto3
from datetime import datetime, timedelta

class SecretsCache:
    # Acquire the secrets from AWS when the object is instantiated
    def __init__(self, keys, region, ttl=1):
        # Initialize a dictionary for each secret key name
        self.secrets    = {}
        for key in keys:
            self.secrets[key] = {}

        self.region     = region
        # Set a 1 minute ttl on refreshing secrets
        self.ttl        = ttl
        self.updated_at = None

        # Fetch the secrets
        self.refresh()

    # Pull the secrets from Parameter Store when object instantiated
    def refresh(self):
        print("Retrieving secrets from Parameter Store")

        # Get current and previous versions of each secret
        for key in self.secrets:
            self.secrets[key] = self.__get_secret_versions(key)

        # Set the updated_at property to now
        self.updated_at = datetime.now()

    # Method to get a secret from the object
    # Default to getting the Current secret
    def secret(self, key, version='Current'):
        # Check if our secrets need a refresh on access
        if self.__stale_secrets():
            self.refresh()

        return self.secrets[key][version]

    def __stale_secrets(self):
        if datetime.now() > self.updated_at + timedelta(minutes = self.ttl):
            print("TTL expired!")
            return True
        else:
            return False

    # Looks up current and previous version for a secret
    def __get_secret_versions(self, key):
        values = {'Current': None, 'Previous': None}

        ssm = boto3.client('ssm', self.region)

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

