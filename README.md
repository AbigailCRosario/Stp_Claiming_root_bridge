# ⚔️ Layer 2 Infrastructure Attack Framework

<p align="center">
  <img src="https://img.shields.io/badge/Security-L2%20Pentesting-red?style=for-the-badge&logo=kali-linux" />
  <img src="https://img.shields.io/badge/Language-Python%203-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Library-Scapy-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Target-Cisco%20IOS-orange?style=for-the-badge&logo=cisco" />
  <img src="https://img.shields.io/badge/Status-Educational-yellow?style=for-the-badge" />
</p>

> **⚠️ DISCLAIMER:** Este repositorio contiene pruebas de concepto (PoC) desarrolladas con fines académicos y de investigación en entornos controlados (GNS3). El uso de estas herramientas en redes sin autorización explícita es ilegal.

---

## 📖 Descripción del Proyecto

Este proyecto documenta la explotación y mitigación de vulnerabilidades críticas en la Capa de Enlace de Datos (Capa 2 del Modelo OSI). El objetivo es demostrar cómo una configuración insegura en los switches de acceso puede derivar en **Denegación de Servicio (DoS)**, **Man-in-the-Middle (MitM)** y **Compromiso Total de la Topología**.

El repositorio incluye scripts en Python/Scapy para automatizar tres vectores de ataque principales:
1.  **STP Root Bridge Takeover:** Secuestro de la jerarquía lógica de la red.
2.  **DHCP Starvation:** Agotamiento de recursos IP (DoS).
3.  **Rogue DHCP Server:** Suplantación de identidad para interceptación de tráfico.

---

## 🗺️ Topología y Escenario

Las pruebas se realizaron sobre una infraestructura simulada en **GNS3** con arquitectura de Núcleo (Core) y Acceso.

### 📋 Tabla de Direccionamiento

| Dispositivo | Rol | Interfaz | VLAN | IP / Subnet | Notas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1-GTW** | Gateway / DHCP | `F0/0.11` | **11** | `10.24.11.1 /24` | Target Gateway |
| | | `F0/0.79` | 79 | `10.24.79.1 /24` | Sub-Interfaz |
| **SW1** | Core Switch | `Eth0/1-2` | 11 | N/A (Trunk) | STP Priority: 32768 |
| **SW2** | Access Switch | `Eth1/0` | 11 | N/A (Access) | **Punto de Inyección** |
| | | `Eth0/2` | 11 | N/A (Trunk) | Uplink al Core |
| **Kali Linux**| **Atacante** | `Eth0` | 11 | `10.24.11.10` | Herramientas Scapy |
| **Victim1** | Cliente | `Eth0` | 11 | DHCP | IP asignada: .2 |

* **Segmento Objetivo:** `10.24.11.0/24`
* **Protocolo STP:** RSTP (Rapid-PVST+)

---

## 📺 Video Demostrativo

Mira la ejecución completa de los ataques y la implementación de las defensas en tiempo real:

[![Ver Video en YouTube](https://img.shields.io/badge/YouTube-Ver%20Demo-red?style=for-the-badge&logo=youtube)](LINK_DE_TU_VIDEO_AQUI)

---

## 💻 Requisitos e Instalación

Para ejecutar estas pruebas de concepto, se requiere un entorno Linux con permisos elevados.

* **Sistema Operativo:** Kali Linux, Parrot OS o Ubuntu.
* **Privilegios:** Root (`sudo`) necesarios para la inyección de paquetes en crudo (*raw sockets*).
* **Dependencias:**

```bash
# 1. Actualizar repositorios
sudo apt update

# 2. Instalar pip y Scapy
sudo apt install python3-pip
sudo pip3 install scapy
⚔️ Módulos de Ataque
1. STP Root Bridge Takeover (king_root.py)
Objetivo: Forzar una re-elección en el protocolo Spanning Tree (RSTP) inyectando BPDUs con prioridad 0. Esto convierte al equipo atacante en el Root Bridge, atrayendo el tráfico de la red hacia él.

sudo python3 king_root.py
2. DHCP Starvation - DoS (dhcp_starvation.py)
Objetivo: Inutilizar el servicio DHCP legítimo agotando el pool de direcciones IP. El script genera miles de solicitudes DHCP DISCOVER por segundo con direcciones MAC falsas (Spoofed MACs).

sudo python3 dhcp_starvation.py
3. Rogue DHCP Server - MitM (dhcp_rogue.py)
Objetivo: Suplantar al servidor DHCP legítimo. Responde a las víctimas con un DHCP OFFER falso que asigna al atacante como Gateway y DNS, permitiendo la interceptación de tráfico.

sudo python3 dhcp_rogue.py
🛡️ Ingeniería Defensiva & Mitigación
Para asegurar la infraestructura contra estos vectores, se deben aplicar las siguientes configuraciones de "Hardening" en los Switches de Acceso (SW2).

A. Defensa contra DHCP Attacks
1. Port Security (Limitación de MACs)
SW2(config)# interface Ethernet1/0
SW2(config-if)# switchport port-security
SW2(config-if)# switchport port-security maximum 3
SW2(config-if)# switchport port-security violation restrict
SW2(config-if)# switchport port-security aging time 2
2. DHCP Snooping (Trusted vs Untrusted)
SW2(config)# ip dhcp snooping
SW2(config)# ip dhcp snooping vlan 11

SW2(config)# interface Ethernet1/0
SW2(config-if)# ip dhcp snooping limit rate 5  

SW2(config)# interface Ethernet0/2
SW2(config-if)# ip dhcp snooping trust
B. Defensa contra STP Attacks
1. BPDU Guard
SW2(config)# interface Ethernet1/0
SW2(config-if)# spanning-tree bpduguard enable
2. Root Guard
SW2(config)# interface Ethernet1/0
SW2(config-if)# spanning-tree guard roo
