module "db" {
  source  = "terraform-aws-modules/rds/aws"
  identifier = "${var.name}-db"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  name     = var.db_name
  username = var.db_user
  password = var.db_password
  port     = 5432
  publicly_accessible = false

  vpc_security_group_ids = [aws_security_group.db.id]
  subnet_ids             = module.vpc.private_subnets
}

resource "aws_security_group" "db" {
  name        = "${var.name}-db-sg"
  description = "DB access from ECS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Postgres from ECS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
