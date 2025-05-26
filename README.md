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

## 🧪 Ejecutar el servidor paso a paso

Desde la terminal del codespace (estando en la raíz del proyecto), ejecuta:

```bash
python3 server/server.py
```

El script te preguntará si quieres iniciar el servidor en modo **vanilla** o con **mods** (Forge/Fabric). Si eliges mods, también te preguntará qué modloader usar.

- Si quieres cambiar la versión de Minecraft o Forge, el script te lo preguntará antes de iniciar.
- El servidor se expondrá automáticamente a Internet usando ngrok y notificará el estado en tu canal de Discord (si configuraste el webhook).

---

## 📝 Notas importantes

- Si no configuras el archivo `.env` correctamente, **no podrás recibir notificaciones en Discord ni exponer el servidor públicamente**.
- Puedes detener el servidor en cualquier momento con `Ctrl+C` en la terminal.
- Los archivos y carpetas de cada tipo de servidor (`vanilla`, `forge`, `fabric`) se crean automáticamente en la carpeta `server/`.

---

## 🛠️ Personalización

- Puedes modificar los archivos `VERSION.txt` y `FORGE_VERSION.txt` manualmente si lo prefieres.
- Si quieres usar otro ejecutable de Java, puedes pasar la ruta con el argumento `--java`:

  ```bash
  python3 server/server.py --java /ruta/a/java
  ```

---

¿Dudas o problemas? ¡Revisa los mensajes de la terminal y asegúrate de que tu `.env` esté bien configurado!
