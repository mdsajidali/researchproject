job "expense" {
  datacenters = ["dc1"]
  type = "service"

  group "app" {

    network {
      mode = "host"
    }

    volume "pgdata" {
      type      = "host"
      read_only = false
      source    = "pgdata_v2"
    }

    task "db" {
      driver = "docker"

      config {
        image = "postgres:15"
        network_mode = "host"
        volumes = ["local/pgdata:/var/lib/postgresql/data"]
      }

      env {
        POSTGRES_DB       = "expensedb"
        POSTGRES_USER     = "expense"
        POSTGRES_PASSWORD = "expensepass"
      }

      resources {
        cpu    = 200
        memory = 256
      }
    }

    task "web" {
      driver = "docker"

      config {
        image = "mdsajidali/expense-tracker:1.1"
        network_mode = "host"
        #volumes = ["local/.env:/app/.env"]
        command = "/bin/sh"
        args    = ["local/entry.sh"]
      }

      env {
        DEBUG                     = "True"
        DJANGO_SUPERUSER_USERNAME = "admin"
        DJANGO_SUPERUSER_EMAIL    = "admin@example.com"
        DJANGO_SUPERUSER_PASSWORD = "adminpass"

        DB_NAME     = "expensedb"
        DB_USER     = "expense"
        DB_PASSWORD = "expensepass"
        DB_HOST     = "127.0.0.1"
        DB_PORT     = "5432"
        ALLOWED_HOSTS = "*,localhost,127.0.0.1,0.0.0.0,app,192.168.74.128"
        # For POSTs later (login/forms), add your IP to CSRF trusted origins:
        CSRF_TRUSTED_ORIGINS = "http://192.168.74.128:8000,http://localhost:8000,http://127.0.0.1:8000"
      }

      resources {
        cpu    = 300
        memory = 512
      }

      template {
        destination = "local/entry.sh"
        perms       = "755"
        data = <<-EOT
        #!/bin/sh
        echo "Waiting for Postgres..."
        until python3 -c "import socket; socket.create_connection(('127.0.0.1', 5432), timeout=2)" >/dev/null 2>&1; do
        echo "Postgres not ready, waiting..."
        sleep 3
        done
        echo "DB up. Setting open host policy..."
        #  Force Django to accept any host at runtime
        export DJANGO_ALLOWED_HOSTS="*"
        export ALLOWED_HOSTS="*"
        export PYTHONUNBUFFERED=1
        echo "Running migrations & collectstatic..."
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        exec gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:8000
      EOT
      }
    }
  }
}

