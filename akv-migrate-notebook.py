# Databricks notebook source
dbutils.library.installPyPI("azure.mgmt.resource")
dbutils.library.installPyPI("azure-core")
dbutils.library.installPyPI("azure.identity")
dbutils.library.installPyPI("azure-keyvault-secrets")

# COMMAND ----------

import os
from azure.identity import DefaultAzureCredential, DeviceCodeCredential
from azure.keyvault.secrets import SecretClient
from azure.mgmt.resource import SubscriptionClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

# COMMAND ----------

# MAGIC %md
# MAGIC https://azuresdkdocs.blob.core.windows.net/$web/python/azure-keyvault-secrets/latest/azure.keyvault.secrets.html#azure.keyvault.secrets.SecretProperties

# COMMAND ----------

# Acquire the resource URL. In this code we assume the resource URL is in an
# environment variable, KEY_VAULT_URL in this case.

source_vault = "<source KV URL>"


destination_vault = "<destination KV URL>"


# Acquire a credential object for the app identity. When running in the cloud,
# DefaultAzureCredential uses the app's managed identity (MSI) or user-assigned service principal.
# When run locally, DefaultAzureCredential relies on environment variables named
# AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID.
##
# credential = DefaultAzureCredential()

# https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate
# for my interactive demo I use a device login
credential = DeviceCodeCredential()

# Acquire an appropriate client object for the resource identified by the URL. The
# client object only stores the given credential at this point but does not attempt
# to authenticate it.

source_client = SecretClient(vault_url=source_vault, credential=credential)

dest_client = SecretClient(vault_url=destination_vault, credential=credential)

# COMMAND ----------

# https://docs.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme?view=azure-python

# COMMAND ----------

def check_dest(secretname) :
  exists = True
  try:
    dest_client.get_secret(secretname)
  except ResourceNotFoundError as e:
    # print("\n"+secretname+". {0}".format(e.message))
    exists = False
  return exists

# COMMAND ----------

def backup_secret(secretname) :
  try:
    secret_backup = source_client.backup_secret(secretname)
    print("Backup created for secret with name '{0}'.".format(secretname))
    return(secret_backup)
  except HttpResponseError as e:
    print("\nAKN has caught an error. {0}".format(e.message))
    return(None)

# COMMAND ----------

def delete_dest_secret(secretname) :
  
    # The storage account secret is no longer in use, so you delete it.
  try :
    print("\n.. Deleting secret...")
    delete_operation = dest_client.begin_delete_secret(secretname)
    deleted_secret = delete_operation.result()
    print("Deleted secret with name '{0}'".format(deleted_secretname))

    # Wait for the deletion to complete before purging the secret.
    # The purge will take some time, so wait before restoring the backup to avoid a conflict.
    delete_operation.wait()
    print("\n.. Purge the secret")
    dest_client.purge_deleted_secret(deleted_secret.name)
    time.sleep(60)
    print("Purged secret with name '{0}'".format(deleted_secret.name))
    return True
  except HttpResponseError as e:
    print("\nDestination AKV has caught an error. {0}".format(e.message))
    return False

# COMMAND ----------

def restore_secret(secret_backup) : 
  try :
    # In the future, if the secret is required again, we can use the backup value to restore it in the Key Vault.
    print("\n.. Restore the secret using the backed up secret bytes")
    secret = dest_client.restore_secret_backup(secret_backup)
    print("Restored secret with name '{0}'".format(secret.name))
    return True

  except HttpResponseError as e:
    # print("\nDestination AKV has caught an error. {0}".format(e.message))
    print("\nDestination AKV has caught an error. Secret Exixts")
    return False

# COMMAND ----------

delete_dups = False
update_version = True

secret_properties = source_client.list_properties_of_secrets()

for secret_property in secret_properties:
    # the list doesn't include values or versions of the secrets
    print(secret_property.name)
    print("---------------------------")
    backup = backup_secret(secret_property.name)
    if restore_secret(backup) :
      print(secret_property.name + " has been migrated")
    else:
      if delete_dups :
        delete_dest_secret(secret_property.name)
        restore_secret(backup)
      else :
        if update_version : 
          try:
            if source_client.get_secret(secname).value == dest_client.get_secret(secname).value :
              print ("Source and Destination ecrets are identical - no update needed")
            else :
              upd_secret = dest_client.set_secret(secret_property.name, source_client.get_secret(secret_property.name), content_type=secret_property.content_type, expires_on=secret_property.expires_on)
              secret_version = upd_secret.properties.version
              print(secret_property.name + " has been updated to version " + secret_version)
          except (HttpResponseError, ResourceNotFoundError) as e:
            print("\n"+secretname+". {0}".format(e.message))
        else : 
          print(secret_property.name + " has been skipped")
        
        
