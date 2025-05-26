# 🧱 Servidor de Minecraft Interactivo (Forge/Fabric/Vanilla)

Este proyecto te permite ejecutar un servidor de Minecraft **interactivamente** usando un script Python que automatiza la instalación y ejecución para **versiones Vanilla, Forge o Fabric**, según tu configuración.

> **Requisitos:**
> - Codespace con Ubuntu y al menos **16 GB de RAM y 4 cores**
> - Python 3.9+
> - Java 8, 17 y 21 disponibles en el contenedor

---

## 🚀 Primeros pasos

1. **Prepara los archivos de versión:**

   - `server/VERSION.txt`: contiene la versión de Minecraft que quieres usar (por ejemplo, `1.20.4`)
   - `server/FORGE_VERSION.txt`: contiene la versión de Forge si usarás mods (por ejemplo, `1.16.5`)

   Ambos archivos deben estar en la carpeta `server/`.

2. **Crea tu archivo `.env` en la carpeta `server/`:**

   Este archivo es necesario para que el servidor pueda enviar notificaciones a Discord y exponer el servidor públicamente con ngrok.

   Ejemplo de contenido para `server/.env`:

   ```
   DISCORD_WEBHOOK=https://discord.com/api/webhooks/tu_webhook_aqui
   NGROK_AUTHTOKEN=tu_token_de_ngrok_aqui
   ```

   - **DISCORD_WEBHOOK:** Obtén tu URL de webhook en la configuración de tu canal de Discord.
   - **NGROK_AUTHTOKEN:** Regístrate en [ngrok.com](https://ngrok.com/), crea un token y pégalo aquí.

---

## 🔑 Autenticación con ngrok

Para que ngrok funcione correctamente y puedas exponer tu servidor a Internet, **debes autenticarte con tu cuenta de ngrok**.  
Esto se realiza automáticamente si defines correctamente el valor de `NGROK_AUTHTOKEN` en tu archivo `.env`.  
Si nunca has usado ngrok antes, sigue estos pasos:

1. Crea una cuenta gratuita en [ngrok.com](https://ngrok.com/).
2. Ve a tu panel de usuario y copia tu "Auth Token".
3. Pega ese token en el archivo `server/.env` como se muestra arriba.

El script se encargará de autenticar ngrok usando ese token la primera vez que lo ejecutes.

---

## 🧑‍💻 Instalación y uso paso a paso en Linux

Sigue estos pasos para preparar y ejecutar tu servidor de Minecraft en cualquier sistema Linux compatible:

### 1. Instala los requisitos del sistema

Asegúrate de tener instalados los siguientes paquetes:

```bash
sudo apt update
sudo apt install -y python3 python3-pip git wget curl unzip
```

### 2. Instala Java (8, 17 y 21)

Puedes instalar varias versiones de Java con:

```bash
sudo apt install -y openjdk-8-jdk openjdk-17-jdk openjdk-21-jdk
```

Verifica que Java esté instalado:

```bash
java -version
```

> **Importante:**  
> Si vas a usar **Forge** con la versión de Minecraft **1.16.4** (o versiones similares de la 1.16), asegúrate de usar **Java 8** para evitar errores de compatibilidad.  
> Puedes especificar el ejecutable de Java 8 al iniciar el servidor así:
>
> ```bash
> python3 server/server.py --java /usr/lib/jvm/java-8-openjdk-amd64/bin/java
> ```
>
> Cambia la ruta si tu sistema tiene Java 8 en otra ubicación.

### 3. Instala ngrok

Descarga y descomprime ngrok:

```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

Verifica la instalación:

```bash
ngrok version
```

### 4. Clona este repositorio

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### 5. Instala dependencias de Python

```bash
pip3 install -r requirements.txt
```

Si no existe `requirements.txt`, instala manualmente:

```bash
pip3 install python-dotenv requests
```

### 6. Prepara los archivos de configuración

Crea la carpeta `server` si no existe:

```bash
mkdir -p server
```

Crea los archivos de versión:

```bash
echo "1.20.4" > server/VERSION.txt
echo "1.16.5" > server/FORGE_VERSION.txt
```

Crea el archivo `.env` en la carpeta `server/` con tu webhook de Discord y tu token de ngrok:

```bash
cat > server/.env <<EOF
DISCORD_WEBHOOK=https://discord.com/api/webhooks/tu_webhook_aqui
NGROK_AUTHTOKEN=tu_token_de_ngrok_aqui
EOF
```

> **Nota:** Debes obtener tu propio webhook de Discord y tu token de ngrok desde [ngrok.com](https://ngrok.com/).

### 7. Ejecuta el servidor

Desde la raíz del proyecto, ejecuta:

```bash
python3 server/server.py
```

El script te guiará paso a paso para elegir el tipo de servidor (vanilla, Forge o Fabric), la versión y configuraciones adicionales.

---

**¡Listo!**  
Tu servidor de Minecraft se instalará y ejecutará automáticamente, exponiéndose a Internet mediante ngrok y notificando el estado en tu canal de Discord.

¿Dudas o problemas?  
Revisa los mensajes de la terminal y asegúrate de que tu archivo `.env` esté bien configurado.
