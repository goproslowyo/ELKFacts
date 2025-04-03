# Docker Setup for Elk Facts Bot

This guide will help you run the Elk Facts Bot in a Docker container. Instructions are provided for Windows, macOS, and Linux users.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/Mac
- Docker Engine for Linux
- Your Twitch credentials (see README.md for setting up OAuth Confidential Client)

## Project Structure

After following this guide, your project will have the following Docker-related files:
```
elkfacts/
├── .dockerignore        # Specifies which files Docker should ignore
├── Dockerfile          # Instructions for building the Docker image
├── docker-compose.yml  # Defines the services and configuration
├── elkfact_bot.py     # The main bot code
├── elk.elkfacts.txt   # The facts file
└── .env               # Your Twitch credentials (never commit this!)
```

## Quick Start

1. Ensure Docker is installed and running on your system
2. Set up your Twitch OAuth Confidential Client (see "Setting Up OAuth" in README.md)
3. Copy your Twitch credentials into `.env` file
4. Open a terminal/command prompt in the project directory
5. Run the bot:
   ```bash
   docker-compose up
   ```

## OAuth Security in Docker

1. Environment Variables:
   - Store credentials in `.env` file
   - Never build images with credentials
   - Use Docker secrets in production

2. Token Cache:
   - Mount token cache as a volume
   - Set proper file permissions
   - Never include in image builds

3. Container Security:
   - Run container as non-root user
   - Mount volumes with correct permissions
   - Keep base images updated

## Detailed Instructions by Platform

### Windows

1. Install Docker Desktop for Windows:
   - Download from [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Follow the installer's instructions
   - Ensure "WSL 2" is enabled if prompted

2. Start Docker:
   - Launch Docker Desktop
   - Wait for the whale icon to stop animating in the system tray

3. Open Command Prompt or PowerShell:
   - Press `Win + R`
   - Type `cmd` or `powershell`
   - Navigate to your project folder:
     ```bash
     cd path\to\elkfacts
     ```

4. Run the bot:
   ```bash
   docker-compose up
   ```

### macOS

1. Install Docker Desktop for Mac:
   - Download from [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Drag Docker to Applications folder
   - Launch Docker and allow system extensions if prompted

2. Open Terminal:
   - Press `Cmd + Space`
   - Type `Terminal`
   - Navigate to your project folder:
     ```bash
     cd path/to/elkfacts
     ```

3. Run the bot:
   ```bash
   docker-compose up
   ```

### Linux

1. Install Docker Engine:
   ```bash
   # Install Docker Engine
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io

   # Install Docker Compose
   sudo apt-get install docker-compose
   ```

2. Start Docker:
   ```bash
   sudo systemctl start docker
   ```

3. Navigate to project folder and run:
   ```bash
   docker-compose up
   ```

## Managing the Bot

First, `cd` into the project directory where your `docker-compose.yml` file is located.

### Starting the Bot
```bash
# Run in the foreground (see logs directly)
docker-compose up

# Run in the background
docker-compose up -d
```

### Stopping the Bot
```bash
# If running in foreground, press Ctrl+C
# If running in background:
docker-compose down
```

### Viewing Logs
```bash
# If running in background
docker-compose logs -f
```

### Updating Elk Facts

The elk.elkfacts.txt file is mounted as a volume, so you can edit it directly on your host machine and changes will be reflected in the container.

## Troubleshooting

1. **Docker not starting**
   - Ensure Docker Desktop is running (Windows/Mac)
   - On Linux, check Docker service: `sudo systemctl status docker`

2. **Permission errors**
   - Windows: Ensure Docker Desktop has necessary permissions
   - Linux: Add your user to docker group:
     ```bash
     sudo usermod -aG docker $USER
     # Log out and back in for changes to take effect
     ```

3. **Container not starting**
   - Check if required ports are available
   - Verify .env file exists with correct credentials
   - Check logs: `docker-compose logs`

4. **Changes to elk.elkfacts.txt not showing**
   - Restart the container: `docker-compose restart`
   - Verify file permissions

5. **OAuth Issues**
   - Verify token cache file permissions
   - Check OAuth configuration in .env
   - Ensure confidential client is set up correctly

## Security Notes

- Never commit your .env file or OAuth token cache
- Keep your Docker installation updated
- Use secure passwords for your Twitch bot account
- Regularly update the base image to get security patches
- Use proper file permissions for token cache
- Follow OAuth security best practices from README.md
- Consider using Docker secrets for production deployments

## Updates and Maintenance

To update the bot:

1. Pull latest code changes
2. Rebuild container:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

For more information about the bot itself and OAuth setup, see README.md
