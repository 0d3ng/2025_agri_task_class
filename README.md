# ICT Agri Exercise 2025 - IoT Sensor Monitoring System

## 📋 Project Overview

This project is a complete IoT sensor monitoring system developed for the **ICT Agri Exercise 2025** class assignment. The system reads temperature and humidity data from a DHT22 sensor connected to a Raspberry Pi 4, processes the data through an automation workflow, stores it in a time-series database, and visualizes it in real-time dashboards.

## 🏗️ System Architecture

```
DHT22 Sensor (GPIO4) 
    ↓
Python Script (main.py)
    ↓
MQTT Broker (Mosquitto)
    ↓
n8n Workflow Automation
    ↓
InfluxDB Time-Series Database
    ↓
Grafana Dashboard Visualization
```

## 🔧 Hardware Requirements

- **Raspberry Pi 4** (or compatible model)
- **DHT22 (AM2302) Temperature & Humidity Sensor**
- Connection: GPIO4 pin
- Power supply for Raspberry Pi

## 💻 Software Stack

- **Python 3.13** - Sensor data collection
- **Docker & Docker Compose** - Container orchestration
- **Mosquitto MQTT** - Message broker
- **n8n** - Workflow automation
- **InfluxDB 2.7** - Time-series database
- **Grafana** - Data visualization

## 📦 Installation

### 1. Prerequisites

```bash
# Install Docker and Docker Compose (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Python virtual environment
python3 -m venv ~/.venvs/agri_task
source ~/.venvs/agri_task/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install adafruit-circuitpython-dht
pip install paho-mqtt
pip install influxdb-client
```

### 3. Start Docker Services

```bash
# Navigate to project directory
cd /home/uwais/Applications/2025_agri_task_class

# Start all services
docker compose up -d

# Check status
docker compose ps
```

## 🚀 Usage

### Running the Sensor Script

```bash
# Activate virtual environment
source ~/.venvs/agri_task/bin/activate

# Run sensor monitoring
python main.py
```

The script will:
- Read DHT22 sensor every 2 seconds
- Publish data to MQTT topic `sensors/dht22`
- Display readings in console
- Automatically send to n8n workflow

### Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://192.168.10.6:3000 | admin / admin |
| **InfluxDB** | http://192.168.10.6:8086 | admin / adminpassword |
| **n8n** | http://192.168.10.6:5678 | - |
| **MQTT** | mqtt://192.168.10.6:1883 | No auth |

## 📊 Data Flow

### 1. Sensor Data Collection (Python)

The Python script reads DHT22 sensor and publishes JSON data:

```json
{
  "timestamp": "2025-12-03 12:30:45",
  "sensor": "DHT22",
  "location": "GPIO4",
  "temperature": 22.5,
  "humidity": 38.7,
  "unit_temp": "celsius",
  "unit_humidity": "percent"
}
```

### 2. n8n Workflow

**Workflow Structure:**
```
MQTT Trigger → Code (Python) → HTTP Request (InfluxDB)
```

**Code Node (Python):**
- Parses MQTT message
- Converts timestamp to nanoseconds
- Formats data as InfluxDB Line Protocol

**HTTP Request Node:**
- Sends data to InfluxDB API
- Endpoint: `http://influxdb:8086/api/v2/write`
- Method: POST with Line Protocol format

### 3. InfluxDB Storage

**Data Structure:**
- **Measurement**: `dht22`
- **Tags**: `sensor=DHT22`, `location=GPIO4`
- **Fields**: `temperature`, `humidity`
- **Timestamp**: Unix nanoseconds

### 4. Grafana Visualization

**Dashboards include:**
- Time-series graph for temperature & humidity trends
- Gauge for current temperature reading
- Gauge for current humidity reading
- Real-time updates every 5 seconds

## 🔍 Querying Data

### Using InfluxDB CLI

```bash
# Query last 1 hour of data
docker exec -it influxdb influx query '
from(bucket: "sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "dht22")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
' --org myorg --token mytoken123456789
```

### Using Grafana Query

```flux
from(bucket: "sensors")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "dht22")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
```

## ⚙️ Configuration

### InfluxDB Configuration

- **Organization**: `myorg`
- **Bucket**: `sensors`
- **Token**: `mytoken123456789`
- **Retention**: Unlimited

### MQTT Configuration

- **Broker**: `mosquitto:1883`
- **Topic**: `sensors/dht22`
- **QoS**: 0
- **Authentication**: None

### Timezone Settings

All services configured with timezone: **Asia/Tokyo (JST)**

## 🛠️ Troubleshooting

### Sensor Not Reading

```bash
# Check GPIO permissions
sudo usermod -aG gpio $USER

# Verify sensor connection
python -c "import board; import adafruit_dht; dht = adafruit_dht.DHT22(board.D4)"
```

### Data Not Appearing in InfluxDB

```bash
# Check n8n workflow status
# Ensure workflow is Active (toggle ON)

# Check n8n execution logs
docker compose logs -f n8n

# Verify MQTT messages
docker exec -it mosquitto mosquitto_sub -h localhost -t "sensors/dht22" -v
```

### Grafana Dashboard Not Showing Data

```bash
# Test InfluxDB connection
docker exec -it influxdb influx query '
from(bucket: "sensors")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "dht22")
  |> limit(n: 5)
' --org myorg --token mytoken123456789

# Adjust time range in Grafana dashboard
# Use absolute time range or increase window period
```

## 📁 Project Structure

```
2025_agri_task_class/
├── main.py                          # Main sensor reading script
├── docker-compose.yml               # Docker services configuration
├── README.md                        # This documentation
├── README_DOCKER.md                 # Docker setup guide
├── mosquitto/
│   └── config/
│       └── mosquitto.conf          # MQTT broker config
└── .venv/                          # Python virtual environment
```

## 🔄 Maintenance

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart grafana
docker compose restart influxdb
docker compose restart n8n
```

### Backup Data

```bash
# Backup InfluxDB data
docker exec influxdb tar czf /tmp/influxdb-backup.tar.gz /var/lib/influxdb2
docker cp influxdb:/tmp/influxdb-backup.tar.gz ./backups/

# Backup Grafana dashboards
docker exec grafana tar czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp grafana:/tmp/grafana-backup.tar.gz ./backups/
```

### Clean Up

```bash
# Stop all services
docker compose down

# Remove all data (WARNING: destructive!)
docker compose down -v

# Remove old sensor data
docker exec -it influxdb influx delete \
  --bucket sensors \
  --start 1970-01-01T00:00:00Z \
  --stop 2025-11-01T00:00:00Z \
  --predicate '_measurement="dht22"'
```

## 📈 Performance Metrics

- **Sensor Reading Interval**: 2 seconds
- **Data Retention**: Unlimited
- **Dashboard Refresh Rate**: 5 seconds
- **Average Latency**: < 1 second (sensor to dashboard)

## 🎯 Project Goals

This project demonstrates:
- ✅ IoT sensor integration with Raspberry Pi
- ✅ Real-time data collection and processing
- ✅ Message broker implementation (MQTT)
- ✅ Workflow automation with n8n
- ✅ Time-series database usage
- ✅ Data visualization and monitoring
- ✅ Containerized microservices architecture

## 👨‍💻 Author

**ICT Agri Exercise 2025**
- Student: Uwais
- Institution: Agricultural ICT Class
- Date: December 2025

## 📝 License

This project is created for educational purposes as part of the ICT Agri Exercise 2025 class assignment.

## 🙏 Acknowledgments

- Raspberry Pi Foundation for hardware platform
- Adafruit for DHT22 sensor libraries
- InfluxData for time-series database
- Grafana Labs for visualization platform
- n8n.io for workflow automation

---

**Last Updated**: December 3, 2025
**Version**: 1.0.0
