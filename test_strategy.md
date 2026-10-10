# Test Strategy for day-ahead-price-alert

## Overview
The day-ahead-price-alert script fetches electricity prices from ENTSO-E API and sends alerts via Telegram when prices fall below a certain threshold.

## Test Scenarios

### 1. Environment Setup Tests
- [ ] Verify all required environment variables are present
- [ ] Confirm API key is properly loaded
- [ ] Validate Telegram credentials are configured

### 2. Functionality Tests
- [ ] Time period calculation accuracy 
- [ ] API request successful with valid data
- [ ] Price parsing and processing works correctly
- [ ] Alert threshold checking functions properly
- [ ] Telegram message sending works (if credentials available)

### 3. Error Handling Tests
- [ ] API connection failures handled gracefully
- [ ] Invalid API responses processed correctly  
- [ ] Timezone calculation errors caught
- [ ] Network timeout handling
- [ ] Missing configuration values

## Testing Approach

### Unit Tests
- Test individual functions like `get_time_period()`
- Test price parsing logic
- Validate timezone operations

### Integration Tests
- Full execution flow testing (with mocked API responses)
- Environment variable validation
- End-to-end script execution

### Manual Testing
- Run script with valid environment setup
- Check for output in console and Telegram
- Verify error messages for missing keys

## Required Tools
- pytest or unittest framework
- Mock objects for API responses
- Environment variable manager
- Logging capabilities

## Expected Output
- Clear console messages during execution
- Error messages when configuration is wrong
- Price data display when successful
- Telegram message sending confirmation