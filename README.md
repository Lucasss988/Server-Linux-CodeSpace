# 🧱 Servidor de Minecraft Interactivo (Forge/Fabric/Vanilla)

Este proyecto te permite ejecutar un servidor de Minecraft **interactivamente** usando un script Python que automatiza la instalación y ejecución para **versiones Vanilla, Forge o Fabric**, basado en tu configuración.

> **Requisitos:**
> - Codespace con Ubuntu y al menos **16 GB de RAM y 4 cores**
> - Python 3.9+
> - Java 8, 17 y 21 disponibles en el contenedor

---

## 🚀 Primeros pasos

1. **Asegúrate de tener los archivos de versión:**

- `VERSION.txt`: contiene la versión de Minecraft que quieres usar (por ejemplo, `1.16.4`)
- `FORGE_VERSION.txt`: contiene la version de Forge en caso de ocupar mods (por ejemplo, `1.16.4`)

Ambos archivos deben estar en la carpeta `server/`.

---

## 🧪 Ejecutar el servidor paso a paso

Desde la terminal del codespace (estando en la raíz del proyecto), ejecuta:

```bash
python3 server/server.py
