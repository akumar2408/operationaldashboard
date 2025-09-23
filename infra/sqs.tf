resource "aws_sqs_queue" "jobs" {
  name = "${var.name}-jobs"
}
