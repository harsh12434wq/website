# DSS Group Website

A fully functional corporate website for **Defensive Security Services (DSS Group)**, built with:
- **Frontend**: Pure HTML/CSS/JS Single Page Application (no build step required)
- **Backend**: FastAPI + Mangum (AWS Lambda-compatible)
- **Deployment**: AWS Lambda + API Gateway (or locally with uvicorn)

---

## 🚀 Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dev server
uvicorn main:app --reload --port 8000

# 3. Open http://localhost:8000
```

---

## ☁️ AWS Lambda Deployment

### Option A: AWS Lambda + API Gateway (Recommended for 10–15 users/day)

**Step 1: Package the app**
```bash
pip install -r requirements.txt -t package/
cp main.py package/
cp -r static/ package/static/
cd package && zip -r ../dss_website.zip . && cd ..
```

**Step 2: Create Lambda Function**
- Go to AWS Lambda → Create Function
- Runtime: Python 3.12
- Handler: `main.handler`
- Upload `dss_website.zip`
- Memory: 256 MB, Timeout: 30s

**Step 3: Create API Gateway**
- Go to API Gateway → Create API → HTTP API
- Add Lambda integration → Select your function
- Route: `$default` (catches all routes)
- Deploy → Copy the URL

**Step 4: (Optional) Custom Domain**
- Register domain in Route53
- Create ACM certificate
- Add custom domain in API Gateway

### Option B: Lambda Container Image

```dockerfile
FROM public.ecr.aws/lambda/python:3.12
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
COPY static/ static/
CMD ["main.handler"]
```

```bash
# Build and push to ECR
docker build -t dss-website .
aws ecr create-repository --repository-name dss-website
docker tag dss-website:latest <ACCOUNT>.dkr.ecr.ap-south-1.amazonaws.com/dss-website:latest
docker push <ACCOUNT>.dkr.ecr.ap-south-1.amazonaws.com/dss-website:latest
```

---

## 📧 Adding Email Notifications (AWS SES)

In `main.py`, inside the `handle_contact` function, uncomment and configure:

```python
import boto3

ses = boto3.client('ses', region_name='ap-south-1')
ses.send_email(
    Source='noreply@yourdomain.com',
    Destination={'ToAddresses': ['info@yourdomain.com']},
    Message={
        'Subject': {'Data': f'New Inquiry from {form.name}'},
        'Body': {
            'Text': {
                'Data': f'''
Name: {form.name}
Phone: {form.phone}
Email: {form.email}
Service: {form.service}
Message: {form.message}
                '''
            }
        }
    }
)
```

Add SES permissions to your Lambda IAM role:
```json
{
  "Effect": "Allow",
  "Action": "ses:SendEmail",
  "Resource": "*"
}
```

---

## 📁 Project Structure

```
dss_website/
├── main.py              # FastAPI app + Lambda handler
├── requirements.txt     # Python dependencies
├── README.md
└── static/
    └── index.html       # Complete SPA (all 4 pages)
```

---

## 🔧 Customization

Before deploying, update these in `static/index.html`:
- Phone number (search: "Please update with your number")
- Email address (search: "Please update with your email")

And in `main.py`:
- SES email addresses
- Any CRM/database integrations

---

## 💰 Cost Estimate (AWS Lambda, 10–15 users/day)

| Service | Monthly Cost |
|---------|-------------|
| Lambda (free tier: 1M requests) | ~$0.00 |
| API Gateway HTTP API | ~$0.01 |
| **Total** | **~Free** |

Well within AWS Free Tier for this traffic level.
