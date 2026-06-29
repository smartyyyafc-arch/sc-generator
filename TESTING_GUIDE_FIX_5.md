# Testing Guide for React Fix #5: API Service Timeout Configuration

## Overview
This guide provides comprehensive testing scenarios for the new timeout-configured API service.

## Test Environment Setup

1. Ensure the backend server is running on `http://localhost:5000`
2. Start the React development server
3. Open browser DevTools (F12) to monitor network requests

## Unit Test Scenarios

### 1. Normal Operation - All Requests Complete Successfully

**Test**: App initialization and data loading
```
Steps:
1. Open application
2. Monitor Network tab in DevTools
3. Verify these requests complete within expected timeouts:
   - GET /api/techniques (expect < 10s)
   - GET /api/fingerprints (expect < 10s)
   - GET /api/proxies (expect < 10s)

Expected Result:
- All techniques, fingerprints, and proxies load
- No error alerts displayed
- UI fully functional
```

### 2. Timeout Error - Backend Delay

**Test**: Simulate slow backend response
```
Setup:
- In browser DevTools, use Network throttling
- Set to "Slow 3G" or add 20-30 second delay

Steps:
1. Refresh the page
2. Observe network requests
3. Wait for timeout to occur

Expected Result:
- Request aborts after timeout period
- Error message: "Request timeout. The server took too long to respond."
- Error displayed with warning icon
- User can retry or continue with other operations
- No console errors (just warnings)
```

### 3. Network Error - Server Unreachable

**Test**: Backend server down
```
Setup:
- Stop the backend server
- Keep React dev server running

Steps:
1. Refresh the page
2. Wait for requests to fail
3. Observe error messages

Expected Result:
- Network error: "Network error. Cannot reach the server at http://localhost:5000"
- Error displayed prominently
- App shows graceful degradation
- No hanging requests
```

### 4. File Upload - 30 Second Timeout

**Test**: Large file upload
```
Steps:
1. Create a test file (5-10 MB)
2. Click "Upload" button
3. Monitor Network tab
4. Observe upload progress

Expected Result:
- Upload uses 30-second timeout
- Progress indicated with loading spinner
- Success message on completion
- File ID and name displayed
```

### 5. Payload Generation - 60 Second Timeout

**Test**: Complex payload generation
```
Steps:
1. Upload a file first
2. Select technique and options
3. Click "Generate Payload"
4. Monitor Network tab

Expected Result:
- Generation uses 60-second timeout
- Loading indicator shows "Generating..."
- Button disabled during generation
- Output displayed on completion
- File download available
```

### 6. Download - 45 Second Timeout

**Test**: Download generated payload
```
Steps:
1. Generate a payload (any mode)
2. Click "Download" button
3. Monitor Network tab
4. Check Downloads folder

Expected Result:
- Download uses 45-second timeout
- File downloads successfully
- Proper filename assigned
- No corrupted downloads
```

### 7. One-Click Installer - Complete Flow

**Test**: Generate and download one-click installer
```
Steps:
1. Switch to "One-Click" mode
2. Upload a file
3. Select obfuscation style
4. Click "Generate One-Click Installer"
5. Monitor loading state and errors
6. Download the installer

Expected Result:
- Styles load within 10 seconds
- Generation uses 60-second timeout
- Error display shows any issues
- Download uses 45-second timeout
- All loading states work correctly
```

### 8. Persistent Payload - Complete Flow

**Test**: Generate and download persistent payload
```
Steps:
1. Switch to "Persistent" mode
2. Upload a file
3. Select persistence method, technique, and obfuscation
4. Click "Generate Persistent Payload"
5. Monitor loading state and errors
6. Download the payload

Expected Result:
- Methods load within 10 seconds
- Generation uses 60-second timeout
- Error display shows any issues
- Download uses 45-second timeout
- All loading states work correctly
```

### 9. Error Recovery - Retry Failed Request

**Test**: Recover from timeout/network error
```
Setup:
- Cause a timeout or network error (use throttling or stop server)

Steps:
1. Wait for error to display
2. Stop throttling or restart server
3. Retry the operation (refresh, re-upload, etc.)

Expected Result:
- Retry successfully completes
- No error messages
- Application functions normally
```

### 10. Concurrent Requests - Multiple Operations

**Test**: Multiple simultaneous requests
```
Steps:
1. Upload file
2. While upload is in progress:
   - Try to select different technique
   - Try to generate payload
3. Monitor all requests in Network tab

Expected Result:
- Proper state management
- Loading indicators accurate
- No race conditions
- Proper error handling if one fails
```

### 11. Memory Leak Prevention - Navigation During Request

**Test**: Navigate while request pending
```
Steps:
1. Start a long operation (generate payload)
2. Before it completes, navigate away/refresh
3. Check Console for errors

Expected Result:
- No unhandled promise rejections
- No memory leaks
- Component cleanup occurs properly
- No warnings about setting state on unmounted components
```

### 12. Memory Leak Prevention - Component Unmount

**Test**: Unmount component with pending request
```
Steps:
1. Switch between modes while one is loading
2. Example: Start generation in Standard mode, switch to One-Click before it completes
3. Check Console

Expected Result:
- Previous request is cancelled
- No warnings about unmounted components
- No state updates after unmount
```

## Error Message Scenarios

### Timeout Error
```
Message: "Request timeout. The server took too long to respond. Please try again."
HTTP Code: 408
isTimeout: true
Auto-dismiss: Yes (6 seconds)
```

### Network Error
```
Message: "Network error. Cannot reach the server at http://localhost:5000"
HTTP Code: 0
isNetworkError: true
Auto-dismiss: Yes (6 seconds)
```

### File Too Large
```
Message: "File too large. Please upload a smaller file."
HTTP Code: 413
Auto-dismiss: Yes (6 seconds)
```

### Rate Limited
```
Message: "Too many requests. Please wait before trying again."
HTTP Code: 429
Auto-dismiss: Yes (6 seconds)
```

### Server Error
```
Message: "Server error. Please try again later."
HTTP Code: 500
Auto-dismiss: Yes (6 seconds)
```

### Service Unavailable
```
Message: "Backend service unavailable. Please check if the server is running."
HTTP Code: 503
Auto-dismiss: Yes (6 seconds)
```

### Bad Request
```
Message: "Bad request. Please check your input."
HTTP Code: 400
Auto-dismiss: Yes (6 seconds)
```

## Browser DevTools Verification

### Network Tab Checks
- Verify request timeouts match configured values:
  - `/api/techniques` (10s)
  - `/api/fingerprints` (10s)
  - `/api/proxies` (10s)
  - `/api/upload` (30s)
  - `/api/generate-payload` (60s)
  - `/api/generate-one-click` (60s)
  - `/api/generate-persistent` (60s)
  - `/api/download/*` (45s)

### Console Checks
- No unhandled promise rejections
- No memory leak warnings
- Proper error logging with context
- No repeated error messages for same request

### Performance Checks
- App remains responsive during requests
- UI updates immediately
- No blocking operations
- Smooth loading transitions

## Regression Testing

Verify existing functionality still works:
- [ ] Fingerprint selector works correctly
- [ ] Proxy manager works correctly
- [ ] Recommendation cards display
- [ ] Output display shows payloads correctly
- [ ] Copy to clipboard functionality works
- [ ] All UI interactions responsive
- [ ] Modal/dialog functionality intact
- [ ] Form validation working

## Load Testing

### Test with Multiple Users
```
Steps:
1. Open multiple browser tabs with the app
2. Perform operations in each tab simultaneously
3. Monitor for race conditions or state corruption

Expected Result:
- Each tab operates independently
- No cross-tab interference
- Proper error isolation
```

### Test with Slow Network
```
Setup:
- Use DevTools Network throttling
- Set to "Slow 3G"

Steps:
1. Perform all operations
2. Monitor timeout behavior
3. Verify loading states

Expected Result:
- Timeouts honored
- Proper error messages
- No hanging requests
```

## Documentation Verification

Verify the following are documented:
- [ ] Timeout configuration in apiService.js comments
- [ ] Error handling strategy documented
- [ ] Component error display documented
- [ ] Memory leak prevention documented
- [ ] Abort controller usage documented

## Sign-Off Checklist

- [ ] All timeout values appropriate for operations
- [ ] Error messages clear and actionable
- [ ] Loading states work correctly
- [ ] No memory leaks detected
- [ ] No unhandled errors
- [ ] Responsive behavior maintained
- [ ] User feedback clear
- [ ] All components properly update state
- [ ] No console warnings or errors
- [ ] Regression tests pass
