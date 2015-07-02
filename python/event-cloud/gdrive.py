from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import httplib2
import os.path
import sys

SETTINGS_FILE = 'credentials.txt'
PARENT_ID = '0B3phOJqOuoksLVZ2ZW5tOERaT1E' #Work_Activity_Reports

def init_settings(gauth):
    gauth.LoadCredentialsFile(SETTINGS_FILE)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
        print 'Settings file not available, attempting to use browser'
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(SETTINGS_FILE)

def init_drive():
    gauth = GoogleAuth()
    init_settings(gauth)
    return GoogleDrive(gauth)

def upload_file(drive, filename, parent_id=None):
    if os.path.exists(filename):
        metadata = {'title': os.path.basename(filename)}
        if parent_id is not None:
            metadata['parents'] = [drive.CreateFile({'id': parent_id})]
        f = drive.CreateFile(metadata)
        f.SetContentFile(filename)
        f.Upload()
    else:
        print 'File doesn\'t exist...'

if __name__ == '__main__':
  if len(sys.argv) < 2 or len(sys.argv) > 3:
    print 'Usage: %s <filename> [parent_id]'
    print 'possible parent id: %s' % (PARENT_ID)
    raise SystemExit
  upload_file(init_drive(), sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)

