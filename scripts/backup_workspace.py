# Script: Backup workspace
import shutil
import datetime
src = '.'
dst = f'backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copytree(src, dst, dirs_exist_ok=True)
print(f'Workspace backed up to {dst}')
