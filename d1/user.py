#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys, getopt
import crypt
import random
import grp
import pwd
import errno
import getpass
import pexpect
import pwd
from pwd import getpwnam
import hashlib

userid=''
passwd=''
str_cmd=''

tpl="""

[{u}]
path=/mnt/hdd/capshr/{u}
hide files = /lost+found/ 
guest ok=no
browseable=no
create mask=0700
directory mask=0700
read only=no
follow symlinks=no
wide links=no
write list={u}
force create mode=777
force directory mode=777
valid users={u}
"""

argv = sys.argv[1:]

try:
	opts, args = getopt.getopt(argv,"u:p:",["user=","pass="])
except getopt.GetoptError:
	sys.exit(1)
   
for opt, arg in opts:
	if opt in ("-u", "--user"):
		userid = arg
		userid.strip()
		userid.replace(" ", "")
		userid.rstrip('\n')
	elif opt in ("-p", "--pass"):
		passwd = arg
		passwd.strip()
		passwd.replace(" ", "")
		passwd.rstrip('\n')

if(passwd == '' or userid == ''):
	sys.exit(1)

cmd='/bin/su - root -c "/bin/mkdir /mnt/hdd/capshr/{u} && /bin/chmod 0777 -R /mnt/hdd/capshr/{u} && /usr/sbin/useradd --no-user-group -M -p {p} -s /bin/false -g sambashare -d /mnt/hdd/capshr/{u} {u} && /usr/bin/fallocate -l 50M /mnt/hdd/disks/{u}.img && /sbin/mkfs.ext4 /mnt/hdd/disks/{u}.img && /bin/mount -o loop /mnt/hdd/disks/{u}.img /mnt/hdd/capshr/{u} && chmod 0777 -R /mnt/hdd/capshr/{u} && /bin/rmdir /mnt/hdd/capshr/{u}/lost+found && /usr/bin/smbpasswd -a {u} && cat <<-EOT >> /etc/samba/smb.conf {s}EOT"'

def getsalt(chars = os.times() + os.uname()):
	return str(random.choice(chars)) + str(random.choice(chars))

getuser = os.popen('cut -d: -f1 /etc/passwd |grep '+userid).read()
getuser.strip()
getuser.replace(" ", "")
getuser.rstrip('\n')

if(getuser != ""):
	sys.exit(1)
else:
	
	salt=getsalt()
	enc = str(crypt.crypt(passwd,salt))
	shr = tpl.format(u=userid)	
	str_cmd = str(cmd.format(p=enc, u=userid, s=shr))			
	
if(str_cmd != ""):
	try:
		child = pexpect.spawn(str_cmd)
		child.expect_exact('Password: ')
		child.sendline('lxmicro2014')
		child.expect('New SMB password:')
		child.sendline (str(passwd))
		child.expect ('Retype new SMB password:')
		child.sendline (str(passwd))
		print child.expect(pexpect.EOF)
	except OSError as exception:
		print(exception)		
		sys.exit(1)

try:
	child = pexpect.spawn('su - root -c "/usr/bin/smbcontrol all reload-config"')
	child.expect_exact('Password: ')
	child.sendline('lxmicro2014')
	print child.expect(pexpect.EOF)
except OSError as exception:
	print(exception)		
	sys.exit(1)

uid = ''
gid = ''

try:
	pw = getpwnam(userid)
	uid = str(pw.pw_uid)
	gid = str(pw.pw_gid)
except:
	sys.exit(1)

if(uid == '' or gid == ''):
	sys.exit(1)

try:	
	m = hashlib.sha1()
	m.update(passwd)
	ep = str(m.hexdigest())
except:
	sys.exit(1)
