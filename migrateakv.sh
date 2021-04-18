#!/bin/bash

# this back up and restore utility will migrate or backup only your Azure key vault 
# it sill only migrate within a subscription because the files are encrypted to to the subscripton 
# if you want to retain the backup files uncomment NODELETETEMPFILE
# if you wan to backup only uncomment BACKUPONLY
# if the is a secret in the destination of the same name - it will be backed up in the BACKUPDIR and deleted from the key vault

# the keyvault to be migrated - source
export VAULTNAME=
# the keyvault we will migrate to - destination
export NEWVAULTNAME=
# folder for temp or permanent storage of backed up secrets
export BACKUPDIR=
# subscription if needed when there are multiple subsciptions
export SUBSCRIPTION=""
# uncomment to save temp backup files
# export NODELETETEMPFILE="1"
# uncomment to backup only 
# export BACKUPONLY="1"

LOGGEDIN=`az ad signed-in-user show | jq .userPrincipalName | grep \@`

if [ -z ${LOGGEDIN} ]
then
    az login
fi

if [ -z "$SUBSCRIPTION" ]
then
	SUBSCRIPTION=`az account show --query id --output tsv`
else
	az account set --subscription ${SUBSCRIPTION}
fi

echo "Using Subscription ID : "${SUBSCRIPTION}


for i in `az keyvault secret list --vault-name "${VAULTNAME}" -o tsv --query "[].name"`
do
	echo " - Getting ${i} from origin, and setting in destination..."
	echo "checking if  exists"
	az keyvault secret backup --file "${BACKUPDIR}/${i}.secretbackup" --vault-name "${VAULTNAME}" -n "${i}"
	if [ -z $BACKUPONLY ]
	then
	  SECRETEXISTS=`az keyvault secret list --vault-name "${NEWVAULTNAME}" -o tsv --query "[].name" | grep ${i}`
	  if [ -z $SECRETEXISTS ]
	  	  then 
				az keyvault secret restore --file "${BACKUPDIR}/${i}.secretbackup" --vault-name "${NEWVAULTNAME}" 
			else
				echo "oops - need to back up and delete a duplicate"
				az keyvault secret backup --file "${BACKUPDIR}/${i}.${NEWVAULTNAME}.secretbackup" --vault-name "${NEWVAULTNAME}" -n "${i}"
				az keyvault secret delete --vault-name "${NEWVAULTNAME}" --name "${i}"
				az keyvault secret restore --file "${BACKUPDIR}/${i}.secretbackup" --vault-name "${NEWVAULTNAME}" 
			fi
	
		if [ -z ${NODELETETEMPFILE} ]
		then 
			# echo "deleting : ${BACKUPDIR}/${i}.secretbackup"
			rm "${BACKUPDIR}/${i}.secretbackup"
		fi
	fi
done


echo "Finished."
