# CDN Simulator

A Python-based Content Delivery Network (CDN) simulator with machine learning optimization, real-time monitoring, and visualization capabilities.

## Features

- **CDN Simulation**
  - Multiple nodes with configurable capacities
  - Intelligent load balancing
  - Request latency simulation
  - Content type-based routing

- **Machine Learning**
  - Traffic prediction using Random Forest
  - Real-time model training and evaluation
  - Accuracy monitoring

- **Caching System**
  - LRU cache implementation
  - Cache hit/miss tracking
  - Configurable cache size

- **Monitoring & Visualization**
  - Real-time metrics collection with Prometheus
  - Beautiful dashboards with Grafana
  - Key metrics:
    - Request rates
    - Node load distribution
    - Cache hit rates
    - ML model accuracy

## Prerequisites

- Python 3.8 or higher
- Homebrew (for macOS users)
- Redis
- Prometheus
- Grafana

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cdn-simulator.git
cd cdn-simulator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install and start Redis:
```bash
brew install redis
brew services start redis
```

4. Install and start Prometheus:
```bash
brew install prometheus
cp prometheus.yml /usr/local/etc/prometheus.yml
brew services start prometheus
```

5. Install and start Grafana:
```bash
brew install grafana
brew services start grafana
```

## Configuration

### Prometheus Setup
The `prometheus.yml` file is configured to scrape metrics from the simulator on port 8000:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cdn-simulator'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Setup

1. Access Grafana at http://localhost:3000 (default credentials: admin/admin)

2. Add Prometheus as a data source:
   - Go to Configuration > Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - Set URL to "http://localhost:9090"
   - Click "Save & Test"

3. Import the dashboard:
   - Go to Dashboards > Import
   - Click "Upload JSON file"
   - Select `grafana-dashboard.json`
   - Click "Import"

## Usage

1. Start the simulator:
```bash
python example.py
```

2. View metrics:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

3. The simulator will:
   - Initialize CDN nodes with random capacities
   - Process simulated content requests
   - Train and update the ML model
   - Collect and display metrics

4. Monitor the dashboard for:
   - Real-time request rates
   - Node load distribution
   - Cache hit rates
   - ML model prediction accuracy

## Project Structure

```
cdn-simulator/
├── cdnsim/
│   ├── core/
│   │   ├── simulator.py      # Main CDN simulator implementation
│   │   └── __init__.py
│   ├── ml/
│   │   ├── traffic_predictor.py  # ML model for traffic prediction
│   │   └── __init__.py
│   ├── caching/
│   │   ├── cache_manager.py  # Cache management implementation
│   │   └── __init__.py
│   └── monitoring/
│       ├── metrics_collector.py  # Prometheus metrics collection
│       └── __init__.py
├── example.py                # Example usage and simulation
├── requirements.txt          # Python dependencies
├── prometheus.yml           # Prometheus configuration
├── grafana-dashboard.json   # Grafana dashboard configuration
└── README.md
```

## Dependencies

Key Python packages:
- numpy
- pandas
- scikit-learn
- prometheus-client
- redis-py

Services:
- Redis (for caching)
- Prometheus (for metrics collection)
- Grafana (for visualization)

## Troubleshooting

1. If ports are in use:
   ```bash
   # Check what's using ports
   lsof -i :3000,8000,9090
   
   # Stop services
   brew services stop grafana
   brew services stop prometheus
   ```

2. If metrics aren't showing:
   - Verify Prometheus is running: `brew services list`
   - Check Prometheus targets at http://localhost:9090/targets
   - Verify the simulator is exposing metrics at http://localhost:8000

3. If Grafana can't connect to Prometheus:
   - Verify Prometheus is running
   - Check the data source configuration in Grafana
   - Ensure the Prometheus URL is correct (http://localhost:9090)

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
