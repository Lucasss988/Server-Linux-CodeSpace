# 🧱 Servidor de Minecraft Interactivo (Forge/Fabric/Vanilla)

Este proyecto te permite ejecutar un servidor de Minecraft **interactivamente** usando un script Python que automatiza la instalación y ejecución para **versiones Vanilla, Forge o Fabric**, según tu configuración.

> ⚡ **Requisitos:**
> - 🖥️ Codespace con Ubuntu y al menos **16 GB de RAM y 4 cores**
> - 🐍 Python 3.9+
> - ☕ Java 8, 17 y 21 disponibles en el contenedor

---

> ⚠️ **Aviso importante sobre Codespaces:**  
> El servidor en GitHub Codespaces es **solo para pruebas**.  
> ⏳ **Codespaces se apaga automáticamente tras 30 minutos sin actividad en la terminal**, por lo que **no es recomendable para servidores de Minecraft en producción o uso prolongado**.  
>  
---

## 🗂️ Versiones de Minecraft y Java soportadas

---
> 📢 **IMPORTANTE:**  
> El script selecciona automáticamente la versión de Java recomendada según la versión de Minecraft que elijas, pero puedes forzar una ruta específica usando el argumento `--java`.

A continuación se muestra una tabla de compatibilidad entre versiones de Minecraft y las versiones de Java que utiliza el script:

| 🎮 Versión de Minecraft | ☕ Java recomendado                        | 📁 Ruta típica del ejecutable Java                      |
|------------------------|--------------------------------------------|--------------------------------------------------------|
| 1.8.x – 1.16.x         | Java 8 (OpenJDK u OpenJ9/Temurin)          | `/usr/lib/jvm/java-8-openjdk-amd64/bin/java`<br>`/usr/lib/jvm/temurin-8u312/bin/java` |
| 1.17.x – 1.20.x        | Java 17                                    | `/usr/lib/jvm/java-17-openjdk-amd64/bin/java`          |
| 1.21.x y superiores    | Java 21                                    | `/usr/lib/jvm/java-21-openjdk-amd64/bin/java`          |

- 🟦 **Temurin Java 8** es especialmente útil para mods y Forge en 1.16.x y anteriores.
- 🟢 **Java 17** es requerido para versiones modernas (1.17 a 1.20).
- 🟣 **Java 21** es recomendado para las versiones más recientes (1.21+).

> ⚠️ **Nota:**  
> Si usas Forge con Minecraft 1.16.4 o versiones similares, **debes usar Java 8**.  
> Para versiones más nuevas, Java 17 o 21 es obligatorio.

### 🔍 ¿Cómo saber qué Java se está usando?

El script imprime en la terminal la ruta del ejecutable Java seleccionado automáticamente.  
Si quieres forzar una versión específica, ejecuta así:

```bash
python3 server/server.py --java /ruta/a/tu/java
```

---

### 📝 Resumen rápido

- **1.8.x – 1.16.x:**  
  - Usa Java 8 (`openjdk-8-jdk` o Temurin 8)
- **1.17.x – 1.20.x:**  
  - Usa Java 17 (`openjdk-17-jdk`)
- **1.21.x y superiores:**  
  - Usa Java 21 (`openjdk-21-jdk`)

---

> 🧩 Si tienes dudas sobre la compatibilidad, revisa los mensajes de la terminal o consulta la documentación oficial de cada modloader.

---

> 💡 **Si quieres un servidor estable y siempre online, considera migrar a un servidor Linux propio o una VPS.**  
> Aquí tienes algunas opciones de VPS con buena relación calidad-precio:
>
> - 🌐 [Hetzner Cloud](https://www.hetzner.com/cloud) (muy buen precio en Europa)
> - 🌐 [Contabo](https://contabo.com/) (gran capacidad y precios bajos)
> - 🌐 [Vultr](https://www.vultr.com/) (opciones globales y flexibles)
> - 🌐 [DigitalOcean](https://www.digitalocean.com/) (fácil de usar y buen soporte)
>
> Busca siempre una VPS con al menos **4 núcleos y 16 GB de RAM** para un rendimiento óptimo.

---

## 🚀 Primeros pasos

1. **Prepara los archivos de versión:**

   - 📄 `server/VERSION.txt`: contiene la versión de Minecraft que quieres usar (por ejemplo, `1.20.4`)
   - 📄 `server/FORGE_VERSION.txt`: contiene la versión de Forge si usarás mods (por ejemplo, `1.16.5`)

   > 🗂️ **Ambos archivos deben estar en la carpeta `server/`.**

2. **Crea tu archivo `.env` en la carpeta `server/`:**

   Este archivo es necesario para que el servidor pueda enviar notificaciones a Discord y exponer el servidor públicamente con ngrok.

   💡 **Ejemplo de contenido para `server/.env`:**

   ```env
   DISCORD_WEBHOOK=https://discord.com/api/webhooks/tu_webhook_aqui
   NGROK_AUTHTOKEN=tu_token_de_ngrok_aqui
   ```

   - 🔗 **DISCORD_WEBHOOK:** Obtén tu URL de webhook en la configuración de tu canal de Discord.
   - 🔑 **NGROK_AUTHTOKEN:** Regístrate en [ngrok.com](https://ngrok.com/), crea un token y pégalo aquí.

---

## 🔑 Autenticación con ngrok

Para que ngrok funcione correctamente y puedas exponer tu servidor a Internet, **debes autenticarte con tu cuenta de ngrok**.  
Esto se realiza automáticamente si defines correctamente el valor de `NGROK_AUTHTOKEN` en tu archivo `.env`.  
Si nunca has usado ngrok antes, sigue estos pasos:

1. 📝 Crea una cuenta gratuita en [ngrok.com](https://ngrok.com/).
2. 🔍 Ve a tu panel de usuario y copia tu **Auth Token**.
3. 🗒️ Pega ese token en el archivo `server/.env` como se muestra arriba.

> 🟢 **El script se encargará de autenticar ngrok usando ese token la primera vez que lo ejecutes.**

---

## 🧑‍💻 Instalación y uso paso a paso en Linux

Sigue estos pasos para preparar y ejecutar tu servidor de Minecraft en cualquier sistema Linux compatible:

---

### 1️⃣ Instala los requisitos del sistema

Asegúrate de tener instalados los siguientes paquetes:

```bash
sudo apt update
sudo apt install -y python3 python3-pip git wget curl unzip
```

---

### 2️⃣ Instala Java (8, 17 y 21)

Puedes instalar varias versiones de Java con:

```bash
sudo apt install -y openjdk-8-jdk openjdk-17-jdk openjdk-21-jdk
```

Verifica que Java esté instalado:

```bash
java -version
```

> ⚠️ **Importante:**  
> Si vas a usar **Forge** con la versión de Minecraft **1.16.4** (o versiones similares de la 1.16), asegúrate de usar **Java 8** para evitar errores de compatibilidad.  
> Puedes especificar el ejecutable de Java 8 al iniciar el servidor así:
>
> ```bash
> python3 server/server.py --java /usr/lib/jvm/java-8-openjdk-amd64/bin/java
> ```
>
> 🛠️ Cambia la ruta si tu sistema tiene Java 8 en otra ubicación.
>
> 🟦 **¿Quieres usar Temurin Java 8 (por ejemplo, `/usr/lib/jvm/temurin-8u312/bin/java`)?**
>
> Instálalo así:
>
> ```bash
> wget https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u312-b07/OpenJDK8U-jdk_x64_linux_hotspot_8u312b07.tar.gz
> sudo mkdir -p /usr/lib/jvm/temurin-8u312
> sudo tar -xzf OpenJDK8U-jdk_x64_linux_hotspot_8u312b07.tar.gz -C /usr/lib/jvm/temurin-8u312 --strip-components=1
> ```
>
> Así tendrás disponible el ejecutable en `/usr/lib/jvm/temurin-8u312/bin/java`.

---

### 3️⃣ Instala ngrok

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

---

### 4️⃣ Clona este repositorio

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

---

### 5️⃣ Instala dependencias de Python

El script `server.py` requiere algunas librerías de Python para funcionar correctamente. Puedes instalarlas fácilmente con el siguiente comando si tienes el archivo `requirements.txt`:

```bash
pip3 install -r requirements.txt
```

Si no tienes un archivo `requirements.txt`, instala manualmente las dependencias necesarias:

```bash
pip3 install python-dotenv requests
```

**Dependencias requeridas:**
- 🟢 `python-dotenv` (para leer variables del archivo `.env`)
- 🟢 `requests` (para enviar notificaciones a Discord y consultar la API de ngrok)

Puedes verificar que están instaladas ejecutando:

```bash
pip3 show python-dotenv requests
```

Si ambas aparecen en la salida, ya tienes todo listo para ejecutar el script.

---

### 6️⃣ Prepara los archivos de configuración

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

> 📝 **Nota:** Debes obtener tu propio webhook de Discord y tu token de ngrok desde [ngrok.com](https://ngrok.com/).

---

### 7️⃣ Ejecuta el servidor

Desde la raíz del proyecto, ejecuta:

```bash
python3 server/server.py
```

- El script te guiará paso a paso para elegir el tipo de servidor (**vanilla**, **Forge** o **Fabric**), la versión y configuraciones adicionales.
- Si todo está correcto, verás mensajes de confirmación y el enlace público generado por ngrok.

---

## 🎉 ¡Listo!

Tu servidor de Minecraft se instalará y ejecutará automáticamente, exponiéndose a Internet mediante ngrok y notificando el estado en tu canal de Discord.

---

### ❓ ¿Dudas o problemas?

- Revisa los mensajes de la terminal para ver si falta alguna dependencia o variable.
- Asegúrate de que tu archivo `.env` esté bien configurado.
- Consulta la documentación oficial de [ngrok](https://ngrok.com/docs) o [Discord Webhooks](https://support.discord.com/hc/es/articles/228383668-Intro-to-Webhooks) si tienes problemas con la integración.

---

> 🟢 **¡Disfruta tu servidor de Minecraft interactivo y automatizado!**
