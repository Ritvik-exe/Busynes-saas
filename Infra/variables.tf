# ================= Variables =================

# S3 Bucket
variable "busynes_bucket"{
    type = string
    description = "busynes-invoice"
    default = "busynes-invoice"
}

# DynamoDB
variable "busynes_db"{
    type = string
    description = "busynes-db"
    default = "busynes-db"
}

# Lambda Role
variable "busynes_lambda_role"{
    type = string
    description = "busynes-lambda-role"
    default = "busynes-lambda-role"
}

# Lambda Function
variable "busynes_lambda_function"{
    type = string
    description = "busynes-lambda-function"
    default = "busynes-lambda-function"
}

# Lambda Trigger
variable "busynes_lambda_trigger" {
    type = string
    description = "busynes-lambda-trigger"
    default = "busynes-lambda-trigger"
}

# HTTP API Gateway
variable "busynes_api"{
    type = string
    description = "busynes-api"
    default = "busynes-api"
}

# Lambda API Trigger 
variable "lambda_api_trigger"{
    type = string
    description = "lambda-api-trigger"
    default = "lambda-api-trigger"
}