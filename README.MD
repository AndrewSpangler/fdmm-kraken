
# FDMM Kraken (Name Subject to Change)

*WIP Node-Based Print Farm Management Docker Ecosystem*

![FDMM Kraken Dashboard](https://raw.githubusercontent.com/AndrewSpangler/fdmm-kraken/refs/heads/main/docu/screenshot.png)

FDMM Kraken is an evolving project with these key objectives:
 - [x] Create a secure, standalone Docker-based ecosystem for managing individual print farm nodes.
 - [ ] Build an extensible system to manage multiple nodes from a single "control server."
 - [ ] Establish a node proxy system to enable delegation, so a single node can act as a proxy to the control server for multiple sub-nodes.
 - [ ] Develop x86_64 and RasPi PXE Boot environments for fully automated, ad-hoc node deployment (external DHCP will be required)

Short Term Goals:
 - [ ] Automate secret file creation using entrypoints, replacing environment variables for better security.
 - [ ] Example on using an external LDAP server so multiple nodes use the same auth credentials.
 - [ ] Provide integration examples with Proxy/DDNS services like Cloudflare. 
 - [ ] Provide integration examples with other signing utilities such as LetsEncrypt
 - [ ] Begin development of "control server" and "managed-node" docker-compose files, the managed node will be a stripped-down version of the normal unmanaged node. The control server will serve to de-duplicate auth, dns, etc and provide a consolidated proxy to handle requests from multiple nodes.

Long Term Goals:
 - [ ] Develop "control server" (Working name: FDMM-Atlantis)
 - [ ] Implement node autodiscovery.
 - [ ] Develop automatic DNS system on the control server for aggregated node records.

---

## Table of Contents

- [Setup](#setup)
  - [Operating System](#operating-system)
  - [Installation](#installation)
    - [Connect to the Node](#step-1-connect-to-the-node)
    - [Install Git](#step-2-install-git)
    - [Clone Kraken Project](#step-3-clone-kraken-project)
    - [Configure with VS Code](#step-4-configure-with-vs-code)
    - [Configure Environment Variables](#step-5-configure-environment-variables)
    - [Start the Docker Stack](#step-6-start-the-docker-stack)
    - [DNS Configuration](#step-7-dns-configuration)
    - [Configure OpenLDAP](#step-8-configure-openldap)
- [Using FDMM Kraken](#using-fdmm-kraken)
- [Advanced Configuration](#advanced-configuration)
- [Credits](#credits)
- [Icons](#icons)

---

## Setup

### Operating System

**The Hostname of Your Machine is Important**  
The hostname will be used to configure local DNS and handle proxying. This guide assumes your computer is named `printhost`. If you use a different name during Ubuntu/Raspberry Pi setup, adjust the instructions accordingly.

 - This Docker stack is resource-intensive and untested on Raspberry Pi. While it may work on higher-end Pi models, performance issues may arise. Removing optional containers such as Portainer, Filebrowser, Code-Server, Glances, and unused printer service containers can help. Removing Traefik, Authelia, OpenLDAP, or CoreDNS will break the reverse proxy and authentication setup.

 - The stack has been tested on a Ryzen 7 2700X using [Ubuntu Server 24.04.1 LTS](https://ubuntu.com/download/server). During installation, Docker was selected, a user named “administrator” was created, and SSH was enabled for headless configuration. Set a static IP address if possible.

---

### Installation

This guide assumes Ubuntu Server 24.04.01. Some steps may need modification for Raspberry Pi.

#### Step 1: Connect to the Node
 - Connect to the node via SSH. If using Ubuntu Desktop, skip this step and open a terminal. To connect, obtain the node’s IP address from your router or check directly on the node.
 - Run:  
   ```bash
   ssh administrator@<node-ip-address>
   ```

#### Step 2: Install Git
 - Update and install Git, which will be used to pull the Kraken project:
   ```bash
   sudo apt update
   sudo apt install git -y
   ```

#### Step 3: Clone Kraken Project
 - Create a folder for Kraken, then pull the project and navigate into it:
   ```bash
   git pull https://github.com/AndrewSpangler/fdmm-kraken.git
   cd fdmm-kraken
   ```

#### Step 4: Configure with VS Code
 - Use a temporary code-server container to configure the Kraken environment. Once running, you can delete it using Portainer.
 - In the `fdmm-kraken` directory, run:
   ```bash
   docker run -d \
     --name=temp-code-server \
     -e PUID=1000 \
     -e PGID=1000 \
     -e PASSWORD=password \
     -e DEFAULT_WORKSPACE=/workspace \
     -p 8443:8443 \
     -v ./config/temp-code-server:/config \
     -v ./:/workspace \
     --restart unless-stopped \
     lscr.io/linuxserver/code-server:latest
   ```
 - Access the container at `http://<node-ip-address>:8443`.

#### Step 5: Configure Environment Variables
 - In code-server, locate the Docker environment files on the left sidebar. Essential folders and files include:
    - `appdata`: *Container-generated data*
    - `certs`: *Server certificate storage*
    - `config`: *Container configuration files*
    - `fdmmhydra`: *Local config application, currently disabled*
    - `logs`: *Some container logs*
    - `.gitignore`: *File for Git repo updates*
    - `docker-compose.yml`: *Main Docker config file*
    - `template.env`: *Environment variable template (rename to `.env` for use)*

 - FDMM Kraken will auto-generate self-signed certificates for secure Traefik reverse-proxying. To avoid browser certificate warnings, download and install the Root CA certificate on your device. Reverse-proxying provides simplified access control, security, and routing.

 - Create a copy of `template.env`, rename it `.env`, and update fields marked #CHANGEME. [it-tools](https://it-tools.tech/token-generator) can simplify this process.

#### Step 6: Start the Docker Stack
In the `docker` folder, start the Docker stack:
```bash
sudo docker compose -f ./docker-compose.yml up -d
```
The containers will download and launch.

#### Step 7: DNS Configuration
 - Set your PC or router to use the node IP as a secondary DNS. This directs `*.printhost.local` (or your chosen hostname) requests to the node.

#### Step 8: Configure OpenLDAP
 - After the first launch, set up OpenLDAP using `ldap-user-manager` by visiting `http://<node-ip>:8785/setup`. Follow the guided setup to create the required groups and admin user.
 - After setup, comment out the `ldap-user-manager` ports section in `docker-compose.yml` to disable local access.

---

### Using FDMM Kraken

If setup was successful, access the FDMM Kraken dashboard via HTTPS at `https://<hostname>.local`. Accept any self-signed certificate warnings; these can be resolved by installing the generated root certificate on your device.
Under the services section of the dashboard there is a link to download the RootCA.pem file called "Download Root Cert", click the link and download the file it serves. Follow the appropriate instructions to install the cert on the devices you want to be able to access the node from [Add self-generated root certificate authorities for 8 operating systems and browsers](https://www.bounca.org/tutorials/install_root_certificate.html)

---

### Advanced Configuration
 - Additional documentation coming soon, covering:
   - Homepage customization
   - Klipper, Moonraker, Fluidd, and Mainsail integration
   - LDAP setup

---

## Credits
 - **Davidzwa** for the [FDM-Monster](https://github.com/fdm-monster/fdm-monster) project and dashboard color scheme inspiration.
 - **Klipper Compose and Config** inspiration from [klipper-web-control-docker](https://github.com/dimalo/klipper-web-control-docker).
 - **mkcert Configuration** from [Setting Up Traefik and mkcert for Local Development](https://dev.to/agusrdz/setting-up-traefik-and-mkcert-for-local-development-48j5).

### Icons
 - Most icons from [pictogrammers](https://pictogrammers.com/), customized for the FDMM theme.
 - Icons from Portainer, Fluidd, Klipper, VS Code, and Mainsail sourced from their projects and adapted for FDMM.
 - FDMM Kraken/Octoprint icons by Lyfe.

---