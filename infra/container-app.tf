resource "azurerm_container_app" "passolivre" {

  name                         = "ca-passolivre-ai"
  container_app_environment_id = azapi_resource.env_standard.id
  resource_group_name          = azurerm_resource_group.rg.name

  revision_mode         = "Single"
  workload_profile_name = "Consumption"

  # ACESSO INTERNO INICIAL
  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {

    min_replicas = 1
    max_replicas = 1

    container {

      name   = "api"
      image  = "ghcr.io/gabriel-riqueto/passolivre-ai:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "OLLAMA_URL"
        value = "http://127.0.0.1:11434"
      }

      env {
        name  = "PASSOLIVRE_MODEL"
        value = "qwen2.5:3b-instruct-q4_K_M"
      }
      env {
        name  = "PASSOLIVRE_REQUIRE_API_KEY"
        value = "true"
      }

      env {
        name        = "PASSOLIVRE_API_KEY"
        secret_name = "passolivre-api-key"
      }
    }


    container {

      name   = "ollama"
      image  = "ghcr.io/gabriel-riqueto/passolivre-ollama-cpu:latest"
      cpu    = 2.0
      memory = "4Gi"

      env {
        name  = "OLLAMA_NUM_PARALLEL"
        value = "1"
      }

      env {
        name  = "OLLAMA_KEEP_ALIVE"
        value = "1m"
      }
    }
  }
  secret {
    name  = "passolivre-api-key"
    value = random_password.api_key.result
  }

  lifecycle {
    ignore_changes = [
      template[0].container[0].image
    ]
  }
}