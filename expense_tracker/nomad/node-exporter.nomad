job "node-exporter" {
  datacenters = ["dc1"]
  type = "system"   # runs on the node like a daemon

  group "exporter" {
    network {
      mode = "host"
      port "metrics" {
        static = 9100
        to     = 9100
      }
    }

    task "node-exporter" {
      driver = "docker"
      config {
        image = "prom/node-exporter:v1.8.1"
        ports = ["metrics"]
        args  = ["--path.rootfs=/host"]
        volumes = ["/:/host:ro"]
      }
      resources {
        cpu    = 100
        memory = 64
      }
    }
  }
}

