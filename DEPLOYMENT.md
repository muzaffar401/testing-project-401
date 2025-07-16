# Deployment Guide for Choreo

This guide will help you deploy your Health & Wellness Planner Agent to Choreo.

## Prerequisites

1. **Choreo Account**: Sign up at [choreo.dev](https://choreo.dev)
2. **Docker Hub Account**: For container registry
3. **OpenAI API Key**: Required for the AI agents
4. **Git Repository**: Your code should be in a Git repository

## Architecture Overview

Your application consists of two main services:

1. **Backend Service** (Python/FastAPI)
   - Port: 8000
   - Health endpoint: `/health`
   - Main API endpoint: `/chat`

2. **Frontend Service** (Next.js)
   - Port: 3000
   - Proxies `/chat` requests to backend

## Step 1: Prepare Your Repository

### 1.1 Environment Variables

Create a `.env` file in the `python-backend` directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 1.2 Update CORS Settings

The backend is already configured to allow Choreo domains. The CORS settings in `python-backend/api.py` include:

```python
allow_origins=["http://localhost:3000", "https://*.choreo.dev"]
```

## Step 2: Build and Push Docker Images

### 2.1 Build Backend Image

```bash
# Build the backend image
docker build -t your-dockerhub-username/health-planner-backend:latest .

# Push to Docker Hub
docker push your-dockerhub-username/health-planner-backend:latest
```

### 2.2 Build Frontend Image

```bash
# Build the frontend image
cd ui
docker build -t your-dockerhub-username/health-planner-frontend:latest .

# Push to Docker Hub
docker push your-dockerhub-username/health-planner-frontend:latest
```

## Step 3: Deploy to Choreo

### 3.1 Create Backend Service

1. **Log into Choreo Console**
2. **Create New Service** → **Container**
3. **Configure Backend Service**:

```yaml
# Service Configuration
Name: health-planner-backend
Image: your-dockerhub-username/health-planner-backend:latest
Port: 8000

# Environment Variables
OPENAI_API_KEY: your_openai_api_key_here

# Health Check
Path: /health
Interval: 30s
Timeout: 10s
Initial Delay: 40s

# Resources (Recommended)
CPU: 0.5 cores
Memory: 1GB
```

### 3.2 Create Frontend Service

1. **Create Another Service** → **Container**
2. **Configure Frontend Service**:

```yaml
# Service Configuration
Name: health-planner-frontend
Image: your-dockerhub-username/health-planner-frontend:latest
Port: 3000

# Environment Variables
BACKEND_URL: https://your-backend-service-url.choreo.dev/chat

# Health Check
Path: /
Interval: 30s
Timeout: 10s
Initial Delay: 40s

# Resources (Recommended)
CPU: 0.5 cores
Memory: 512MB
```

### 3.3 Configure Service Communication

1. **In Frontend Service Settings**:
   - Set `BACKEND_URL` to your backend service URL
   - Example: `https://health-planner-backend-abc123.choreo.dev/chat`

2. **Update CORS in Backend** (if needed):
   - Add your frontend service URL to allowed origins

## Step 4: Configure Custom Domains (Optional)

### 4.1 Backend Domain
```
api.yourdomain.com → health-planner-backend.choreo.dev
```

### 4.2 Frontend Domain
```
yourdomain.com → health-planner-frontend.choreo.dev
```

## Step 5: Environment Variables Management

### 5.1 Secure Environment Variables

In Choreo Console:
1. Go to your backend service
2. Navigate to **Environment Variables**
3. Add:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ENVIRONMENT`: `production`

### 5.2 Frontend Environment Variables

For the frontend service:
- `BACKEND_URL`: Your backend service URL
- `NODE_ENV`: `production`

## Step 6: Monitoring and Logs

### 6.1 Health Checks

Both services include health checks:
- **Backend**: `GET /health`
- **Frontend**: `GET /` (Next.js default)

### 6.2 Logs

Access logs through Choreo Console:
1. Select your service
2. Go to **Logs** tab
3. Monitor for any errors or issues

## Step 7: Scaling Configuration

### 7.1 Backend Scaling

```yaml
# Recommended for production
Min Replicas: 2
Max Replicas: 10
CPU Target: 70%
Memory Target: 80%
```

### 7.2 Frontend Scaling

```yaml
# Recommended for production
Min Replicas: 2
Max Replicas: 5
CPU Target: 70%
Memory Target: 80%
```

## Step 8: Testing Your Deployment

### 8.1 Test Backend Health

```bash
curl https://your-backend-service.choreo.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123
}
```

### 8.2 Test Frontend

1. Visit your frontend URL
2. Try the chat interface
3. Verify agent responses

### 8.3 Test API Communication

```bash
curl -X POST https://your-backend-service.choreo.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to lose 5kg in 2 months"}'
```

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Verify CORS settings in backend
   - Check frontend URL is in allowed origins

2. **Connection Timeouts**:
   - Verify `BACKEND_URL` environment variable
   - Check service health status

3. **OpenAI API Errors**:
   - Verify `OPENAI_API_KEY` is set correctly
   - Check API key permissions and quota

4. **Memory Issues**:
   - Increase memory allocation
   - Monitor resource usage

### Debug Commands

```bash
# Check backend logs
choreo logs health-planner-backend

# Check frontend logs
choreo logs health-planner-frontend

# Test backend connectivity
curl -v https://your-backend-service.choreo.dev/health
```

## Security Considerations

1. **API Keys**: Never commit API keys to Git
2. **Environment Variables**: Use Choreo's secure environment variable management
3. **HTTPS**: Choreo provides automatic HTTPS
4. **CORS**: Configure properly for production domains

## Cost Optimization

1. **Resource Allocation**: Start with minimal resources and scale up
2. **Auto-scaling**: Configure based on actual usage patterns
3. **Monitoring**: Use Choreo's built-in monitoring to optimize costs

## Next Steps

1. **Set up monitoring** with Choreo's built-in tools
2. **Configure alerts** for service health
3. **Set up CI/CD** for automated deployments
4. **Add custom domains** for production use
5. **Implement backup strategies** for conversation state

## Support

- **Choreo Documentation**: [docs.choreo.dev](https://docs.choreo.dev)
- **Choreo Community**: [community.choreo.dev](https://community.choreo.dev)
- **OpenAI Agents SDK**: [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) 