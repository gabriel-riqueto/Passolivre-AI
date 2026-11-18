output "resource_group" {
  description = "Resource Group do PassoLivre AI"
  value       = azurerm_resource_group.rg.name
}

output "container_apps_environment" {
  description = "Nome do ambiente Container Apps"
  value       = azurerm_container_app_environment.env.name
}

output "container_apps_environment_id" {
  description = "ID do ambiente Container Apps"
  value       = azurerm_container_app_environment.env.id
}

output "log_analytics_workspace" {
  description = "Nome do Log Analytics"
  value       = azurerm_log_analytics_workspace.logs.name
}