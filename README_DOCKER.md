# Docker Compose Setup for IoT Monitoring Stack

This setup includes:
- **Mosquitto MQTT Broker** - for sensor data messaging
- **InfluxDB** - time-series database for storing sensor data
- **Grafana** - visualization and dashboards
- **Node-RED** - (commented out, since already installed locally)

## Quick Start

1. Start all services:
```bash
docker-compose up -d
```

2. Check status:
```bash
docker-compose ps
```

3. View logs:
```bash
docker-compose logs -f
```

## Access URLs

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`

- **InfluxDB**: http://localhost:8086
  - Username: `admin`
  - Password: `adminpassword`
  - Organization: `myorg`
  - Bucket: `sensors`
  - Token: `mytoken123456789`

- **MQTT Broker**: `localhost:1883`
  - No authentication (allow_anonymous = true)

- **n8n**: http://localhost:5678
  - Username: `admin`
  - Password: `admin`

## Configuration

### InfluxDB Setup
After first run, InfluxDB will be automatically configured with:
- Organization: `myorg`
- Bucket: `sensors`
- Admin Token: `mytoken123456789`

### Mosquitto Config
Edit `mosquitto/config/mosquitto.conf` to customize MQTT broker settings.

### Connect Sensors to MQTT
Your Python sensor scripts can publish to MQTT:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.publish("sensors/temperature", temperature)
client.publish("sensors/humidity", humidity)
```

### Grafana Data Source
1. Login to Grafana (http://localhost:3000)
2. Add InfluxDB data source:
   - URL: `http://influxdb:8086`
   - Organization: `myorg`
   - Token: `mytoken123456789`
   - Default Bucket: `sensors`

## Stop Services

```bash
docker-compose down
```

## Stop and Remove Data

```bash
docker-compose down -v
```

## Useful Commands

```bash
# Restart specific service
docker-compose restart mosquitto

# View logs for specific service
docker-compose logs -f grafana

# Execute command in container
docker-compose exec influxdb influx
```
