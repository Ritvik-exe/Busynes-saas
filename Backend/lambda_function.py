# Importing Libraries
import json
import boto3
import datetime
import os
import re
import logging
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import stripe
import base64

# Initializing AWS Clients
s3_client = boto3.client('s3')
dynamo_resource = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamo_resource.Table(table_name)
ses_client = boto3.client('ses')
rekog_client = boto3.client('rekognition')
cognito_client = boto3.client('cognito-idp')
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Main Lambda Function
def lambda_handler(event, context):
    try:
        # Variables initialization
        timestamp = datetime.datetime.now().isoformat()
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        month_date = datetime.date.today().strftime('%Y-%m')
        today_amount = Decimal('0.00')
        month_amount = Decimal('0.00')
        if 'Records' in event:
            email_address = 'ritvikyalala@gmail.com'
            invoice_total = Decimal('0.00')
            all_amounts = []

            # Getting S3 Bucket and File Name
            bucket_name = event['Records'][0]['s3']['bucket']['name']
            file_name = event['Records'][0]['s3']['object']['key']
            path = file_name.split('/')
            if len(path) > 1:
                ClientID = path[-2]
                clean_file_name = path[-1]
                user_pool_id = os.environ.get('USER_POOL_ID')
                try:
                    cognito_user = cognito_client.admin_get_user(
                        UserPoolId = user_pool_id,
                        Username = ClientID
                    )

                    email_address = ''
                    for attr in cognito_user.get('UserAttributes', []):
                        if attr['Name'] == 'email':
                            email_address = attr['Value']
                            break
                except Exception as e:
                    print(f'Error getting user info: {e}')

            else:
                ClientID = 'Admin'
                clean_file_name = file_name

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
                        'ClientID' : ClientID,
                        'Timestamp' : timestamp,
                        'Amount' : invoice_total,
                        'Filename' : file_name
                    }
                )

                # Fetching all items from table that meets with criteria
                response = table.query(
                    KeyConditionExpression = Key('ClientID').eq(ClientID) & Key('Timestamp').begins_with(month_date)

                )

                # Summing all amounts of today
                for item in response['Items']:
                    month_amount += item['Amount']
                    if item['Timestamp'].startswith(today_date):
                        today_amount += item['Amount']

                print(f'Today invoice total = {today_amount}')
                print(f'This month invoice total = {month_amount}')

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
                            <h2 style="margin:0;">Busynes</h2>
                        </div>
                        <p>Hello, your invoice has been processed successfully.</p>
                        <p><strong>File:</strong> {file_name}</p>
                        <p><strong>Total Detected:</strong></p>
                        <div class="amount">£{invoice_total}</div>
                        <p><strong>Today invoices Total:</strong> £{today_amount}</p>
                        <p><strong>This Month's Total:</strong> £{month_amount}</p>
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
                Source = 'support@busynes.com',

                Destination = {
                    'ToAddresses':[email_address]
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
        else:
            invoice_list = []
            method = event.get('requestContext',{}).get('http',{}).get('method', 'GET')
            path = event.get('requestContext',{}).get('http',{}).get('path', '/')

            # GET method used to fetch invoice data for client
            if method == 'GET' and path == '/':
                ClientID = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub')
                if not ClientID:
                    ClientID = event.get('queryStringParameters',{}).get('client_id', 'Admin')

                response = table.query(
                    KeyConditionExpression = Key('ClientID').eq(ClientID) & Key('Timestamp').begins_with(month_date)
                )

                for items in response['Items']:
                    invoice_list.append({ 'Timestamp': items['Timestamp'], 'Amount': float(items['Amount']), 'Filename': items['Filename'] })
                    month_amount += items['Amount']
                    if items['Timestamp'].startswith(today_date):
                        today_amount += items['Amount']

                return {
                    'statusCode' : 200,
                    'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                    'body' : json.dumps({'ClientID' : ClientID, 'This_Month_Total' : float(month_amount), 'Today_Total' : float(today_amount), 'Invoices' : invoice_list})
                }

            # POST method used to create a new client in DynamoDB
            elif method == 'POST' and path == '/':
                # Filtering out valid user to upload invoices
                user_id = event.get('requestContext',{}).get('authorizer',{}).get('jwt',{}).get('claims',{}).get('sub')
                if not user_id:
                    user_id = event.get('queryStringParameters',{}).get('client_id', 'Admin')
                user_email = event.get('requestContext',{}).get('authorizer',{}).get('jwt',{}).get('claims',{}).get('email','')
                user_plan_query = table.get_item(Key = {'ClientID' : user_id, 'Timestamp' : 'USER_PLAN'})
                if user_plan_query:
                    user_plan = user_plan_query.get('Item', {}).get('plan', 'Free')

                count_check = table.query(KeyConditionExpression = Key('ClientID').eq(user_id) & Key('Timestamp').begins_with(month_date), Select = 'COUNT')
                count = count_check.get('Count', 0)

                if user_email == 'ritvikyalala@gmail.com' or user_email.endswith('@busynes.com'):
                    user_plan = 'Pro'
                if user_plan != 'Pro' and count >= 10:
                    return {
                        'statusCode' : 403,
                        'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                        'body' : json.dumps({'error': "Must upgrade to 'The Sunday Saver' plan to upload more than 10 invoices."})
                    }
                else: 
                    # Generating presigned URL for client to upload invoice
                    bucket_name = os.environ.get('INVOICE_BUCKET')
                    body_data = json.loads(event.get('body', '{}'))
                    file_name = body_data.get('file_name')
                    file_type = body_data.get('file_type')

                    user_id = event.get('requestContext',{}).get('authorizer',{}).get('jwt',{}).get('claims',{}).get('sub')
                    s3_key = f'uploads/{user_id}/{file_name}'
                    response = s3_client.generate_presigned_url(
                        'put_object',
                        Params = {'Bucket' : bucket_name, 'Key' : s3_key, 'ContentType' : file_type},
                        ExpiresIn = 300
                    )

                    return {
                        'statusCode' : 200,
                        'headers' : {'Content-Type' : 'Application/json','Access-Control-Allow-Origin': '*'},
                        'body' : json.dumps({'upload_url' : response, 'file_name' : s3_key})
                    }

            # POST method used to create a checkout session for client
            elif method == 'POST' and path == '/checkout':
                body_data = json.loads(event.get('body', '{}'))
                price_id = body_data.get('price_id')
                user_id = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub')
                session = stripe.checkout.Session.create(
                    payment_method_types = ['card'],
                    line_items = [{'price' : price_id, 'quantity': 1}],
                    mode = 'subscription',
                    success_url = 'https://busynes.com/dashboard.html?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url = 'https://busynes.com/pricing.html',
                    client_reference_id = user_id
                )
                return {
                    'statusCode' : 200,
                    'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'}, 
                    'body' : json.dumps({'checkout_url' : session.url})
                }
            
            # POST method used to handle stripe webhooks
            elif method == 'POST' and path == '/webhook/stripe':
                amount_paid = Decimal('0.00')
                payload = event.get('body', '')
                if event.get('isBase64Encoded', False) == True:
                    payload = base64.b64decode(payload)
                sig_header = event.get('headers', {}).get('stripe-signature') or event.get('headers', {}).get('Stripe-Signature')
                webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
                try:
                    stripe_event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
                except ValueError:
                    return {
                        'statusCode' : 400,
                        'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                        'body' : json.dumps({'error' : 'Invalid payload'})
                    }
                except stripe.error.SignatureVerificationError:
                    return {
                        'statusCode' : 400,
                        'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},                            'body' : json.dumps({'error' : 'Invalid signature'})
                    }

                if stripe_event.type == 'checkout.session.completed':
                    session = stripe_event.data.object
                    user_id = session.client_reference_id
                    customer_name = session.customer_details.name
                    user_email = session.customer_details.email
                    amount_paid = Decimal(session.amount_total) / 100
                    invoice_id = session.invoice
                    success_email_html = f"""
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
                                    <h2 style="margin:0; color: #187c13;">Busynes</h2>
                                </div>
                                <p>Hello {customer_name},</p>
                                <p>Thank you for subscribing to <strong>The Sunday Saver Plan</strong>!</p>
                                <p>Your payment has been successfully processed, and your account has been upgraded to <strong>Pro</strong>. Unlimited invoice processing is now active on your dashboard.</p>
                                <div class="amount">£{amount_paid:.2f} Paid</div>
                                <p style="margin-top: 15px; font-size: 13px; color: #555;">
                                    <strong>Billing Status:</strong> Active<br>
                                    <strong>Invoice ID:</strong> {invoice_id}
                                </p>
                                <div class="footer">
                                    Busynes for Business — Reclaiming your Sunday afternoons.
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    table.put_item(
                        Item = {
                            'ClientID' : user_id,
                            'Timestamp' : 'USER_PLAN',
                            'plan' : 'Pro'
                        }
                    )

                    ses_client.send_email(
                        Source = 'support@busynes.com',
                        Destination = {'ToAddresses' : [user_email]},
                        Message = {
                            'Subject':{
                                'Data' : 'Payment Successful !' 
                            },
                            'Body':{
                                'Html':{
                                    'Data' : success_email_html
                                }
                            } 
                        }
                    )

                elif stripe_event.type == 'invoice.payment_failed':
                    invoice = stripe_event.data.object
                    user_email = invoice.customer_email
                    customer_name = invoice.customer_name or "Valued Customer"
                    response = cognito_client.list_users(
                        UserPoolId = os.environ.get('USER_POOL_ID'),
                        Filter = f'email = "{user_email}"'
                        )
                    amount_due = Decimal(invoice.amount_due) / 100
                    invoice_id = invoice.id
                    failure_email_html = f"""
                    <html>
                    <head>
                        <style>
                            .wrapper {{ font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 30px; }}
                            .container {{ background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #ef4444; max-width: 500px; margin: auto; }}
                            .header {{ border-bottom: 2px solid #ef4444; padding-bottom: 10px; margin-bottom: 20px; }}
                            .alert {{ font-size: 24px; color: #ef4444; font-weight: bold; }}
                            .footer {{ font-size: 10px; color: #999; margin-top: 20px; text-align: center; }}
                        </style>
                    </head>
                    <body>
                        <div class="wrapper">
                            <div class="container">
                                <div class="header">
                                    <h2 style="margin:0; color: #ef4444;">Busynes Alert</h2>
                                </div>
                                <p>Hello {customer_name},</p>
                                <p>We were unable to process your payment for <strong>The Sunday Saver Plan</strong>.</p>
                                <div class="alert">Payment Declined</div>
                                <p>Your bank or card issuer declined the transaction of <strong>£{amount_due:.2f}</strong>.</p>
                                <p>Please log in to your Busynes billing portal or check your Stripe subscription settings to update your card. Your account has entered a 3-day grace period to prevent service disruption before reverting to the Free tier limits.</p>
                                <p style="margin-top: 15px; font-size: 13px; color: #555;">
                                    <strong>Invoice ID:</strong> {invoice_id}
                                </p>
                                <div class="footer">
                                    Busynes for Business — Reclaiming your Sunday afternoons.
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    if response.get('Users'):
                        user_id = response['Users'][0]['Username']
                        table.put_item(
                            Item = {
                                'ClientID' : user_id,
                                'Timestamp' : 'USER_PLAN',
                                'plan' : 'Free'
                            }
                        )

                        ses_client.send_email(
                        Source = 'support@busynes.com',
                        Destination = {'ToAddresses' : [user_email]},
                        Message = {
                            'Subject':{
                                'Data' : 'Payment Failed !' 
                            },
                            'Body':{
                                'Html':{
                                    'Data' : failure_email_html
                                }
                            } 
                        }
                    )

                return {
                    'statusCode' : 200,
                    'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                    'body' : json.dumps({'success' : 'Webhook received and processed'})
                }

            # Support email requests
            elif method == 'POST' and path == '/support':
                body_data = json.loads(event.get('body', {}))
                user_email = body_data.get('email')
                user_message = body_data.get('message')
                request_type = body_data.get('type', 'callback')

                if not user_email or not user_message:
                    return {
                        'statusCode' : 400,
                        'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                        'body' : json.dumps({'error' : 'Email and message fields are required.'})
                    }

                support_html_email = f"""
                <html>
                <head>
                    <style>
                        .wrapper {{ font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 30px; }}
                        .container {{ background-color: #ffffff; padding: 25px; border-radius: 10px; border: 1px solid #e0e0e0; max-width: 550px; margin: auto; }}
                        .header {{ border-bottom: 2px solid #10b981; padding-bottom: 12px; margin-bottom: 20px; }}
                        .badge {{ display: inline-block; padding: 4px 8px; background-color: #e6f4ea; color: #137333; font-size: 11px; font-weight: bold; border-radius: 4px; text-transform: uppercase; margin-bottom: 15px; }}
                        .info-label {{ font-size: 12px; color: #666; font-weight: bold; margin-bottom: 4px; }}
                        .info-value {{ font-size: 14px; color: #333; margin-bottom: 15px; background: #f9f9f9; padding: 10px; border-radius: 6px; border: 1px solid #f1f1f1; }}
                        .footer {{ font-size: 10px; color: #999; margin-top: 25px; text-align: center; border-top: 1px solid #eee; padding-top: 15px; }}
                    </style>
                </head>
                <body>
                    <div class="wrapper">
                        <div class="container">
                            <div class="header">
                                <h2 style="margin:0; color: #111;">Busynes Notification</h2>
                            </div>
                            
                            <div class="badge">{request_type} request</div>
                            
                            <div class="info-label">SENDER EMAIL:</div>
                            <div class="info-value"><strong>{user_email}</strong></div>
                            
                            <div class="info-label">MESSAGE DETAILS:</div>
                            <div class="info-value" style="white-space: pre-wrap;">{user_message}</div>
                            
                            <div class="footer">
                                Busynes Internal Support Alert — Reply directly to this email to contact the user [1].
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """

                ses_client.send_email(
                    Source = 'support@busynes.com',
                    Destination = {'ToAddresses' : ['support@busynes.com']},
                    ReplyToAddresses = [user_email],
                    Message = {'Subject': {'Data' : f'[Busynes Alert] New {request_type.capitalize()} request from {user_email}'}},
                    Body = {'Html' : {'Data' : support_html_email}}
                )

                return {
                    'statusCode' : 200,
                    'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                    'body' : json.dumps({'success' : 'Support request sent successfully'})
                }
  
            # DELETE method used to delete invoice from DynamoDB and S3
            elif method == 'DELETE' and path == '/':
                user_id = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub')
                if not user_id:
                    user_id = event.get('queryStringParameters',{}).get('client_id', 'Admin')
                bucket_name = os.environ.get('INVOICE_BUCKET')
                body_data = json.loads(event.get('body', '{}'))
                timestamp = body_data.get('timestamp')
                filename = body_data.get('filename')

                table.delete_item(Key={'ClientID' : user_id, 'Timestamp' : timestamp})

                s3_client.delete_object(
                    Bucket = bucket_name,
                    Key = filename
                )

                return {
                    'statusCode' : 200,
                    'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
                    'body' : json.dumps({'message' : 'Invoice successfully deleted'})
                }
        
    # Error handling
    except Exception as e:
        return {
            'statusCode' : 500,
            'headers' : {'Content-Type' : 'Application/json', 'Access-Control-Allow-Origin' : '*'},
            'body' : json.dumps({'Error' : str(e)})
        }
        