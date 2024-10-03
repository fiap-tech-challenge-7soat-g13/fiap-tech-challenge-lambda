import json
import logging
import os

import boto3
import botocore.exceptions

cognito = boto3.client('cognito-idp')

USER_POOL_ID = os.environ.get('USER_POOL_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')


def lambda_handler(event, context):
    identifier = event.get('email')

    if not identifier:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': "{ 'message': 'Identifier (Email) is required' }",
        }

    try:
        response = cognito.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='CUSTOM_AUTH',
            AuthParameters={'USERNAME': identifier}
        )
        logging.success('Code 200: ' + error)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response),
        }

    except botocore.exceptions.ClientError as error:
        logging.error(error)

        if error.response['Error']['Code'] == 'UserNotFoundException':
            logging.error('Code 401: ' + error)
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': "{ 'message': 'Unauthorized' }",
            }

        return internal_error(error)

    except Exception as error:
        return internal_error(error)


def internal_error(error):
    logging.error('Code 500: ' + error)
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': "{ 'message': 'Internal server error' }",
    }