import shutil, time, os
p = 'db.sqlite3'
if os.path.exists(p):
    dst = f'db.sqlite3.bak_{int(time.time())}'
    shutil.copy(p, dst)
    print('BACKUP_CREATED', dst)
else:
    print('NO_DB')
