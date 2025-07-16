# Health & Wellness Planner Agent - Choreo Deployment Summary

## Project Overview

Your **Health & Wellness Planner Agent** is a sophisticated AI-powered application that provides personalized health and wellness planning through a multi-agent system. The application consists of two main components:

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (Next.js)     │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │   OpenAI API    │
         │              │   (Agents SDK)  │
         └──────────────┘                 │
                                          │
                                          ▼
                              ┌─────────────────┐
                              │  Multi-Agent    │
                              │   System        │
                              │                 │
                              │ • Health Planner│
                              │ • Nutrition Exp │
                              │ • Injury Support│
                              │ • Escalation    │
                              └─────────────────┘
```

### 🤖 AI Agents

1. **Health & Wellness Planner** (Main Agent)
   - Coordinates all health activities
   - Manages user goals and progress
   - Handles agent handoffs

2. **Nutrition Expert**
   - Specialized dietary planning
   - Meal plan generation
   - Dietary preference handling

3. **Injury Support**
   - Safe exercise modifications
   - Injury recovery guidance
   - Low-impact workout plans

4. **Escalation Agent**
   - Human coach connections
   - Complex case handling
   - Support escalation

### 🛠️ Key Features

- **Real-time Chat Interface**: Interactive conversation with AI agents
- **Goal Analysis**: Structured health goal processing
- **Meal Planning**: 7-day personalized meal plans
- **Workout Recommendations**: Exercise plans based on goals and injuries
- **Progress Tracking**: Session-based progress monitoring
- **Guardrails**: Input validation and health relevance checks
- **Agent Visualization**: Real-time agent interaction display

## 🚀 Deployment Strategy

### Containerization Approach

The application is containerized using Docker with two separate services:

1. **Backend Container** (`Dockerfile`)
   - Python 3.11 slim image
   - FastAPI with Uvicorn
   - Health check endpoint
   - Non-root user for security

2. **Frontend Container** (`ui/Dockerfile`)
   - Node.js 18 Alpine image
   - Next.js standalone build
   - Optimized for production
   - Multi-stage build for efficiency

### Choreo Deployment Benefits

✅ **Automatic Scaling**: Horizontal pod autoscaling based on CPU/memory usage
✅ **Health Monitoring**: Built-in health checks and monitoring
✅ **SSL/TLS**: Automatic HTTPS certificates
✅ **Load Balancing**: Built-in load balancer
✅ **Environment Management**: Secure environment variable handling
✅ **Logging**: Centralized log management
✅ **Cost Optimization**: Pay-per-use pricing model

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Set up Choreo account
- [ ] Create Docker Hub account
- [ ] Get OpenAI API key
- [ ] Test locally with `./deploy-local.sh`

### Backend Service Configuration
- [ ] Image: `your-username/health-planner-backend:latest`
- [ ] Port: 8000
- [ ] Environment Variables:
  - `OPENAI_API_KEY`
  - `ENVIRONMENT=production`
- [ ] Health Check: `/health`
- [ ] Resources: 0.5 CPU, 1GB RAM

### Frontend Service Configuration
- [ ] Image: `your-username/health-planner-frontend:latest`
- [ ] Port: 3000
- [ ] Environment Variables:
  - `BACKEND_URL`
  - `NODE_ENV=production`
- [ ] Health Check: `/`
- [ ] Resources: 0.5 CPU, 512MB RAM

### Post-Deployment
- [ ] Test health endpoints
- [ ] Verify agent functionality
- [ ] Monitor logs for errors
- [ ] Set up custom domains (optional)
- [ ] Configure auto-scaling

## 🔧 Technical Details

### API Endpoints

**Backend Service:**
- `GET /health` - Health check
- `POST /chat` - Main chat endpoint

**Request Format:**
```json
{
  "conversation_id": "optional_conversation_id",
  "message": "user message"
}
```

**Response Format:**
```json
{
  "conversation_id": "uuid",
  "current_agent": "agent_name",
  "messages": [...],
  "events": [...],
  "context": {...},
  "agents": [...],
  "guardrails": [...]
}
```

### Environment Variables

**Backend:**
```bash
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
```

**Frontend:**
```bash
BACKEND_URL=https://your-backend-service.choreo.dev/chat
NODE_ENV=production
```

### Scaling Configuration

**Backend:**
- Min Replicas: 2
- Max Replicas: 10
- CPU Target: 70%
- Memory Target: 80%

**Frontend:**
- Min Replicas: 2
- Max Replicas: 5
- CPU Target: 70%
- Memory Target: 80%

## 🛡️ Security Considerations

1. **API Key Management**: Use Choreo's secure environment variables
2. **CORS Configuration**: Properly configured for production domains
3. **HTTPS**: Automatic SSL/TLS certificates
4. **Non-root Containers**: Both services run as non-root users
5. **Health Checks**: Regular health monitoring

## 📊 Monitoring & Observability

### Health Checks
- Backend: `GET /health` returns status and timestamp
- Frontend: Next.js default health check

### Logging
- Structured logging in both services
- Centralized log collection in Choreo
- Error tracking and alerting

### Metrics
- CPU and memory usage
- Request latency
- Error rates
- Custom business metrics

## 💰 Cost Optimization

### Resource Allocation
- Start with minimal resources (0.5 CPU, 512MB-1GB RAM)
- Scale based on actual usage patterns
- Use auto-scaling to handle traffic spikes

### Optimization Tips
- Monitor resource usage in Choreo dashboard
- Adjust scaling parameters based on usage
- Use appropriate instance types for your workload
- Implement caching strategies if needed

## 🔄 CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:

1. **Tests**: Runs Python and Node.js tests
2. **Builds**: Creates optimized Docker images
3. **Pushes**: Uploads images to Docker Hub
4. **Deploys**: Can be configured to deploy to Choreo

### Required Secrets
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password/token
- `OPENAI_API_KEY`: OpenAI API key
- `BACKEND_URL`: Backend service URL

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify CORS settings in backend
   - Check frontend URL in allowed origins

2. **Connection Timeouts**
   - Verify `BACKEND_URL` environment variable
   - Check service health status

3. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check API key permissions and quota

4. **Memory Issues**
   - Increase memory allocation
   - Monitor resource usage

### Debug Commands

```bash
# Test backend health
curl https://your-backend-service.choreo.dev/health

# Test API communication
curl -X POST https://your-backend-service.choreo.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to lose 5kg in 2 months"}'

# Check service logs in Choreo console
```

## 📚 Next Steps

1. **Deploy to Choreo** following the detailed guide in `DEPLOYMENT.md`
2. **Set up monitoring** with Choreo's built-in tools
3. **Configure alerts** for service health
4. **Add custom domains** for production use
5. **Implement backup strategies** for conversation state
6. **Set up CI/CD** for automated deployments

## 📞 Support Resources

- **Choreo Documentation**: [docs.choreo.dev](https://docs.choreo.dev)
- **Choreo Community**: [community.choreo.dev](https://community.choreo.dev)
- **OpenAI Agents SDK**: [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Next.js Documentation**: [nextjs.org/docs](https://nextjs.org/docs)

---

**Ready to deploy?** Follow the step-by-step guide in `DEPLOYMENT.md` to get your Health & Wellness Planner Agent running on Choreo! 🚀 