# db-backup
Repositorio para realizar el empaquetado del servicio que mantiene la coherencia y la consistencia de las bases de datos principal y de backup.

## Procedimiento

```bash
sudo apt update
sudo apt install dh-systemd
sudo apt install build-essential

git clone git@github.com:Proyecto-Integrador-FCEFYN/db-redundancy
cd db-redundancy/db-backup
dpkg-buildpackage -us -uc -d
```

El .deb se encontrará en la ruta db-redundancy/

### Instalación
```bash
sudo dpkg -i db-backup_1.0_amd64.deb
```
### Desinstalación
```bash
sudo apt-get -y remove db-backup
```
## Output de ejemplo

```bash
dpkg-buildpackage -us -uc -d
dpkg-buildpackage: info: source package db-backup
dpkg-buildpackage: info: source version 1.0
dpkg-buildpackage: info: source distribution unstable
dpkg-buildpackage: info: source changed by  Enzo Candotti <enzo.candotti@mi.unc.edu.ar>
dpkg-buildpackage: info: host architecture amd64
 dpkg-source --before-build .
 fakeroot debian/rules clean
dh clean --with=systemd
   dh_clean
 dpkg-source -b .
dpkg-source: info: using source format '3.0 (native)'
dpkg-source: info: building db-backup in db-backup_1.0.tar.xz
dpkg-source: info: building db-backup in db-backup_1.0.dsc
 debian/rules build
dh build --with=systemd
   dh_update_autotools_config
   dh_autoreconf
   create-stamp debian/debhelper-build-stamp
 fakeroot debian/rules binary
dh binary --with=systemd
   dh_testroot
   dh_prep
   debian/rules override_dh_auto_install
make[1]: Entering directory '/home/ecandott/Documentos/tesis/github-dbbackup/db-redundancy/db-backup'
install -m 755 -p -D db-backup.py /home/ecandott/Documentos/tesis/github-dbbackup/db-redundancy/db-backup/debian/tmp/usr/sbin/db-backup.py
install -m 600 -p -D db-backup-parameters /home/ecandott/Documentos/tesis/github-dbbackup/db-redundancy/db-backup/debian/tmp/etc/default/db-backup-parameters
install -m 644 -p -D logrotate.conf /home/ecandott/Documentos/tesis/github-dbbackup/db-redundancy/db-backup/debian/tmp/home/dbbackupuser/logrotate.conf
make[1]: Leaving directory '/home/ecandott/Documentos/tesis/github-dbbackup/db-redundancy/db-backup'
   dh_install
   dh_installdocs
   dh_installchangelogs
   dh_systemd_enable
   dh_installinit
   dh_systemd_start
   dh_perl
   dh_link
   dh_strip_nondeterminism
   dh_compress
   dh_fixperms
   dh_missing
   dh_strip
   dh_makeshlibs
   dh_shlibdeps
   dh_installdeb
   dh_gencontrol
   dh_md5sums
   dh_builddeb
dpkg-deb: building package 'db-backup' in '../db-backup_1.0_amd64.deb'.
 dpkg-genbuildinfo
 dpkg-genchanges  >../db-backup_1.0_amd64.changes
dpkg-genchanges: info: including full source code in upload
 dpkg-source --after-build .
dpkg-buildpackage: info: full upload; Debian-native package (full source is included)
➜  db-backup git:(master) ✗ cd ..
➜  db-redundancy git:(master) ✗ sudo dpkg -i db-backup_1.0_amd64.deb
(Reading database ... 290325 files and directories currently installed.)
Preparing to unpack db-backup_1.0_amd64.deb ...
Adding system user `dbbackupuser' (UID 131) ...
Adding new group `dbbackupuser' (GID 139) ...
Adding new user `dbbackupuser' (UID 131) with group `dbbackupuser' ...
Creating home directory `/home/dbbackupuser' ...
Collecting pymongo==3.2.2
  Downloading pymongo-3.2.2.tar.gz (504 kB)
     |████████████████████████████████| 504 kB 2.2 MB/s 
Building wheels for collected packages: pymongo
  Building wheel for pymongo (setup.py) ... done
  Created wheel for pymongo: filename=pymongo-3.2.2-cp38-cp38-linux_x86_64.whl size=355440 sha256=9790b27b2bdf8d7364cd721c904f9f82ba71026dceb1a1531cef94d88eb7bc8e
  Stored in directory: /home/dbbackupuser/.cache/pip/wheels/1c/ad/25/dc1a2d03ce163e817b24a0df4b3730de8edc7fcf24d8493feb
Successfully built pymongo
Installing collected packages: pymongo
Successfully installed pymongo-3.2.2
Unpacking db-backup (1.0) over (1.0) ...
Setting up db-backup (1.0) ...
reading config file /home/dbbackupuser/logrotate.conf
Reading state from file: /home/dbbackupuser/logrotate-state
Allocating hash table for state file, size 64 entries

Handling 1 logs

rotating pattern: /home/dbbackupuser/db_backup.log  hourly (3 rotations)
empty log files are rotated, old logs are removed
considering log /home/dbbackupuser/db_backup.log
  log /home/dbbackupuser/db_backup.log does not exist -- skipping
Creating new state
Paquete db-backup instalado con éxito
```