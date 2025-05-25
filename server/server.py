import os
import shutil
import subprocess
import urllib.request
import json
import socket
import sys
from xml.etree import ElementTree
import argparse

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
    elif version_numerica <= 1.20:
        rutas_preferidas.append("/usr/lib/jvm/java-17-openjdk-amd64/bin/java")
    else:
        rutas_preferidas.append("/usr/lib/jvm/java-21-openjdk-amd64/bin/java")

    rutas_preferidas += [
        "/usr/lib/jvm/temurin-8u312/bin/java",
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
    subprocess.run([java_bin, "-jar", "forge-installer.jar", "--installServer"], cwd=FORGE_DIR)

    forge_jar_file = None
    for file in os.listdir(FORGE_DIR):
        if file.startswith(f"forge-{version}-{forge_version}") and file.endswith(".jar"):
            forge_jar_file = os.path.join(FORGE_DIR, file)
            break

    if not forge_jar_file:
        raise RuntimeError("No se encontró el archivo JAR de Forge después de la instalación.")

    with open(os.path.join(FORGE_DIR, "eula.txt"), "w") as f:
        f.write("eula=true\n")

    print("Iniciando servidor Forge con mods...")
    subprocess.run([java_bin, "-Xmx10G", "-Xms10G", "-jar", os.path.basename(forge_jar_file), "nogui"], cwd=FORGE_DIR)
    print("Servidor Forge iniciado.")

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
    subprocess.run([java_bin, "-Xmx8G", "-Xms8G", "-jar", "server.jar", "nogui"], cwd=FABRIC_DIR)
    print("Servidor Fabric iniciado.")

elif modo == "vanilla":
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
    subprocess.run([java_bin, "-Xmx8G", "-Xms8G", "-jar", "server.jar", "nogui"], cwd=VANILLA_DIR)
    print("Servidor vanilla iniciado.")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

print("\n====================================")
print("Dirección para conectarse al servidor de Minecraft:")
print(f"IP: {get_local_ip()}  Puerto: 25565")
print("====================================\n")
