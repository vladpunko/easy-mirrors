variable "NAME" {
  default = "docker.io/vladpunko/easy-mirrors"
}

variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["amd64", "arm64"]
}

target "amd64" {
  args = {
    "BASE_IMAGE" = "vladpunko/python3-easy-mirrors:3.10"
  }
  context = "."
  platforms = ["linux/amd64"]
  tags = ["${NAME}:${TAG}"]
}

target "arm64" {
  args = {
    "BASE_IMAGE" = "vladpunko/python3-easy-mirrors:3.10-aarch64"
  }
  context = "."
  platforms = ["linux/arm64"]
  tags = ["${NAME}:${TAG}-aarch64"]
}
