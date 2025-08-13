# Password Reset Rate Limiting

## Overview
The password reset system now includes comprehensive rate limiting to prevent abuse while maintaining accessibility for legitimate users.

## Rate Limiting Layers

### 1. IP-Based Rate Limiting (Global)
- **Rate**: 5 password reset requests per hour per IP address
- **Scope**: All password reset requests from the same IP
- **Implementation**: `PasswordResetThrottle` class
- **Cache Key**: Based on IP address (handles proxies via X-Forwarded-For)

### 2. Email-Based Cooldown (Per User)
- **Rate**: 1 reset request per 15 minutes per email address
- **Scope**: Same email address
- **Implementation**: Database check for recent reset codes
- **Response**: 429 Too Many Requests with remaining wait time

### 3. User-Based Hourly Limit (Per User)
- **Rate**: Maximum 3 reset requests per hour per user account
- **Scope**: Same user account (by email)
- **Implementation**: Database count of recent reset codes
- **Response**: 429 Too Many Requests with hourly limit message

## Configuration

### Settings
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'password_reset': '5/hour',  # 5 requests per hour per IP
    }
}
```

### View Configuration
```python
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]  # Custom throttle
```

## Rate Limiting Flow

```
1. Request comes in
   ↓
2. IP-based throttle check (5/hour)
   ↓
3. Email cooldown check (15 min)
   ↓
4. User hourly limit check (3/hour)
   ↓
5. Create reset code and send email
```

## Response Codes

### Success (200)
- Reset code sent successfully

### Rate Limited (429)
- **IP limit exceeded**: "Rate limit exceeded"
- **Email cooldown**: "Please wait X minutes"
- **User hourly limit**: "Too many reset requests"

### Other Errors (400, 404, 500)
- Standard validation and system errors

## Security Benefits

1. **Prevents brute force attacks** on email addresses
2. **Reduces email spam** from malicious users
3. **Protects against DoS attacks** on the reset endpoint
4. **Maintains user experience** for legitimate requests
5. **Logs suspicious activity** for monitoring

## Monitoring

The system logs:
- Rate limit violations
- Excessive reset requests per user
- Failed email attempts

## Testing Rate Limits

### Test IP-based limit:
```bash
# Make 6 requests from same IP within 1 hour
# 6th request should return 429
```

### Test email cooldown:
```bash
# Request reset for same email twice within 15 minutes
# 2nd request should return 429 with wait time
```

### Test user hourly limit:
```bash
# Request reset for same email 4 times within 1 hour
# 4th request should return 429 with hourly limit message
```

## Customization

You can adjust the limits by modifying:
- `settings.py` throttle rates
- `throttling.py` throttle class
- View logic for email cooldown and user limits
