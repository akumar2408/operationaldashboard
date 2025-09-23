resource "aws_ecs_cluster" "this" {
  name = var.name
}

resource "aws_iam_role" "task_exec" {
  name = "${var.name}-task-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_exec_attach" {
  role       = aws_iam_role.task_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecr_repository" "api" { name = "${var.name}-api" }
resource "aws_ecr_repository" "web" { name = "${var.name}-web" }

# Load Balancer
resource "aws_lb" "alb" {
  name               = "${var.name}-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = module.vpc.public_subnets
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_security_group" "alb" {
  name   = "${var.name}-alb-sg"
  vpc_id = module.vpc.vpc_id

  ingress { from_port = 80, to_port = 80, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 0,  to_port = 0,  protocol = "-1",  cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_lb_target_group" "api" {
  name     = "${var.name}-api-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  health_check { path = "/"; matcher = "200" }
}

resource "aws_lb_target_group" "web" {
  name     = "${var.name}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  health_check { path = "/"; matcher = "200-399" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Path routing: /api -> api service
resource "aws_lb_listener_rule" "api_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern { values = ["/api*", "/api/*"] }
  }
}

# Security group for ECS tasks
resource "aws_security_group" "ecs" {
  name   = "${var.name}-ecs-sg"
  vpc_id = module.vpc.vpc_id
  egress { from_port = 0, to_port = 0, protocol = "-1", cidr_blocks = ["0.0.0.0/0"] }
}

# Task Definitions
resource "aws_ecs_task_definition" "api" {
  family                   = "${var.name}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu    = 512
  memory = 1024
  execution_role_arn = aws_iam_role.task_exec.arn
  container_definitions = jsonencode([{
    name  = "api",
    image = "${aws_ecr_repository.api.repository_url}:prod",
    essential = true,
    portMappings = [{ containerPort = 8000, hostPort = 8000 }],
    environment = [
      { name = "SECRET_KEY", value = "CHANGE_ME" },
      { name = "ACCESS_TOKEN_EXPIRE_MINUTES", value = "60" },
      { name = "POSTGRES_USER", value = var.db_user },
      { name = "POSTGRES_PASSWORD", value = var.db_password },
      { name = "POSTGRES_DB", value = var.db_name },
      { name = "POSTGRES_HOST", value = module.db.db_instance_address },
      { name = "POSTGRES_PORT", value = "5432" },
      { name = "AWS_REGION", value = var.aws_region },
      { name = "S3_BUCKET", value = var.s3_bucket },
      { name = "CORS_ORIGINS", value = "*" }
    ]
  }])
  runtime_platform { operating_system_family = "LINUX"  }
}

resource "aws_ecs_task_definition" "web" {
  family                   = "${var.name}-web"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu    = 256
  memory = 512
  execution_role_arn = aws_iam_role.task_exec.arn
  container_definitions = jsonencode([{
    name  = "web",
    image = "${aws_ecr_repository.web.repository_url}:prod",
    essential = true,
    portMappings = [{ containerPort = 80, hostPort = 80 }]
  }])
  runtime_platform { operating_system_family = "LINUX"  }
}

# Services
resource "aws_ecs_service" "api" {
  name            = "${var.name}-api"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }
  depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "web" {
  name            = "${var.name}-web"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets = module.vpc.public_subnets
    security_groups = [aws_security_group.ecs.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name   = "web"
    container_port   = 80
  }
  depends_on = [aws_lb_listener.http]
}
