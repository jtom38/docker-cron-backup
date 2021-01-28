# docker-cron-backup

This image is made to do something simple, mount the source and destination volumes, tar the source directory and move it to the destination directory.  Once that has been done, post a message to Discord.  It will check the age of the backups and if something is older then what is defined in `BACKUP_MAXAGEDAYS` it will be removed from the disk.

## Image

The image can be found on [hub.docker.com](https://hub.docker.com/r/jtom38/cron-backup).

## Script Parameters

* BACKUP_JOB        = This defines that job name.  Use lowercase and no spaces.
  * Example: 'jenkins-jobs'
* BACKUP_DEST       = This defines where backups will be stored.
  * Example: '/backup'
* BACKUP_SOURCE     = Points ot the directory to backup.
  * Example: '/var/jenkins_home/jobs'
* BACKUP_WEBHOOK    = This is the full URL for the Discord Webhook.
  * Example: "https://discord.com/api/webhooks/..."
* BACKUP_USERNAME   = Defines the user that will post the backup status to Discord.
  * Example: "Kubernetes
* BACKUP_MAXAGEDAYS   = Defines how old a backup file can be before it is deleted.
  * Example: 30
* BACKUP_DEBUG = Enable the output of vars to STDOUT to help with debugging.
  * Example: true

## Changelog

* 0.0.4
  * Fixed the script to post to Discord.
