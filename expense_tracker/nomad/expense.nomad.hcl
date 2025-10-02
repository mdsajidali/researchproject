job "expenses" {
  datacenters = ["dc1"]

  group "db" {
    task "postgres" {
      driver = "docker"
      config {
        image = "postgres:15"
        port_map { pg = 5432 }
      }
      env {
        POSTGRES_DB = "expensedb"
        POSTGRES_USER = "expense"
        POSTGRES_PASSWORD = "expensepass"
      }
      resources { network { port "pg" { to = 5432 } } }
      volume_mount {
        volume      = "pgdata"
        destination = "/var/lib/postgresql/data"
      }
    }

    volume "pgdata" {
      type      = "host"
      read_only = false
      source    = "pgdata"
    }
  }

  group "web" {
    network {
      port "http" { to = 8000, host_network = "default" }
    }
    task "web" {
      driver = "docker"
      config {
        image = "<dockerhub-username>/expense-tracker:1.0"
        ports = ["http"]
      }
      env {
        DEBUG       = "False"
        SECRET_KEY  = "prod-secret-change-me"
        ALLOWED_HOSTS = "localhost,127.0.0.1"
        DB_NAME     = "expensedb"
        DB_USER     = "expense"
        DB_PASSWORD = "expensepass"
        DB_HOST     = "alloc.db.service.consul" # replace with service discovery if you wire Consul
        DB_PORT     = "5432"
      }
      # simple healthcheck hitting "/"
      service {
        name = "expenses-web"
        port = "http"
        check {
          type     = "http"
          path     = "/"
          interval = "10s"
          timeout  = "2s"
        }
      }
      resources { cpu = 500; memory = 512 }
      # count = 2  # scalable instances when you want
    }
  }
}
