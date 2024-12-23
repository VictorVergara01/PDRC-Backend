# Implementación del Cosechador de Revistas Científicas

Este proyecto implementa un cosechador de revistas científicas utilizando el protocolo OAI-PMH, basado en Django. Sigue las instrucciones a continuación para instalar, configurar y ejecutar el proyecto en un entorno Linux.

---

## Requisitos previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Ubuntu o una distribución Linux compatible**
- **Acceso root o permisos sudo**
- **Git**
- **MySQL Server**

---

## Instalación y configuración

### 1. Actualizar el sistema
```bash
sudo apt update && sudo apt upgrade
```

### 2. Instalar herramientas esenciales
```bash
sudo apt install git
sudo apt install net-tools
sudo apt install ufw
sudo apt install pkg-config
sudo apt install build-essential default-libmysqlclient-dev
```

### 3. Clonar el repositorio
```bash
git clone https://github.com/VictorVergara01/Portal-de-Revistas.git
cd Portal-de-Revistas
```

### 4. Instalar Python 3.12
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
python3.12 --version  # Verificar la instalación
```

### 5. Configurar el entorno virtual
```bash
sudo apt install python3.12-venv
python3.12 -m venv env
source env/bin/activate
```

### 6. Instalar dependencias del proyecto
```bash
pip install -r requirements.txt
```

# Instalación y Configuración de MySQL para Conexiones Remotas en Ubuntu

Esta guía detalla los pasos para instalar y configurar MySQL en un servidor Ubuntu, habilitar conexiones remotas y crear un usuario y una base de datos específicos.

---

## 1. Actualizar el Sistema
Antes de comenzar, actualiza tu sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 2. Instalar MySQL
Ejecuta el siguiente comando para instalar MySQL Server:

```bash
sudo apt install mysql-server -y
```

Esto instalará MySQL y lo configurará para iniciarse automáticamente.

---

## 3. Asegurar la Instalación de MySQL
Ejecuta el script de configuración de seguridad:

```bash
sudo mysql_secure_installation
```

Durante el proceso:
- Configura una contraseña para el usuario `root`.
- Elimina usuarios anónimos.
- Deshabilita el acceso remoto del usuario `root` (recomendado).
- Elimina la base de datos de prueba.
- Recarga las tablas de privilegios.

---

## 4. Configurar MySQL para Conexiones Remotas

1. **Edita el archivo de configuración de MySQL:**

   ```bash
   sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
   ```

2. **Modifica la línea `bind-address`:**

   Cambia:
   ```plaintext
   bind-address = 127.0.0.1
   ```
   Por:
   ```plaintext
   bind-address = 0.0.0.0
   ```

3. **Guarda y reinicia el servicio MySQL:**

   ```bash
   sudo systemctl restart mysql
   ```

---

## 5. Crear Usuario y Base de Datos

1. **Accede a MySQL:**

   ```bash
   sudo mysql -u root -p
   ```

2. **Crea una base de datos:**

   ```sql
   CREATE DATABASE revistas_db;
   ```

3. **Crea un usuario remoto:**

   ```sql
   CREATE USER 'revista'@'%' IDENTIFIED BY 'ContrasenaSegura';
   ```

4. **Otorga permisos al usuario:**

   ```sql
   GRANT ALL PRIVILEGES ON revistas_db.* TO 'revista'@'%';
   FLUSH PRIVILEGES;
   ```

5. **Sal de MySQL:**

   ```sql
   EXIT;
   ```

---

## 6. Configurar el Firewall

1. **Permite el puerto 3306 en el firewall:**

   ```bash
   sudo ufw allow 3306
   sudo ufw reload
   ```

2. **Verifica que MySQL está escuchando en el puerto 3306:**

   ```bash
   sudo netstat -tuln | grep 3306
   ```

   Deberías ver algo como:
   ```plaintext
   tcp        0      0 0.0.0.0:3306           0.0.0.0:*             LISTEN
   ```

---

## 7. Probar la Conexión Remota

1. **Desde una máquina remota, instala el cliente MySQL si no está instalado:**

   ```bash
   sudo apt install mysql-client -y
   ```

2. **Conéctate al servidor MySQL:**

   ```bash
   mysql -h <IP_DEL_SERVIDOR> -P 3306 -u revista -p
   ```

   Reemplaza `<IP_DEL_SERVIDOR>` con la IP del servidor donde está instalado MySQL.

---

## Resumen de Comandos

### **Instalación y Configuración**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install mysql-server -y
sudo mysql_secure_installation
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql
```

### **Base de Datos y Usuario**
```sql
CREATE DATABASE revistas_db;
CREATE USER 'revista'@'%' IDENTIFIED BY 'ContrasenaSegura';
GRANT ALL PRIVILEGES ON revistas_db.* TO 'revista'@'%';
FLUSH PRIVILEGES;
```

### **Firewall**
```bash
sudo ufw allow 3306
sudo ufw reload
```

### **Prueba de Conexión**
```bash
mysql -h <IP_DEL_SERVIDOR> -P 3306 -u revista -p
```

---

## Consideraciones de Seguridad

- **Contraseñas seguras:** Usa contraseñas fuertes para los usuarios de MySQL.
- **Restringir accesos:** Si es posible, limita las conexiones remotas a rangos de IP específicos:
  ```sql
  CREATE USER 'revista'@'192.168.1.%' IDENTIFIED BY 'ContrasenaSegura';
  GRANT ALL PRIVILEGES ON revistas_db.* TO 'revista'@'192.168.1.%';
  FLUSH PRIVILEGES;
  ```
- **TLS:** Configura conexiones encriptadas para mayor seguridad.

---

### 9. Realizar las migraciones de la base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 10. Crear un usuario administrador
```bash
python manage.py createsuperuser
```

### 11. Recopilar archivos estáticos
```bash
python manage.py collectstatic
```

### 12. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

---

## Configuración para producción

### 1. Instalar Gunicorn
Gunicorn es un servidor WSGI para aplicaciones Python, ideal para entornos de producción:
```bash
pip install gunicorn
```

### 2. Ejecutar Gunicorn
```bash
gunicorn gestor_revistas.wsgi:application
```

O usando un archivo de configuración:
```bash
gunicorn -c gunicorn.conf.py gestor_revistas.wsgi:application
```

---

## Notas adicionales

- Asegúrate de configurar el firewall (UFW) para permitir el tráfico necesario:
  ```bash
  sudo ufw allow 8000  # Puerto por defecto para Django
  sudo ufw allow 80    # Puerto HTTP
  sudo ufw enable
  ```

- Configura un servidor web como **Nginx** para servir la aplicación en producción.

---

## Contribuir

Si deseas contribuir a este proyecto, realiza un fork del repositorio y crea un pull request con tus cambios.

---

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).
