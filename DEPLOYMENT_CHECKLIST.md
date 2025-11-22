# 🚀 Mitel API Mock - Deployment Checklist

## ✅ Pre-Deployment Checklist

### Local Testing
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server starts successfully (`python app.py`)
- [ ] Health check works (`curl http://localhost:5000/api/health`)
- [ ] Test suite passes (`python test_api.py`)
- [ ] All endpoints return data (`./examples.sh`)

### Docker Testing
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Image builds successfully (`docker-compose build`)
- [ ] Container starts (`docker-compose up -d`)
- [ ] Health check passes from container
- [ ] Logs show no errors (`docker-compose logs`)

## 🔧 EC2 Deployment Checklist

### AWS Setup
- [ ] EC2 instance created (Ubuntu 20.04 LTS)
- [ ] Instance type: t2.small or larger
- [ ] Key pair created/downloaded (.pem file)
- [ ] Security Group configured:
  - [ ] Port 22 (SSH) open from your IP
  - [ ] Port 5000 (API) open from required IPs
- [ ] Elastic IP assigned (recommended for production)

### File Transfer
- [ ] All files copied to EC2:
  ```bash
  scp -i your-key.pem -r /path/to/mitel-api/* ubuntu@EC2_IP:~/mitel-api/
  ```
- [ ] Scripts are executable:
  ```bash
  chmod +x deploy-ec2.sh deploy-docker.sh examples.sh
  ```

### Deployment Method Selection

#### Option A: Docker Deployment (Recommended)
- [ ] Connect to EC2: `ssh -i your-key.pem ubuntu@EC2_IP`
- [ ] Navigate to directory: `cd ~/mitel-api`
- [ ] Run deployment: `./deploy-docker.sh`
- [ ] Verify container running: `docker ps`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Test health: `curl http://localhost:5000/api/health`

#### Option B: Systemd Deployment
- [ ] Connect to EC2: `ssh -i your-key.pem ubuntu@EC2_IP`
- [ ] Navigate to directory: `cd ~/mitel-api`
- [ ] Run deployment: `./deploy-ec2.sh`
- [ ] Verify service: `sudo systemctl status mitel-api-mock`
- [ ] Check logs: `sudo journalctl -u mitel-api-mock -f`
- [ ] Test health: `curl http://localhost:5000/api/health`

### Post-Deployment Verification
- [ ] API accessible from EC2: `curl http://localhost:5000/api/health`
- [ ] API accessible externally: `curl http://EC2_PUBLIC_IP:5000/api/health`
- [ ] All endpoints respond correctly
- [ ] Test with Postman collection
- [ ] Load test with multiple requests
- [ ] Check error logs for issues

## 🔒 Security Checklist

### Production Security
- [ ] Restrict Security Group port 5000 to specific IPs (not 0.0.0.0/0)
- [ ] Consider adding API authentication
- [ ] Enable HTTPS/SSL (use nginx reverse proxy)
- [ ] Set up CloudWatch monitoring
- [ ] Configure log rotation
- [ ] Implement rate limiting
- [ ] Use environment variables for sensitive config
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

### Optional Enhancements
- [ ] Set up nginx reverse proxy
- [ ] Configure SSL certificate (Let's Encrypt)
- [ ] Add API key authentication
- [ ] Set up CloudWatch alarms
- [ ] Configure auto-scaling
- [ ] Set up load balancer (for multiple instances)

## 📊 Monitoring Checklist

### Health Monitoring
- [ ] Set up monitoring endpoint check
- [ ] Configure CloudWatch metrics
- [ ] Set up alerts for downtime
- [ ] Monitor disk space
- [ ] Monitor memory usage
- [ ] Monitor CPU usage

### Log Management
- [ ] Configure log retention
- [ ] Set up log aggregation (CloudWatch Logs)
- [ ] Monitor error rates
- [ ] Set up alerts for errors

## 🧪 Testing Checklist

### Endpoint Testing
- [ ] `/` - API home
- [ ] `/api/health` - Health check
- [ ] `/api/v1/cdr` - CDR records (default)
- [ ] `/api/v1/cdr?limit=50` - CDR with limit
- [ ] `/api/v1/cdr?extension=694311` - Filter by extension
- [ ] `/api/v1/cdr?direction=I` - Filter by direction
- [ ] `/api/v1/cdr/stream` - Kafka format
- [ ] `/api/v1/cdr/export` - CSV export
- [ ] `/api/v1/extensions` - Extensions list
- [ ] `/api/v1/stats` - Statistics

### Performance Testing
- [ ] Single request response time < 200ms
- [ ] Handles 10 concurrent requests
- [ ] Handles 100 concurrent requests
- [ ] Memory usage stable
- [ ] No memory leaks over time

## 📝 Documentation Checklist

- [✓] README.md complete
- [✓] QUICKSTART.md available
- [✓] PROJECT_SUMMARY.md created
- [✓] STRUCTURE.md documented
- [✓] API endpoints documented
- [✓] Deployment process documented
- [✓] Postman collection provided
- [✓] Example scripts included

## 🎯 Final Verification

### From Local Machine
```bash
# Replace EC2_IP with your EC2 public IP
export API_URL="http://EC2_IP:5000"

# Health check
curl $API_URL/api/health

# Get CDR records
curl "$API_URL/api/v1/cdr?limit=5"

# Get statistics
curl $API_URL/api/v1/stats

# Export CSV
curl "$API_URL/api/v1/cdr/export?limit=10" > test_export.csv
```

### All Tests Passing
- [ ] Health check returns 200
- [ ] CDR endpoint returns data
- [ ] Kafka stream format works
- [ ] CSV export downloads
- [ ] Extensions list returns data
- [ ] Statistics endpoint works
- [ ] No errors in logs

## 🎉 Success Criteria

- ✅ API running on EC2
- ✅ All endpoints accessible
- ✅ No errors in logs
- ✅ Health check passes
- ✅ External access works
- ✅ Performance acceptable
- ✅ Documentation complete

## 🆘 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Can't connect to EC2 | Check Security Group port 5000 |
| Service won't start | Check logs: `sudo journalctl -u mitel-api-mock -f` |
| Docker container stops | Check logs: `docker-compose logs` |
| Port 5000 in use | Kill process: `sudo lsof -i :5000` |
| Permission denied | Run `chmod +x *.sh` |
| Module not found | Install deps: `pip install -r requirements.txt` |

## 📞 Support Resources

- **README.md** - Full documentation
- **QUICKSTART.md** - Quick start guide
- **examples.sh** - Usage examples
- **test_api.py** - Automated tests

## 🔄 Maintenance Checklist

### Weekly
- [ ] Check disk space
- [ ] Review error logs
- [ ] Monitor API performance

### Monthly
- [ ] Update dependencies
- [ ] Security patches: `sudo apt update && sudo apt upgrade`
- [ ] Review access logs
- [ ] Test backups (if configured)

### Quarterly
- [ ] Review and update documentation
- [ ] Performance optimization
- [ ] Security audit

---

## Quick Command Reference

```bash
# Start service
sudo systemctl start mitel-api-mock    # systemd
docker-compose up -d                    # Docker

# Stop service
sudo systemctl stop mitel-api-mock     # systemd
docker-compose stop                     # Docker

# Restart service
sudo systemctl restart mitel-api-mock  # systemd
docker-compose restart                  # Docker

# View logs
sudo journalctl -u mitel-api-mock -f   # systemd
docker-compose logs -f                  # Docker

# Check status
sudo systemctl status mitel-api-mock   # systemd
docker-compose ps                       # Docker
```

---

**Ready for deployment!** ✅

