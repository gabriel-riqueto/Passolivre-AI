# RESOURCE GROUP

resource "azurerm_resource_group" "rg" {
  name     = "rg-passolivre-devops"
  location = var.location

  tags = {
    projeto  = "PassoLivre AI"
    ambiente = "academico"
  }
}


# LOG ANALYTICS

resource "azurerm_log_analytics_workspace" "logs" {
  name                = "logs-passolivre"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku               = "PerGB2018"
  retention_in_days = 30
}


# CONTAINER APPS ENVIRONMENT

resource "azurerm_container_app_environment" "env" {
  name                = "env-passolivre"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
  logs_destination           = "log-analytics"

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}