# Mitel API Mock Server

A comprehensive mock API server that simulates a Mitel telephony system, generating realistic Call Detail Records (CDR) based on Mitel MiVoice Business/CloudLink platform structure.

## Features

- 🎯 **RESTful API** endpoints for CDR retrieval
- 📊 **Realistic mock data** generation matching Mitel's CDR format
- 🔄 **Kafka-style streaming** format support
- 📈 **Statistics endpoints** for call analytics
- 🐳 **Docker support** for easy deployment
- ☁️ **EC2-ready** with automated deployment scripts
- 🔒 **CORS enabled** for frontend development

## API Endpoints

### Core Endpoints

- `GET /` - API home and documentation
- `GET /api/health` - Health check endpoint

### CDR Endpoints

- `GET /api/v1/cdr` - Get Call Detail Records
  - Query params: `limit`, `from_date`, `to_date`, `extension`, `direction`
- `GET /api/v1/cdr/stream` - Get CDR in Kafka message format
  - Query params: `limit`
- `GET /api/v1/cdr/export` - Export CDR as CSV file
  - Query params: `limit`

### Management Endpoints

- `GET /api/v1/extensions` - Get list of extensions
- `GET /api/v1/stats` - Get call statistics

## Data Structure

The mock API generates CDR records with the following structure:

```json
{
  "RecordId": 78337984,
  "Extno": "694311",
  "Username": "PTP AG4311,METZ",
  "Call_date": "2025-09-25T10:25:03",
  "Number": "+33123456789",
  "Port": "+33987654321",
  "Ring_time": 0,
  "Duration": 243,
  "Direction": "I",
  "CallId": "K1013687",
  "Call_outcome": "103",
  "TenantId": "1",
  "JourneyOutcome": "701",
  "CallExperienceRating": "4",
  ...
}
```

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   cd /path/to/mitel-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python app.py
   ```

4. **Test the API**
   ```bash
   curl http://localhost:5000/api/health
   curl http://localhost:5000/api/v1/cdr?limit=5
   ```

### Docker Deployment (Recommended)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the service**
   ```bash
   docker-compose down
   ```

### Production Deployment with Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## EC2 Deployment

### Option 1: Automated Docker Deployment (Recommended)

1. **Connect to your EC2 instance**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-public-ip
   ```

2. **Copy the application files**
   ```bash
   # From your local machine
   scp -i your-key.pem -r ./* ec2-user@your-ec2-ip:/home/ec2-user/mitel-api
   ```

3. **Run the Docker deployment script**
   ```bash
   cd /home/ec2-user/mitel-api
   chmod +x deploy-docker.sh
   ./deploy-docker.sh
   ```

### Option 2: Manual EC2 Setup

1. **Connect to EC2**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-public-ip
   ```

2. **Copy files and run setup script**
   ```bash
   scp -i your-key.pem -r ./* ec2-user@your-ec2-ip:/home/ec2-user/mitel-api
   ssh -i your-key.pem ec2-user@your-ec2-ip
   cd /home/ec2-user/mitel-api
   chmod +x deploy-ec2.sh
   ./deploy-ec2.sh
   ```

3. **Configure EC2 Security Group**
   - Add inbound rule: Custom TCP, Port 5000, Source: 0.0.0.0/0 (or your IP)
   - Keep SSH port 22 open

4. **Test the deployment**
   ```bash
   curl http://your-ec2-public-ip:5000/api/health
   ```

## EC2 Instance Requirements

- **Instance Type**: t2.micro or larger (t2.small recommended)
- **AMI**: Amazon Linux 2023 or Amazon Linux 2
- **Storage**: 8 GB minimum
- **Security Group**: 
  - Port 22 (SSH)
  - Port 5000 (API)

## API Usage Examples

### Get CDR Records

```bash
# Get 10 records (default)
curl http://localhost:5000/api/v1/cdr

# Get 50 records
curl http://localhost:5000/api/v1/cdr?limit=50

# Filter by extension
curl http://localhost:5000/api/v1/cdr?extension=694311

# Filter by direction (I=Inbound, O=Outbound, B=Both)
curl http://localhost:5000/api/v1/cdr?direction=I&limit=20
```

### Get Kafka-formatted Stream

```bash
curl http://localhost:5000/api/v1/cdr/stream?limit=10
```

### Export as CSV

```bash
curl http://localhost:5000/api/v1/cdr/export?limit=100 > cdr_export.csv
```

### Get Extensions

```bash
curl http://localhost:5000/api/v1/extensions
```

### Get Call Statistics

```bash
curl http://localhost:5000/api/v1/stats
```

## Response Examples

### CDR Response

```json
{
  "success": true,
  "count": 2,
  "records": [
    {
      "RecordId": 78337984,
      "Extno": "694311",
      "Username": "PTP AG4311,METZ",
      "Call_date": "2025-09-25T10:25:03",
      "Duration": 243,
      "Direction": "I",
      ...
    }
  ],
  "timestamp": "2025-11-20T10:30:00"
}
```

### Kafka Stream Response

```json
{
  "success": true,
  "count": 1,
  "messages": [
    {
      "timestamp": 1758814963690,
      "timestampType": "CREATE_TIME",
      "partition": 0,
      "offset": 25393546,
      "key": {"key": "78337984"},
      "value": { /* CDR record */ },
      "headers": []
    }
  ]
}
```

## Configuration

Environment variables (optional):

- `PORT` - Server port (default: 5000)
- `FLASK_ENV` - Environment (production/development)
- `HOST` - Server host (default: 0.0.0.0)

## Development

### Project Structure

```
mitel-api/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── deploy-ec2.sh         # EC2 deployment script
├── deploy-docker.sh      # Docker deployment script
├── README.md             # This file
└── resources/            # Sample data files
    └── Telephonie_message_data.csv
```

### Adding New Features

The mock data generator in `app.py` can be extended to:
- Add more realistic phone number patterns
- Include additional CDR fields
- Implement authentication
- Add database persistence
- Support filtering by date ranges

## Monitoring

### Check Service Status (systemd deployment)

```bash
sudo systemctl status mitel-api-mock
```

### View Logs (systemd deployment)

```bash
sudo journalctl -u mitel-api-mock -f
```

### View Logs (Docker deployment)

```bash
docker-compose logs -f
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### EC2 Connection Issues

- Verify Security Group allows port 5000
- Check service status: `sudo systemctl status mitel-api-mock`
- Check logs: `sudo journalctl -u mitel-api-mock -f`
- Verify firewall: `sudo ufw status`

## Security Considerations

For production use, consider:
- Adding API authentication (API keys, OAuth)
- Enabling HTTPS with SSL certificates
- Restricting CORS origins
- Implementing rate limiting
- Using environment variables for sensitive config

## License

This is a mock API for development purposes.

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Ensure ports are not blocked by firewall

## Related Resources

- [Mitel Developer Portal](https://developer.mitel.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

