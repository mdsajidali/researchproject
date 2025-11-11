job "docker-test" {
  datacenters = ["dc1"]
  type = "service"

  group "demo" {
    task "ping" {
      driver = "docker"
      config {
        image = "busybox"
        command = "ping"
        args = ["-c", "3", "localhost"]
      }
    }
  }
}
