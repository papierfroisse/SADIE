"""Script to start monitoring services."""
import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(debug: bool = False):
    """Setup logging configuration.
    
    Args:
        debug: Enable debug logging
    """
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_prerequisites():
    """Check if required services are installed."""
    missing = []
    
    # Check Prometheus
    try:
        subprocess.run(['prometheus', '--version'], capture_output=True)
    except FileNotFoundError:
        missing.append('prometheus')
        
    # Check Node Exporter
    try:
        subprocess.run(['node_exporter', '--version'], capture_output=True)
    except FileNotFoundError:
        missing.append('node_exporter')
        
    # Check Redis Exporter
    try:
        subprocess.run(['redis_exporter', '--version'], capture_output=True)
    except FileNotFoundError:
        missing.append('redis_exporter')
        
    # Check Grafana
    try:
        subprocess.run(['grafana-server', '-v'], capture_output=True)
    except FileNotFoundError:
        missing.append('grafana')
        
    if missing:
        logger.error(f"Missing services: {', '.join(missing)}")
        logger.info("Please install missing services using the installation guide")
        sys.exit(1)

def start_prometheus():
    """Start Prometheus server."""
    try:
        logger.info("Starting Prometheus...")
        subprocess.Popen([
            'prometheus',
            '--config.file=prometheus.yml',
            '--storage.tsdb.path=data/prometheus'
        ])
    except Exception as e:
        logger.error(f"Failed to start Prometheus: {str(e)}")
        sys.exit(1)

def start_node_exporter():
    """Start Node Exporter."""
    try:
        logger.info("Starting Node Exporter...")
        subprocess.Popen(['node_exporter'])
    except Exception as e:
        logger.error(f"Failed to start Node Exporter: {str(e)}")
        sys.exit(1)

def start_redis_exporter():
    """Start Redis Exporter."""
    try:
        logger.info("Starting Redis Exporter...")
        subprocess.Popen([
            'redis_exporter',
            '--redis.addr=redis://localhost:6379'
        ])
    except Exception as e:
        logger.error(f"Failed to start Redis Exporter: {str(e)}")
        sys.exit(1)

def start_grafana():
    """Start Grafana server."""
    try:
        logger.info("Starting Grafana...")
        subprocess.Popen([
            'grafana-server',
            '--config=/etc/grafana/grafana.ini',
            '--homepath=/usr/share/grafana'
        ])
    except Exception as e:
        logger.error(f"Failed to start Grafana: {str(e)}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Start monitoring services')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)

    # Create data directory
    data_dir = Path('data/prometheus')
    data_dir.mkdir(parents=True, exist_ok=True)

    # Check prerequisites
    check_prerequisites()

    # Start services
    start_prometheus()
    start_node_exporter()
    start_redis_exporter()
    start_grafana()

    logger.info("""
Monitoring services started:
- Prometheus: http://localhost:9090
- Node Exporter: http://localhost:9100
- Redis Exporter: http://localhost:9121
- Grafana: http://localhost:3000

Default Grafana credentials:
- Username: admin
- Password: admin
    """)

if __name__ == '__main__':
    main() 