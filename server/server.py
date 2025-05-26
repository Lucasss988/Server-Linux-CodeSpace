import os
import shutil
import subprocess
import urllib.request
import json
import socket
import sys
from xml.etree import ElementTree
import argparse
import json
import time
import urllib.request
import requests 
from dotenv import load_dotenv  # Agrega esta línea al inicio del archivo

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(SERVER_DIR, "VERSION.txt")
FORGE_VERSION_FILE = os.path.join(SERVER_DIR, "FORGE_VERSION.txt")

def leer_version(path):
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    raise ValueError(f"No se encontró ninguna versión descomentada en {path}")

def descargar_con_user_agent(url, destino):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(destino, 'wb') as out_file:
        out_file.write(response.read())

def version_instalada_ok(carpeta, version):
    version_path = os.path.join(carpeta, "INSTALLED_VERSION.txt")
    if not os.path.exists(version_path):
        return False
    with open(version_path, "r") as f:
        return f.read().strip() == version

def guardar_version_instalada(carpeta, version):
    with open(os.path.join(carpeta, "INSTALLED_VERSION.txt"), "w") as f:
        f.write(version)

def seleccionar_java_por_version(mc_version):
    rutas_preferidas = []

    partes = mc_version.split(".")
    try:
        major = int(partes[0])
        minor = int(partes[1])
    except (IndexError, ValueError):
        print("⚠️ No se pudo interpretar la versión de Minecraft. Usando 'java' por defecto.")
        return "java"

    version_numerica = major + minor / 100

    if version_numerica <= 1.16:
        rutas_preferidas.append("/usr/lib/jvm/temurin-8u312/bin/java")
        rutas_preferidas.append("/usr/lib/jvm/java-8-openjdk-amd64/bin/java")  # <-- Añade esta línea
    elif version_numerica <= 1.20:
        rutas_preferidas.append("/usr/lib/jvm/java-17-openjdk-amd64/bin/java")
    else:
        rutas_preferidas.append("/usr/lib/jvm/java-21-openjdk-amd64/bin/java")

    rutas_preferidas += [
        "/usr/lib/jvm/temurin-8u312/bin/java",
        "/usr/lib/jvm/java-8-openjdk-amd64/bin/java",  # <-- Añade esta línea
        "/usr/lib/jvm/java-17-openjdk-amd64/bin/java",
        "/usr/lib/jvm/java-21-openjdk-amd64/bin/java"
    ]

    for ruta in rutas_preferidas:
        if os.path.exists(ruta):
            print(f"✅ Usando Java: {ruta}")
            return ruta

    print("⚠️ No se encontró ninguna versión conocida de Java. Usando 'java' por defecto.")
    return "java"

def get_latest_forge_version(mc_version):
    url = "https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml = response.read()
        root = ElementTree.fromstring(xml)
        versions = [v.text for v in root.findall(".//version")]
        forge_versions = [v for v in versions if v.startswith(mc_version + "-")]
        if not forge_versions:
            return None
        return forge_versions[-1].split("-", 1)[1]
    except Exception as e:
        print(f"No se pudo obtener la versión de Forge: {e}")
        return None

def descargar_instalador_fabric(version, destino):
    url = f"https://meta.fabricmc.net/v2/versions/installer"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        latest_installer = data[0]["url"]
        urllib.request.urlretrieve(latest_installer, destino)

# Carga las variables de entorno desde el archivo .env en la carpeta server
load_dotenv(os.path.join(SERVER_DIR, ".env"))

def leer_webhook_desde_env():
    # Solo obtiene el webhook desde la variable de entorno del .env
    return os.environ.get("DISCORD_WEBHOOK")

def enviar_webhook_discord(webhook_url, mensaje):
    if not webhook_url:
        print("No se encontró el webhook de Discord.")
        return
    data = {"content": mensaje}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Mensaje enviado a Discord correctamente.")
        else:
            print(f"Error al enviar mensaje a Discord: {response.status_code}")
    except Exception as e:
        print(f"Error enviando webhook: {e}")

WEBHOOK_URL = leer_webhook_desde_env()

def notificar_estado_servidor(estado, version=None, public_url=None):
    version_info = f"\nVersión de Minecraft: `{version}`" if version else ""
    # Quita el prefijo tcp:// si existe
    if public_url and public_url.startswith("tcp://"):
        ip_publica = public_url.replace("tcp://", "")
        ngrok_info = f"\n🌐 Acceso público: `{ip_publica}`"
    elif public_url:
        ngrok_info = f"\n🌐 Acceso público: `{public_url}`"
    else:
        ngrok_info = "\n🌐 No se pudo obtener la URL pública de ngrok."
    if estado == "online":
        mensaje = f"🟢 El servidor está **ONLINE**{version_info}{ngrok_info}"
    else:
        mensaje = f"🔴 El servidor está **OFFLINE**{version_info}{ngrok_info}"
    enviar_webhook_discord(WEBHOOK_URL, mensaje)

def iniciar_ngrok_y_obtener_url(puerto=25565):
    ngrok_authtoken = os.environ.get("NGROK_AUTHTOKEN")
    if not ngrok_authtoken:
        print("No se encontró NGROK_AUTHTOKEN en el .env. Por favor, agrégalo.")
        return None, None

    # Autentica ngrok antes de iniciar el túnel
    subprocess.run(["ngrok", "config", "add-authtoken", ngrok_authtoken], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Inicia ngrok sin forzar el puerto, deja que asigne uno público automáticamente
    ngrok_proc = subprocess.Popen(
        ["ngrok", "tcp", str(puerto)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    time.sleep(3)
    try:
        resp = requests.get("http://localhost:4040/api/tunnels")
        tunnels = resp.json().get("tunnels", [])
        for tunnel in tunnels:
            if tunnel["proto"] == "tcp":
                public_url = tunnel["public_url"]
                return public_url, ngrok_proc
        print("⚠️ No se encontró túnel TCP en la respuesta de ngrok.")
    except Exception as e:
        print(f"Error obteniendo la URL de ngrok: {e}")
    return None, ngrok_proc

# Leer la versión deseada
version = leer_version(VERSION_FILE)

# Leer argumentos
parser = argparse.ArgumentParser()
parser.add_argument("--java", help="Ruta al ejecutable de Java", default="java")
args_parsed, unknown = parser.parse_known_args()
java_bin = args_parsed.java if args_parsed.java != "java" else seleccionar_java_por_version(version)

modo = None
modloader = None
if len(sys.argv) > 1 and sys.argv[1] in ["mods", "vanilla"]:
    modo = sys.argv[1]
    if modo == "mods":
        if len(sys.argv) > 2 and sys.argv[2] in ["forge", "fabric"]:
            modloader = sys.argv[2]
else:
    modo = input("¿Quieres iniciar el servidor con mods (Forge/Fabric) o vanilla? Escribe 'mods' o 'vanilla': ").strip().lower()
    if modo == "mods":
        modloader = input("¿Qué modloader quieres usar? Escribe 'forge' o 'fabric': ").strip().lower()

if modo == "mods" and modloader == "forge":
    version = leer_version(FORGE_VERSION_FILE)
else:
    version = leer_version(VERSION_FILE)

if modo == "mods":
    if modloader == "forge":
        forge_version = get_latest_forge_version(version)
        if not forge_version:
            print(f"No se encontró Forge compatible con Minecraft {version}. Iniciando vanilla.")
            modo = "vanilla"
    elif modloader == "fabric":
        pass
    else:
        print("Modloader no válido. Iniciando vanilla.")
        modo = "vanilla"

# Preguntar versión después de elegir modloader
if modo == "mods":
    if modloader == "forge":
        version_actual = leer_version(FORGE_VERSION_FILE)
    elif modloader == "fabric":
        version_actual = leer_version(VERSION_FILE)
    else:
        version_actual = leer_version(VERSION_FILE)

    print(f"La versión actual configurada es: {version_actual}")
    cambiar = input("¿Quieres cambiar la versión? (s/n): ").strip().lower()
    if cambiar == "s":
        nueva_version = input("Escribe la versión de Minecraft que quieres usar (ejemplo: 1.20.4): ").strip()
        if modloader == "forge":
            with open(FORGE_VERSION_FILE, "w") as f:
                f.write(nueva_version)
        else:
            with open(VERSION_FILE, "w") as f:
                f.write(nueva_version)
        version = nueva_version
        print(f"Versión cambiada a: {version}")
        # <-- Agrega esto:
        if modloader == "forge":
            forge_version = get_latest_forge_version(version)
    else:
        version = version_actual

# Selecciona el Java correcto según la versión final
java_bin = args_parsed.java if args_parsed.java != "java" else seleccionar_java_por_version(version)
print(f"✅ Usando Java: {java_bin}")

# ============================
# SELECCIÓN DE RAM POR USUARIO
# ============================
print("\n" + "="*60)
print("💾  ¿CUÁNTA RAM QUIERES ASIGNAR AL SERVIDOR?  💾".center(60))
print("="*60)
print("🔴 Elige la cantidad de RAM (en GB) que usará el servidor.")
print("⚠️  Mínimo recomendado: 2 GB | Máximo permitido: 16 GB")
print("💡 Si pones un valor inválido, se usará 4 GB por defecto.")
print("="*60)

try:
    ram_gb = int(input("👉 Ingresa la cantidad de RAM (GB): ").strip())
    if ram_gb < 2 or ram_gb > 16:
        print("⚠️  Valor fuera de rango. Se usará 4 GB por defecto.")
        ram_gb = 4
except Exception:
    print("⚠️  Valor inválido. Se usará 4 GB por defecto.")
    ram_gb = 4

ram_str = f"-Xmx{ram_gb}G -Xms{ram_gb}G"
print(f"✅ El servidor se ejecutará con {ram_gb} GB de RAM.\n")
# ============================

ngrok_proc = None
public_url = None

if modo in ["vanilla", "mods"]:
    public_url, ngrok_proc = iniciar_ngrok_y_obtener_url(25565)

if modo == "mods" and modloader == "forge":
    FORGE_DIR = os.path.join(SERVER_DIR, "forge")
    forge_version_full = f"{version}-{forge_version}"
    if not version_instalada_ok(FORGE_DIR, forge_version_full):
        if os.path.exists(FORGE_DIR):
            shutil.rmtree(FORGE_DIR)
        os.makedirs(FORGE_DIR, exist_ok=True)
    guardar_version_instalada(FORGE_DIR, forge_version_full)

    forge_installer_path = os.path.join(FORGE_DIR, f"forge-installer.jar")
    print(f"Descargando Forge {forge_version} para Minecraft {version}...")
    forge_installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version}-{forge_version}/forge-{version}-{forge_version}-installer.jar"
    if not os.path.exists(forge_installer_path):
        descargar_con_user_agent(forge_installer_url, forge_installer_path)
        print("Forge installer descargado.")

    print("Instalando Forge...")
    subprocess.run(
        [java_bin, "-jar", "forge-installer.jar", "--installServer"],
        cwd=FORGE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL  # Oculta los errores gráficos de la salida
    )

    forge_jar_file = None

    # 1. Buscar archivo universal específico
    for file in os.listdir(FORGE_DIR):
        if file.endswith(".jar") and "universal" in file and file.startswith(f"forge-{version}-{forge_version}"):
            forge_jar_file = os.path.join(FORGE_DIR, file)
            break

    # 2. Buscar cualquier archivo universal
    if not forge_jar_file:
        for file in os.listdir(FORGE_DIR):
            if file.endswith(".jar") and "universal" in file and file.startswith("forge"):
                forge_jar_file = os.path.join(FORGE_DIR, file)
                break

    # 3. Buscar archivo server como último recurso
    if not forge_jar_file:
        for file in os.listdir(FORGE_DIR):
            if file.endswith(".jar") and file.startswith("forge") and "installer" not in file:
                forge_jar_file = os.path.join(FORGE_DIR, file)
                break

    # 4. Si solo hay installer, decide según la versión de Minecraft
    if not forge_jar_file:
        # Extrae la versión mayor y menor de Minecraft
        partes = version.split(".")
        try:
            major = int(partes[0])
            minor = int(partes[1])
        except (IndexError, ValueError):
            major = 0
            minor = 0

        # Si es 1.17 o superior, usa run.sh
        if (major == 1 and minor >= 17) or (major > 1):
            run_sh = os.path.join(FORGE_DIR, "run.sh")
            if os.path.exists(run_sh):
                print("Iniciando servidor Forge con mods usando run.sh...")
                subprocess.run(["bash", "run.sh"], cwd=FORGE_DIR)
                print("El servidor fue cerrado con éxito.")
                sys.exit(0)
            else:
                raise RuntimeError("No se encontró el script run.sh de Forge después de la instalación. ¿El instalador terminó correctamente?")
        else:
            raise RuntimeError("No se encontró el archivo JAR de Forge después de la instalación. ¿El instalador terminó correctamente?")

    with open(os.path.join(FORGE_DIR, "eula.txt"), "w") as f:
        f.write("eula=true\n")

    # Ahora sí, ejecuta el servidor
    if (major == 1 and minor >= 17) or (major > 1):
        run_sh = os.path.join(FORGE_DIR, "run.sh")
        if os.path.exists(run_sh):
            print("Preparando eula.txt para Forge...")
            # 1. Ejecuta run.sh SOLO hasta que se genere eula.txt
            proc = subprocess.Popen(["bash", "run.sh"], cwd=FORGE_DIR)
            import time
            eula_path = os.path.join(FORGE_DIR, "eula.txt")
            # Espera a que se genere eula.txt (timeout 30s)
            for _ in range(30):
                if os.path.exists(eula_path):
                    break
                time.sleep(1)
            # Mata el proceso si sigue corriendo
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
            # 2. Escribe eula=true
            with open(eula_path, "w") as f:
                f.write("eula=true\n")
            print("eula.txt actualizado a eula=true. Iniciando servidor Forge con mods...")
            # 3. Ahora sí, arranca el servidor normalmente
            subprocess.run(["bash", "run.sh"], cwd=FORGE_DIR)
            print("El servidor fue cerrado con éxito.")
            sys.exit(0)
        else:
            raise RuntimeError("No se encontró el script run.sh de Forge después de la instalación. ¿El instalador terminó correctamente?")

    # Si usas el JAR universal (para versiones antiguas)
    print("Iniciando servidor Forge con mods...")
    notificar_estado_servidor("online", version, public_url)  # Notifica que está online antes de arrancar
    subprocess.run([java_bin, *ram_str.split(), "-jar", os.path.basename(forge_jar_file), "nogui"], cwd=FORGE_DIR)
    print("El servidor fue cerrado con éxito.")
    notificar_estado_servidor("offline", version, public_url)
    if ngrok_proc:
        ngrok_proc.terminate()

elif modo == "mods" and modloader == "fabric":
    FABRIC_DIR = os.path.join(SERVER_DIR, "fabric")
    if not version_instalada_ok(FABRIC_DIR, version):
        if os.path.exists(FABRIC_DIR):
            shutil.rmtree(FABRIC_DIR)
        os.makedirs(FABRIC_DIR, exist_ok=True)
    guardar_version_instalada(FABRIC_DIR, version)

    fabric_installer_path = os.path.join(FABRIC_DIR, "fabric-installer.jar")
    descargar_instalador_fabric(version, fabric_installer_path)

    print(f"Instalando servidor Fabric para Minecraft {version}...")
    subprocess.run([java_bin, "-jar", "fabric-installer.jar", "server", "-mcversion", version, "-dir", ".", "-downloadMinecraft"], cwd=FABRIC_DIR)

    with open(os.path.join(FABRIC_DIR, "eula.txt"), "w") as f:
        f.write("eula=true\n")

    fabric_server_jar = os.path.join(FABRIC_DIR, "server.jar")
    if not os.path.exists(fabric_server_jar):
        raise RuntimeError("No se encontró server.jar en la carpeta de Fabric")

    print("Iniciando servidor Fabric...")
    notificar_estado_servidor("online", version, public_url)  # Notifica que está online antes de arrancar
    subprocess.run([java_bin, *ram_str.split(), "-jar", "server.jar", "nogui"], cwd=FABRIC_DIR)
    print("El servidor fue cerrado con éxito.")
    notificar_estado_servidor("offline", version, public_url)
    if ngrok_proc:
        ngrok_proc.terminate()

elif modo == "vanilla":
    # Pide la versión de Minecraft al usuario antes de continuar
    version_actual = leer_version(VERSION_FILE)
    print(f"La versión actual configurada es: {version_actual}")
    cambiar = input("¿Quieres cambiar la versión? (s/n): ").strip().lower()
    if cambiar == "s":
        nueva_version = input("Escribe la versión de Minecraft que quieres usar (ejemplo: 1.20.4): ").strip()
        with open(VERSION_FILE, "w") as f:
            f.write(nueva_version)
        version = nueva_version
        print(f"Versión cambiada a: {version}")
    else:
        version = version_actual

    VANILLA_DIR = os.path.join(SERVER_DIR, "vanilla")
    if not version_instalada_ok(VANILLA_DIR, version):
        if os.path.exists(VANILLA_DIR):
            shutil.rmtree(VANILLA_DIR)
        os.makedirs(VANILLA_DIR, exist_ok=True)
    guardar_version_instalada(VANILLA_DIR, version)

    JAR_FILE_VANILLA = os.path.join(VANILLA_DIR, "server.jar")
    EULA_FILE_VANILLA = os.path.join(VANILLA_DIR, "eula.txt")

    MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    print(f"Descargando servidor de Minecraft versión {version}...")

    with urllib.request.urlopen(MANIFEST_URL) as response:
        manifest = json.loads(response.read().decode())

    version_data = next((v for v in manifest["versions"] if v["id"] == version), None)
    if not version_data:
        raise ValueError(f"Versión {version} no encontrada en manifest.json")

    with urllib.request.urlopen(version_data["url"]) as response:
        version_json = json.loads(response.read().decode())

    jar_url = version_json["downloads"]["server"]["url"]

    if not os.path.exists(JAR_FILE_VANILLA):
        urllib.request.urlretrieve(jar_url, JAR_FILE_VANILLA)
        print(f"Descargado server.jar de {version} en carpeta vanilla")

    with open(EULA_FILE_VANILLA, "w") as f:
        f.write("eula=true\n")

    print("Iniciando servidor vanilla...")
    notificar_estado_servidor("online", version, public_url)  # Notifica que está online antes de arrancar
    subprocess.run([java_bin, *ram_str.split(), "-jar", "server.jar", "nogui"], cwd=VANILLA_DIR)
    print("El servidor fue cerrado con éxito.")
    notificar_estado_servidor("offline", version, public_url)
    if ngrok_proc:
        ngrok_proc.terminate()

