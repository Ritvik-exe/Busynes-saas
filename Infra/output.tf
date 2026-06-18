output "busynes_api_url"{
    description = "The public URL of the Busynes HTTP API"
    value = aws_apigatewayv2_stage.busynes_api_stage.invoke_url
}