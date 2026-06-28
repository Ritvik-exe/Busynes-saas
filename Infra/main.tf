# ========================== Terraform and AWS versions ==========================
terraform{
    required_providers{
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
    backend "s3"{
        bucket = "busynes-tf-state-ritvik-160835721559-eu-west-2-an"
        key = "global/s3/terraform.tfstate"
        region = "eu-west-2"
    }
}

# ========================== AWS Region ==========================
provider "aws" {
    region = "eu-west-2"
}

# ========================== S3 Bucket ==========================
resource "aws_s3_bucket" "invoice"{
    bucket = var.busynes_bucket

    tags = {
        Name = var.busynes_bucket
        Environment = "dev"
        Project = "busynes"
        managedby = "terraform"
    }
    }

# S3 Versioning
resource "aws_s3_bucket_versioning" "invoice_version"{
    bucket = aws_s3_bucket.invoice.id
    versioning_configuration{
        status = "Enabled"
    }
}

resource "aws_s3_bucket_public_access_block" "invoice_public_block"{
    bucket = aws_s3_bucket.invoice.id
    block_public_acls = true
    block_public_policy = true
    ignore_public_acls = true
    restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "invoice_cors"{
    bucket = aws_s3_bucket.invoice.id
    cors_rule {
        allowed_headers = ["*"]
        allowed_methods = ["GET", "PUT", "POST", "HEAD"]
        allowed_origins = ["https://busynes.com", "http://localhost:5173", "http://localhost:8080", "http://localhost:3000"]
        expose_headers = ["ETag"]
        max_age_seconds = 300
    }
}

# ========================== DynamoDB ========================== 
resource "aws_dynamodb_table" "memory"{
    name = var.busynes_db
    hash_key = "ClientID"
    range_key = "Timestamp"
    billing_mode = "PAY_PER_REQUEST"

    attribute {
        name = "ClientID"
        type = "S"
    }

    attribute {
        name = "Timestamp"
        type = "S"
    }

    tags = {
        Name = var.busynes_db
        Environment = "dev"
        Project = "busynes"
        managedby = "terraform"
    }
}

# ========================== IAM Roles ========================== 
resource "aws_iam_role" "busynes_lambda_role"{
    name = var.busynes_lambda_role
    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Action = "sts:AssumeRole",
                Effect = "Allow",
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
            }
        ]
    })
    tags = {
        Name = var.busynes_lambda_role
        Environment = "dev"
        Project = "busynes"
        managedby = "terraform"
    }
    }

resource "aws_iam_role" "github_action_role"{
    name = var.github_actions_role
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRoleWithWebIdentity"
                Effect = "Allow"
                Sid = ""
                Principal = {
                    Federated = aws_iam_openid_connect_provider.github_actions.arn
                }
                Condition = {
                    StringEquals = {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                    }
                    StringLike = {
                        "token.actions.githubusercontent.com:sub": "repo:Ritvik-exe/Busynes-saas:*"
                    }
                }

            }
    ]
    }
)

tags = {
    Name = var.github_actions_role
    Environment = "dev"
    Project = "busynes"
    managedby = "terraform"
}
}

# ========================== IAM policies Attachments ==========================
resource "aws_iam_role_policy_attachment" "busynes_lambda_s3"{
    role = aws_iam_role.busynes_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "busynes_lambda_dynamodb"{
    role = aws_iam_role.busynes_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "busynes_lambda_execution"{
    role = aws_iam_role.busynes_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "busynes_lambda_rekognition"{
    role = aws_iam_role.busynes_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "busynes_lambda_ses"{
    role = aws_iam_role.busynes_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

resource "aws_iam_role_policy_attachment" "busynes_github_action"{
    role = aws_iam_role.github_action_role.name
    policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# ========================== Lambda Function ==========================
data "archive_file" "lambda_zip"{
    type = "zip"
    source_file = "${path.module}/../Backend/lambda_function.py"
    output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "busynes_lambda_function"{
    filename = data.archive_file.lambda_zip.output_path
    function_name = var.busynes_lambda_function
    role = aws_iam_role.busynes_lambda_role.arn
    handler = "lambda_function.lambda_handler"
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256

    runtime = "python3.12"

    environment {
        variables = {
            TABLE_NAME = aws_dynamodb_table.memory.name
            INVOICE_BUCKET = aws_s3_bucket.invoice.id
        }
    }

    tags = {
        Name = var.busynes_lambda_function
        Environment = "dev"
        Project = "busynes"
        managedby = "terraform"
    }
}

# ========================== Lambda Trigger ==========================
resource "aws_lambda_permission" "invoice_trigger"{
    statement_id = var.busynes_lambda_trigger
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.busynes_lambda_function.arn
    principal = "s3.amazonaws.com"
    source_arn = aws_s3_bucket.invoice.arn
}

resource "aws_s3_bucket_notification" "bucket_notification"{
    bucket = aws_s3_bucket.invoice.id

    lambda_function {
        lambda_function_arn = aws_lambda_function.busynes_lambda_function.arn
        events = ["s3:ObjectCreated:*"]
        }
    depends_on = [aws_lambda_permission.invoice_trigger]
}

# ========================== HTTP API Gateway ==========================
resource "aws_apigatewayv2_api" "busynes_api"{
    name = var.busynes_api
    protocol_type = "HTTP"

    cors_configuration {
        allow_headers = ["content-type", "authorization"]
        allow_methods = ["GET", "POST", "PUT", "OPTIONS"]
        allow_origins = ["https://busynes.com", "http://localhost:5173", "http://localhost:8080", "http://localhost:3000"]
        max_age = 300
    }
}

resource "aws_apigatewayv2_integration" "busynes_api_integration"{
    api_id = aws_apigatewayv2_api.busynes_api.id
    integration_type = "AWS_PROXY"
    integration_method = "POST"
    integration_uri = aws_lambda_function.busynes_lambda_function.invoke_arn
    payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "busynes_api_route"{
    api_id = aws_apigatewayv2_api.busynes_api.id
    route_key = "ANY /"
    target = "integrations/${aws_apigatewayv2_integration.busynes_api_integration.id}"
}

resource "aws_apigatewayv2_stage" "busynes_api_stage"{
    api_id = aws_apigatewayv2_api.busynes_api.id
    name = "$default"
    auto_deploy = true

    tags = {
        Name = var.busynes_api
        Environment = "dev"
        Project = "busynes"
        managedby = "terraform"
    }
}


# Lambda Trigger for API Gateway
resource "aws_lambda_permission" "lambda_api_trigger"{
    statement_id = var.lambda_api_trigger
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.busynes_lambda_function.arn
    principal = "apigateway.amazonaws.com"
    source_arn = "${aws_apigatewayv2_api.busynes_api.execution_arn}/*/*"
}

# ========================== GitHub actions ==========================
resource "aws_iam_openid_connect_provider" "github_actions"{
    url = "https://token.actions.githubusercontent.com"
    client_id_list = [
        "sts.amazonaws.com"
    ]
    thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

# ========================== Cognito User Pool ==========================
resource "aws_cognito_user_pool" "busynes_user_pool"{
    name = var.cognito_user_pool
    username_attributes = ["email"]
    auto_verified_attributes = ["email"]

    email_configuration{
        email_sending_account = "DEVELOPER" 
        from_email_address = "support@busynes.com"
        source_arn = "arn:aws:ses:eu-west-2:160835721559:identity/busynes.com"
    }

    tags = {
        Name = var.cognito_user_pool
        Environment = "dev"
        Project = "busynes"
        managedby = "terraform"
    }
}

# ========================== Cognito User Pool Client ==========================
resource "aws_cognito_user_pool_client" "busynes_app_client"{
    name = var.cognito_app_client
    user_pool_id = aws_cognito_user_pool.busynes_user_pool.id
    generate_secret = false
}