# akv-migrate

this back up and restore utility will migrate or backup only your Azure key vault. It will only migrate within a subscription because the files are encrypted to to the subscripton.


 If you want to retain the backup files uncomment NODELETETEMPFILE
 
 if you want to backup only uncomment BACKUPONLY


 If the secret is in the destination with the same name - it will be backed up in the BACKUPDIR and deleted from the destination key vault
