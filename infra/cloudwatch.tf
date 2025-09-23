resource "aws_cloudwatch_event_rule" "scheduled" {
  name                = "${var.name}-scheduled"
  schedule_expression = "rate(1 day)"
}
