output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "data_factory_name" {
  value = azurerm_data_factory.adf.name
}

output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.workspace.workspace_url
}

output "sql_server_name" {
  value = azurerm_sql_server.sql.name
}

output "sql_database_name" {
  value = azurerm_sql_database.sqldb.name
}

output "vm_name" {
  value = azurerm_windows_virtual_machine.vm.name
}
