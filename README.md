# AI Cloud Cost Autopilot

AI Cloud Cost Autopilot is an intelligent cloud infrastructure optimization platform that analyzes resource utilization across multiple cloud providers and automatically recommends cost-saving strategies.

The system monitors compute, storage, and network usage, identifies inefficient resources, and generates automated scaling recommendations to reduce operational costs.



# Features

• Multi-cloud cost analysis (AWS, GCP, Azure)

• AI-powered infrastructure optimization

• Automated cost-saving recommendations

• Background job processing for infrastructure analysis

• Real-time analytics dashboard

• Containerized microservices architecture



# Tech Stack

Backend
- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery

Frontend
- React
- Vite.js
- TailwindCSS

Infrastructure
- Docker
- Kubernetes
- AWS
- Google Cloud
- Microsoft Azure

DevOps
- Git
- GitHub
- Docker Compose



# Architecture

The platform consists of three core layers:

1. Data Collection Layer  
Collects infrastructure metrics from cloud providers.

2. Analysis Engine  
Processes metrics using background workers powered by Celery and Redis.

3. Recommendation Engine  
Generates automated scaling and cost optimization suggestions.


## Setup

### Backend

cd backend
pip install -r requirements.txt
python manage.py runserver


cd autopilot-dashboard
npm install
npm run dev

















