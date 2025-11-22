# Mitel API Mock Server - Project Summary

## 📋 Overview

This project provides a fully functional mock API server that simulates a Mitel telephony system. It generates realistic Call Detail Records (CDR) data matching the structure found in Mitel MiVoice Business/CloudLink platforms.

## 🎯 Purpose

- **Development**: Test your applications without connecting to a real Mitel system
- **Integration Testing**: Validate data processing pipelines
- **Demos**: Showcase telephony analytics applications
- **Learning**: Understand Mitel CDR data structure

## 📁 Project Structure

```
mitel-api/
├── app.py                                    # Main Flask application (API server)
├── requirements.txt                          # Python dependencies for production
├── requirements-dev.txt                      # Additional dependencies for testing
├── Dockerfile                                # Docker container configuration
├── docker-compose.yml                        # Docker Compose setup
├── deploy-ec2.sh                            # EC2 deployment script (systemd)
├── deploy-docker.sh                         # Docker deployment script
├── test_api.py                              # Automated test suite
├── examples.sh                              # API usage examples
├── README.md                                # Full documentation
├── QUICKSTART.md                            # Quick start guide
├── Mitel_API_Mock.postman_collection.json   # Postman collection
└── resources/
    └── Telephonie_message_data.csv          # Sample data reference
```

## 🚀 Key Features

### API Endpoints

1. **Core Endpoints**
   - `GET /` - API information and documentation
   - `GET /api/health` - Health check

2. **CDR Endpoints**
   - `GET /api/v1/cdr` - Get Call Detail Records
   - `GET /api/v1/cdr/stream` - Get CDR in Kafka format
   - `GET /api/v1/cdr/export` - Export CDR as CSV

3. **Management Endpoints**
   - `GET /api/v1/extensions` - List extensions
   - `GET /api/v1/stats` - Call statistics

### Mock Data Features

- **Realistic CDR records** with 50+ fields
- **Multiple call types**: Inbound, Outbound, Internal
- **Random but realistic data**: Phone numbers, extensions, usernames
- **Kafka-style message format**: Matches actual Mitel data stream
- **Configurable limits**: Control number of records returned

## 🛠 Technology Stack

- **Language**: Python 3.11+
- **Framework**: Flask (lightweight REST API)
- **WSGI Server**: Gunicorn (production)
- **Containerization**: Docker & Docker Compose
- **Deployment**: AWS EC2, systemd

## 📊 Data Structure

The API generates CDR records with fields including:

- **Call Information**: RecordId, CallId, Call_date, Duration
- **Parties**: Extno, Username, Number, Port
- **Call Flow**: Direction, Transfer, Call_legs, Call_outcome
- **Quality Metrics**: Ring_time, Wait_time, Hold_duration
- **Journey Data**: JourneyOutcome, ContactPoints, CallExperienceRating
- **Technical**: LegID, DeviceId, TenantId

## 🔧 Deployment Options

### 1. Local Development
```bash
pip install -r requirements.txt
python app.py
```
**Best for**: Quick testing and development

### 2. Docker
```bash
docker-compose up -d
```
**Best for**: Consistent environment, easy deployment

### 3. AWS EC2
```bash
./deploy-ec2.sh  # or ./deploy-docker.sh
```
**Best for**: Cloud hosting, production use

## 📖 Usage Examples

### Basic Request
```bash
curl http://localhost:5000/api/v1/cdr?limit=10
```

### Filter by Extension
```bash
curl http://localhost:5000/api/v1/cdr?extension=694311
```

### Get Kafka Format
```bash
curl http://localhost:5000/api/v1/cdr/stream?limit=5
```

### Export as CSV
```bash
curl http://localhost:5000/api/v1/cdr/export?limit=100 > cdr.csv
```

## 🧪 Testing

Run the automated test suite:
```bash
pip install -r requirements-dev.txt
python test_api.py
```

Or run example requests:
```bash
./examples.sh
```

## 📦 What's Included

### Core Files
- ✅ Flask API application with 7+ endpoints
- ✅ Mock data generator with realistic patterns
- ✅ Kafka message format support
- ✅ CSV export functionality

### Deployment
- ✅ Docker configuration (Dockerfile + docker-compose.yml)
- ✅ EC2 systemd deployment script
- ✅ Docker deployment script
- ✅ Production-ready with Gunicorn

### Documentation
- ✅ Comprehensive README
- ✅ Quick start guide
- ✅ API usage examples
- ✅ Postman collection

### Testing
- ✅ Automated test suite
- ✅ Example requests script
- ✅ Health check endpoint

## 🔒 Security Notes

This is a **mock API for development**. For production:

- Add authentication (API keys, OAuth, JWT)
- Enable HTTPS/TLS
- Restrict CORS origins
- Implement rate limiting
- Use environment variables for secrets
- Add input validation

## 📈 Next Steps

1. **Test locally**: `python app.py`
2. **Deploy to EC2**: Follow QUICKSTART.md
3. **Integrate**: Point your application to the API
4. **Customize**: Modify mock data in app.py
5. **Scale**: Add more endpoints as needed

## 💡 Customization

To modify mock data:
1. Edit `app.py`
2. Update `USERNAMES`, `EXTENSIONS`, or other data pools
3. Modify `generate_cdr_record()` function
4. Restart the server

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | `sudo lsof -i :5000` and kill process |
| Can't connect to EC2 | Check Security Group port 5000 |
| Docker build fails | `docker-compose build --no-cache` |
| Module not found | `pip install -r requirements.txt` |

## 📝 API Response Format

All endpoints return JSON with this structure:

```json
{
  "success": true,
  "count": 10,
  "records": [...],
  "timestamp": "2025-11-20T10:30:00"
}
```

## 🌟 Highlights

- **Zero Configuration**: Works out of the box
- **Fully Documented**: README, examples, Postman collection
- **Production Ready**: Docker + Gunicorn + systemd
- **Easy Deployment**: One-command EC2 setup
- **Realistic Data**: Matches actual Mitel CDR format

## 📞 Support

For questions or issues:
1. Check README.md for detailed documentation
2. Review QUICKSTART.md for deployment help
3. Check logs for error messages
4. Verify all dependencies are installed

## ✨ Summary

This mock API provides everything you need to develop and test applications that consume Mitel telephony data, without requiring access to a real Mitel system. It's ready to deploy to EC2 and start generating realistic CDR data immediately.

**Ready to use in 5 minutes!** 🚀

