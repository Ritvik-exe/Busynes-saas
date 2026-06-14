# Importing Libraries
import json
import boto3
import datetime
import os
import re
from decimal import Decimal

# Initializing AWS Clients
s3_client = boto3.client('s3')

dynamo_resource = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamo_resource.Table(table_name)

ses_client = boto3.client('ses')
rekog_client = boto3.client('rekognition')

# Main Lambda Function
def lambda_handler(event, context):
    try:
        invoice_total = Decimal('0.00')
        timestamp = datetime.datetime.now().isoformat()
        all_amounts = []

        # Getting S3 Bucket and File Name
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_name = event['Records'][0]['s3']['object']['key']

        # Validating File Extension
        allowed_extensions = ('jpeg', 'png', 'jpg')
        if file_name.split('.')[-1].lower() not in allowed_extensions:
            return {
                'statusCode': 400,
                'message' : f'File type not supported! Please upload only {allowed_extensions}.'
            }
        else:
            # Calling Rekognition on the uploaded file
            response = rekog_client.detect_text(
                Image = {
                    'S3Object' :{
                        'Bucket': bucket_name,
                        'Name' : file_name
                    }
                }
            )

            print(f'AI response : {response}')

            # Extracting Total Amount from Rekognition Response
            for item in response['TextDetections']:
                if item['Type'] == 'LINE':
                    matches = re.findall(r'\d+[.,]\d{2}', item['DetectedText'])
                    if matches:
                        clean_value = matches[0].replace(',', '.')
                        all_amounts.append(Decimal(clean_value))
            
            if all_amounts:
                invoice_total = max(all_amounts)
                print(f'Total: {invoice_total}')
            else:
                invoice_total = Decimal('0.00')

            # Putting the extracted data into DynamoDB
            response = table.put_item(
                Item = {
                    'ClientID' : 'User_1',
                    'Timestamp' : timestamp,
                    'Amount' : invoice_total,
                    'Filename' : file_name
                }
            )

            # PREPPED FOR PYTHON F-STRING (DOUBLE BRACES INCLUDED)
            html_template = f"""
        <html>
        <head>
            <style>
                .wrapper {{ font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 30px; }}
                .container {{ background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; max-width: 500px; margin: auto; }}
                .header {{ border-bottom: 2px solid #10b981; padding-bottom: 10px; margin-bottom: 20px; }}
                .amount {{ font-size: 24px; color: #10b981; font-weight: bold; }}
                .footer {{ font-size: 10px; color: #999; margin-top: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <div class="header">
                        <h2 style="margin:0;">Busynes Platform</h2>
                    </div>
                    <p>Hello, your invoice has been processed successfully.</p>
                    <p><strong>File:</strong> {file_name}</p>
                    <p><strong>Total Detected:</strong></p>
                    <div class="amount">£{invoice_total}</div>
                    <div class="footer">
                        Busynes for Business — Reclaiming your Sunday afternoons.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Sending Email Notification via SES
        response = ses_client.send_email(
            Source = 'busynes.platform@gmail.com',

            Destination = {
                'ToAddresses': ['ritvikyalala@gmail.com']
            },

            Message = {
                'Subject' : {
                    'Data' : f'Invoice processed - {file_name}'
                },
        
                'Body' : {
                    'Html' : {
                        'Data' : html_template
                    }
                }
            },

        )
    # Error handling
    except Exception as e:
        print(f'Error : {str(e)}')
        return {
            'statusCode' : 500,
            'Error' : f'Error: {str(e)}'
        }
        