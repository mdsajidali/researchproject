job "cadvisor" {
  datacenters = ["dc1"]
  type        = "system"

  group "cad" {
    network {
      mode = "host"
      port "http" {
        static = 8080
      }
    }

    task "cadvisor" {
      driver = "docker"

      config {
        image   = "gcr.io/cadvisor/cadvisor:v0.49.1"
        ports   = ["http"]
        volumes = [
          "/:/rootfs:ro",
          "/var/run:/var/run:rw",
          "/sys:/sys:ro",
          "/var/lib/docker/:/var/lib/docker:ro",
          "/dev/disk/:/dev/disk:ro"
        ]
        args = [
          "--docker_only=true",
          "--housekeeping_interval=10s",
          "--disable_metrics=percpu,sched,tcp,udp,process"
        ]
      }

      resources {
        cpu    = 200
        memory = 256
      }

      service {
        name = "cadvisor"
        port = "http"
        check {
          type     = "http"
          path     = "/metrics"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}
