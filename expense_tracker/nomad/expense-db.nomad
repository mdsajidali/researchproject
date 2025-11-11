job "expense-db" {
  datacenters = ["dc1"]
  type = "service"

  group "db" {
    count = 1

    network {
      mode = "host"
      port "db" {
        static = 5432
      }
    }

    task "postgres" {
      driver = "docker"

      config {
        image = "postgres:15"
        ports = ["db"]
        volumes = ["/opt/nomad/volumes/pgdata:/var/lib/postgresql/data"]
      }

      env {
        POSTGRES_DB       = "expense"
        POSTGRES_USER     = "expense"
        POSTGRES_PASSWORD = "expensepass"
      }

      resources {
        cpu    = 300
        memory = 512
      }

      service {
        name = "expense-db"
        port = "db"
        check {
          name     = "pg-tcp"
          type     = "tcp"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}

