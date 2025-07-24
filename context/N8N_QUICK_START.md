# N8N Integration Quick Start Guide

## Overview

This guide will help you get your N8N workflow connected to your Cuentamelo API for real-time AI character orchestration visualization.

## Prerequisites

1. **N8N Running**: Make sure N8N is running on `http://localhost:5678`
2. **API Running**: Your FastAPI server should be running on `http://localhost:8000`
3. **Environment Setup**: Configure your `.env` file with N8N settings

## Step 1: Environment Configuration

Add these settings to your `.env` file:

```env
# N8N Integration Settings
N8N_WEBHOOK_URL=http://localhost:5678
DEMO_MODE_ENABLED=true
N8N_WEBHOOK_TIMEOUT=5
DEMO_SPEED_MULTIPLIER=1.0
```

## Step 2: Start Your API

```bash
# From your project root directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 3: Test the Integration

Run the test script to verify everything is working:

```bash
python scripts/test_n8n_integration.py
```

This will test:

- ✅ API health
- ✅ Demo endpoints
- ✅ N8N connection
- ✅ Webhook events
- ✅ Demo start functionality

## Step 4: Import Your Workflow

1. Open N8N at `http://localhost:5678`
2. Import your workflow JSON file: `configs/fixed_n8n_workflow (28).json`
3. The workflow should show:
   - **Start Demo** (Manual Trigger)
   - **Trigger Python** (HTTP Request to `http://localhost:8000/api/demo/start`)
   - **Event Receiver** (Webhook at `/webhook/cuentamelo-event`)
   - **Character Checks** (If nodes for Jovani and Ciudadano)
   - **Display Nodes** (Set nodes for character information)
   - **Response** (Respond to Webhook)

## Step 5: Test the Workflow

1. **Click "Start Demo"** in N8N
2. This will trigger the HTTP request to your API
3. Your API will start a demo scenario
4. Events will be sent to the N8N webhook
5. You'll see the workflow execute in real-time

## API Endpoints

Your API now includes these demo endpoints:

- `POST /demo/start` - Start a demo (called by N8N)
- `GET /demo/scenarios` - List available scenarios
- `GET /demo/status` - Get demo status
- `POST /demo/test-connection` - Test N8N connection
- `POST /demo/test-webhook` - Test webhook event
- `POST /demo/trigger-scenario` - Trigger specific scenario
- `POST /demo/custom-news` - Inject custom news

## Troubleshooting

### API Not Starting

```bash
# Check if port 8000 is available
netstat -an | grep 8000

# Try different port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### N8N Connection Failed

1. Check if N8N is running: `http://localhost:5678`
2. Verify webhook URL in `.env`: `N8N_WEBHOOK_URL=http://localhost:5678`
3. Enable demo mode: `DEMO_MODE_ENABLED=true`

### Workflow Not Triggering

1. Check the webhook URL in your workflow: `/webhook/cuentamelo-event`
2. Verify the HTTP request URL: `http://localhost:8000/api/demo/start`
3. Check N8N logs for errors

### Events Not Flowing

1. Run the test script to verify connection
2. Check API logs for webhook errors
3. Verify N8N webhook is active and listening

## Expected Workflow Behavior

When you click "Start Demo" in N8N:

1. **HTTP Request** → `POST http://localhost:8000/api/demo/start`
2. **API Response** → Starts demo scenario in background
3. **Events Sent** → Multiple events sent to N8N webhook:

   - `demo_started`
   - `news_discovered`
   - `character_analyzing`
   - `engagement_decision`
   - `response_generating`
   - `post_published`
   - `demo_stopped`

4. **Workflow Execution** → Each event triggers workflow nodes
5. **Visual Display** → Character information displayed in N8N

## Next Steps

Once the basic integration is working:

1. **Enhance the Workflow**: Add more visual elements, routing, and formatting
2. **Add More Scenarios**: Create additional demo scenarios
3. **Real Twitter Integration**: Connect to actual Twitter posting
4. **Performance Monitoring**: Add metrics and analytics
5. **Production Deployment**: Deploy to production environment

## Support

If you encounter issues:

1. Check the test script output for specific errors
2. Review API logs for webhook communication issues
3. Verify N8N workflow configuration
4. Test individual endpoints using the API documentation at `http://localhost:8000/docs`

---

**Happy orchestrating! 🎭🤖**
