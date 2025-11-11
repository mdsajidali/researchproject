job "expense-app" {
  datacenters = ["dc1"]
  type = "service"

  group "app" {
    count = 1

    network {
      mode = "host"
      port "http" {
        static = 8000
      }
    }

    task "app" {
      driver = "docker"

      config {
        image = "mdsajidali/expense-tracker:1.1"
        ports = ["http"]
      }

      env {
        DJANGO_SECRET_KEY    = "change-me"
        DJANGO_DEBUG         = "False"
        DJANGO_ALLOWED_HOSTS = "*"
        DB_NAME              = "expense"
        DB_USER              = "expense"
        DB_PASSWORD          = "expensepass"
        DB_HOST              = "172.31.28.246"
        DB_PORT              = "5432"
      }

      resources {
        cpu    = 400
        memory = 512
      }

      service {
        name = "expense-app"
        port = "http"
        check {
          name     = "http"
          type     = "http"
          path     = "/"
          interval = "5s"
          timeout  = "2s"
        }
      }
    }
  }
}

