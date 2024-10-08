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
    password = event.get('password')

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
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': identifier,
                'PASSWORD': password,
            }
        )

        logging.error(response)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
        }

    except botocore.exceptions.ClientError as error:
        logging.error(error)

        if error.response['Error']['Code'] == 'UserNotFoundException':
            logging.error(error)
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': "{ 'message': 'Unauthorized' }",
            }

        return internal_error(error)

    except Exception as error:
        return internal_error(error)


def internal_error(error):
    logging.error(error)
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': "{ 'message': 'Internal server error' }",
    }