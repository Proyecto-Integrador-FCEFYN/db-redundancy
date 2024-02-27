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
