variable "subscription_id" {
  description = "ID da assinatura Azure"
  type        = string
}

variable "location" {
  description = "Regiao da infraestrutura"
  type        = string
  default     = "brazilsouth"
}