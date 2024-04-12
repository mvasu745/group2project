# Default tags
output "default_tags" {
  value = {
    "Owner" = "Project"
    "App"   = "Web"
    "Project" = "CLO835"
  }
}

# Prefix to identify resources
output "prefix" {
  value     = "Project"
}