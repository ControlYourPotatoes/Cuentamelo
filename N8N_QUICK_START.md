# N8N Quick Start Guide

## 🚀 Quick Setup

### 1. Enable Demo Mode

```bash
python scripts/enable_demo_mode.py
```

### 2. Test Connection

```bash
python scripts/test_n8n_demo_workflow.py
```

### 3. Start N8N (if not running)

```bash
docker-compose up n8n
```

### 4. Import Workflow

1. Open N8N at http://localhost:5678
2. Go to Workflows → Import from File
3. Select `n8n_workflow_cuentamelo.json`
4. Activate the workflow

### 5. Test Events

```bash
# Test individual events
python scripts/test_n8n_demo_workflow.py

# Or trigger a full demo scenario
curl -X POST http://localhost:8000/demo/trigger-scenario \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "political_announcement", "speed_multiplier": 2.0}'
```

## 📡 Webhook Endpoint

**Production URL**: `http://localhost:5678/webhook/cuentamelo-event`

This is the exact endpoint where all Cuentamelo events are sent.

## 🎯 Event Types

The workflow handles these event types:

- `news_discovered` - New Puerto Rican news
- `character_analyzing` - Character evaluating relevance
- `engagement_decision` - Character decides to respond
- `response_generating` - AI generating response
- `post_published` - Live Twitter post

## 🔧 Troubleshooting

### Events not showing in N8N?

1. Check demo mode is enabled: `DEMO_MODE_ENABLED=true`
2. Verify N8N is running on port 5678
3. Confirm workflow is active in N8N
4. Check webhook path is exactly: `cuentamelo-event`

### Connection issues?

```bash
# Test connection directly
curl -X POST http://localhost:5678/webhook/cuentamelo-event \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test", "data": {"test": true}}'
```

## 📊 Expected Results

When working correctly, you should see:

- ✅ All 8 tests passing
- 📡 Events flowing to N8N in real-time
- 🎭 Character workflows visualized
- 🐦 Twitter posts simulated

## 🎉 Success!

Once everything is working, you'll have a beautiful real-time visualization of your AI character orchestration system!
