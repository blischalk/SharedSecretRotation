import requests
import secretscache as sc
import time

# Initialize some globals
api_token_key = 'RotationExample'
aws_region    = 'us-east-1'

api_endpoint='http://localhost:5000/'
s = sc.SecretsCache([api_token_key], aws_region)

# Loop forever
while True:
    print(f'Trying to access api using secret: {s.secret(api_token_key)}. For demonstration purposes only. Don\'t log secrets!')
    r = requests.get(api_endpoint, headers={"Authorization": f'Bearer {s.secret(api_token_key)}'})
    print(f'Request was {r.status_code}')
    time.sleep(5)

if __name__ == '__main__':
    sys.exit(main())
