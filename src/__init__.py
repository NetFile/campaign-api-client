import json
import logging

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('../logs/log.txt', 'a')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
# Set the logging level to logging.DEBUG for verbose output, or to logging.INFO for less verbose output
logger.setLevel(logging.INFO)

with open('../resources/config.json', 'r') as f:
    config = json.load(f)

# Variables below are set in resources/config.json file
env = 'preview'

# Subscription id can be stored in config
subscription_id = config[env.upper()]['SUBSCRIPTION_ID']
# Base URL of the API. Example - "https://netfile.com/filing/api"
api_url = config[env.upper()]['API_URL']
# Username credential to authenticate against the Campaign API
api_key = config[env.upper()]['API_KEY']
# Password credential to authenticate against the Campaign API
api_password = config[env.upper()]['API_PASSWORD']
