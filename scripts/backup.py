#!/bin/python3
# BACKUP_JOB        = This defines that job name.  Use lowercase and no spaces
#   Example: 'jenkins-jobs'
# BACKUP_DEST       = This defines where backups will be stored.
#   Example: '/backup'
# BACKUP_SOURCE     = Points ot the directory to backup.
#   Example: '/var/jenkins_home/jobs'
# BACKUP_WEBHOOK    = This is the full URL for the Discord Webhook
#   Example: "https://discord.com/api/webhooks/..."
# BACKUP_USERNAME   = Defines the user that will post the backup status to Discord
#   Example: "Kubernetes"
# BACKUP_GEN_JOB_DIR = If enabled, it will check to see if a directory exists inside of `BACKUP_DEST` that contains the name of `BACKUP_JOB`.  If the directory does not exists, it will generate it for you.
#   Example: true

import os
import tarfile
import json
import time
from datetime import datetime
from os import environ
from requests import post
from typing import List

def checkEnvValues(envName: str) -> str:
  try:
    res = environ[envName]
  except:
    res = ''  
  return res

def removeOldBackups(dest: str, maxAge: int) -> None:
  files = os.listdir(dest)
  compare = list()
  if len(files) >= maxAge:
    # Collect info on the files in the dir
    for f in files:
      f = os.path.join(dest, f)
      s = os.stat(f)
      age= datetime.utcfromtimestamp(s.st_mtime)
      compare.append({'file': f, 'age': age})

    # Find the oldest files
    for c in compare:
      now = datetime.now()
      m = now.month - c['age'].month
      d = now.day - c['age'].day
      d = d + m * 30
      if d > maxAge:
        try:
          os.remove(c['file'])
          print(f"'{c['file']}' is {d} days old and was removed from disk. Max age is set to: {maxAge}")
        except Exception as e:
          print(f"Failed to remove {c['file']} from the disk. Reason: {e}")
        pass
  pass

def tarDirectory(tarPath: str, sourceDir: str) -> List:
  if os.path.exists(tarPath) == True:
    os.remove(tarPath)
  
  print("Starting to tar creation...")
  start = time.perf_counter()
  with tarfile.open(tarPath, 'w') as tf:
    tf.add(sourceDir)
  finish = time.perf_counter()
  print(f"Done! Took {finish - start:0.4f} seconds to finish.")


  print("Checking to confirm the file...")
  if os.path.exists(tarPath) == False:
    #raise BackupFileMissing(f"Expected to find '{tarPath}' but the file was not found.")
    status = 2
    message = "Failed to generate the backup."
    print("Failed to generate the backup.")
  else:
    status = 0
    message = f"'{tarPath}' was found on disk."
    print(f"'{tarPath}' was found on disk.")

  l = list()
  l.append(status)
  l.append(message)
  return l

def postMessageDiscord(webhook: str, username: str, job: str, status: str, message: str):
  if "https://discord.com/api/webhooks/" not in webhook:
    print(f"'{webhook}' is not a valid URL.")
    exit()

  webhook = webhook.rstrip()
  header = {'Content-Type': 'application/json'}
  body = { 'username': f"{username}",'content': f"**Job**: {job}\n**Status**: {status}\n**Message**: {message}" }
  bodyJson = json.dumps(body)
  try:
    res = post(url=webhook, headers=header, data=bodyJson)
    if res.status_code == 204:
      print("Message was sent to Discord and no errors reported.")
    else:
      print(f"Sent a message to Discord and expected status code 204 but got {res.status_code}.")
  except Exception as e:
    print(f"Failed to post to Discord. {e}")
  pass

# Collect ENV settings
job: str        = checkEnvValues('BACKUP_JOB')
dest: str       = checkEnvValues('BACKUP_DEST')
source: str     = checkEnvValues('BACKUP_SOURCE')
webhook: str    = checkEnvValues('BACKUP_WEBHOOK')
username: str   = checkEnvValues('BACKUP_USERNAME')
maxAge          = checkEnvValues('BACKUP_MAXAGEDAYS')
if maxAge == '':
  maxAge = -1
else:
  maxAge = int(maxAge)

genBackupDir: bool = bool(checkEnvValues('BACKUP_GEN_JOB_DIR'))
if genBackupDir == True:
  if dest.endswith('/') == True:
    dest = f"{dest}{job}"
  else:
    dest = f"{dest}/{job}"
  
  if os.path.exists(dest) == False:
    os.mkdir(dest)

debug           = bool(checkEnvValues('BACKUP_DEBUG'))
if debug == True:
  # Output to stdout if told to do so.
  print(f'Debug Mode = True')
  print(f'BACKUP_JOB: {job}')
  destExists = os.path.exists(dest)
  print(f"BACKUP_GEN_JOB_DIR: {genBackupDir}")
  print(f"BACKUP_DEST: {dest} | Exists: {destExists}")
  sourceExists = os.path.exists(source)
  print(f"BACKUP_SOURCE: {source} | Exists: {sourceExists}")
  print(f"BACKUP_WEBHOOK: {webhook}")
  print(f"BACKUP_USERNAME: {username}")
  print(f"BACKUP_MAXAGEDAYS: {maxAge}")
  print('')


dt = datetime.now().strftime("%m%d%Y.%H%M%S")
tarFile: str = f"{dest}/{job}-{dt}.tar.gz"

if maxAge >= 1:
  removeOldBackups(dest, maxAge)

tarResults = tarDirectory(tarFile, source)
status = tarResults[0]
message = tarResults[1]
postMessageDiscord(webhook, username, job, status, message)
