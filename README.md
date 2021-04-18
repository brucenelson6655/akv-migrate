# akv-migrate

### this back up and restore utility will migrate or backup only your Azure key vault 
### it sill only migrate within a subscription because the files are encrypted to to the subscripton 
### if you want to retain the backup files uncomment NODELETETEMPFILE
### if you wan to backup only uncomment BACKUPONLY
### if the is a secret in the destination of the same name - it will be backed up in the BACKUPDIR and deleted from the key vault
