# Analytics Tracking Guidelines

**IMPORTANT**: All new features, buttons, and user interactions MUST include PostHog tracking.

## When Adding New Features

**1. Add Event Constants First** (`bigbongo/analytics/analytics.py`):
```python
class Events:
    YOUR_FEATURE_CREATED = 'your_feature_created'
    YOUR_FEATURE_ACTION = 'your_feature_action'
```

**2. Backend Tracking** (views, signals):
```python
from bigbongo.analytics import Analytics, Events

# After successful operation
Analytics.track(
    Events.YOUR_FEATURE_CREATED,
    user=request.user,
    properties={
        'feature_id': feature.id,
        'metadata_only': True  # NEVER track user input/content
    }
)
```

**3. Frontend Tracking** (templates):
```html
<!-- For navigation links -->
<a href="/your-page/"
   onclick="if(typeof posthog !== 'undefined') posthog.capture('nav_clicked', {destination: 'your_page', location: 'main_nav'});">
  Your Page
</a>

<!-- For buttons/actions -->
<button onclick="posthog.capture('feature_action', {action: 'clicked', feature: 'export'})">
  Export
</button>
```

**4. Test Tracking**:
```python
@override_settings(ANALYTICS_IN_DEV=True, POSTHOG_API_KEY='test_key')
@patch('your_module.Analytics.track')
def test_your_feature_tracked(self, mock_track):
    # Verify tracking called
```

## What NOT to Track

- High-frequency operations (status checks, polling >1/second)
- User input/content (PII, prompts, code)
- Secrets (API keys, passwords, tokens)

## Code Review Checklist

Before merging any PR with new features:
- [ ] Event constants added to Events class?
- [ ] Backend tracking added with try/except?
- [ ] Frontend tracking added for key actions?
- [ ] Navigation links include `nav_clicked` tracking? (if adding new nav items)
- [ ] Tests verify tracking?
- [ ] No sensitive data in properties?
- [ ] Logging added (logger.info)?
