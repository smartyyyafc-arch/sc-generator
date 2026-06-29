# React Frontend Fix #5: API Service Timeout Configuration

## Problem
The API service lacked proper request timeout configuration, leading to:
- Requests hanging indefinitely
- No user feedback on timeout events
- Inconsistent error handling across components
- Manual timeout workarounds with setTimeout/clearTimeout
- Memory leaks from incomplete request cleanup
- Poor user experience when server is slow or unreachable

## Solution Implemented

### 1. Centralized API Service (`src/services/apiService.js`)
Created a dedicated API service with:
- **Timeout Configuration**: Different timeouts for different request types
  - Default: 10 seconds for standard requests
  - Upload: 30 seconds for file uploads
  - Generate: 60 seconds for payload generation
  - Download: 45 seconds for downloads

- **Consistent Error Handling**: Unified error response format
  - Timeout errors (ECONNABORTED)
  - Network connection errors
  - HTTP status code handling (400, 404, 408, 413, 429, 500, 503)
  - Unknown error fallback

- **Retry-Friendly Architecture**: Status code validation
  - Only resolves for status < 500
  - Allows graceful handling of 4xx errors

### 2. Updated App.jsx
- Removed direct axios imports and API_BASE constant
- Integrated apiService for all API calls
- Updated all fetch functions with proper error handling
- Removed manual setTimeout/clearTimeout timeouts
- Consistent abort controller usage via ref
- Loading states work correctly with timeout detection

Functions updated:
- `fetchTechniques()` - 10s timeout
- `fetchFingerprints()` - 10s timeout
- `fetchProxies()` - 10s timeout
- `handleFileUpload()` - 30s timeout
- `handleGeneratePayload()` - 60s timeout
- `handleAddProxy()` - 10s timeout
- `handleCreateFingerprint()` - 10s timeout

### 3. Updated OneClickInstaller.jsx
- Removed direct axios imports
- Integrated apiService for all API calls
- Added abort controller ref for proper cleanup
- Added error state management
- Updated functions:
  - `fetchStyles()` - 10s timeout
  - `handleGenerate()` - 60s timeout
  - `handleDownload()` - 45s timeout
- Added error display UI with proper styling
- Proper cleanup on component unmount

### 4. Updated PersistencePayload.jsx
- Removed direct axios imports
- Integrated apiService for all API calls
- Added abort controller ref for proper cleanup
- Added error state management
- Updated functions:
  - `fetchMethods()` - 10s timeout
  - `handleGenerate()` - 60s timeout
  - `handleDownload()` - 45s timeout
- Added error display UI with proper styling
- Proper cleanup on component unmount

## Key Features

### Error Handling
- Complete error coverage with specific messages
- Timeout errors identified separately (isTimeout flag)
- Network errors distinguished from server errors
- HTTP status codes handled appropriately

### Loading States
- Proper loading state management in all components
- Visual feedback during requests
- Disabled buttons during operations
- Auto-dismiss error alerts after 6 seconds in App.jsx

### User Feedback
- Clear error messages for each error type
- Error display in components (OneClickInstaller, PersistencePayload)
- Error auto-dismiss in App.jsx
- Different error types (error, warning, info)

### Memory Leak Prevention
- Abort controllers stored in refs
- Cleanup functions in useEffect
- Component unmount handlers
- Request cancellation on navigation/unmount
- Proper cleanup of axios instances

### Responsive Behavior
- Different timeouts for different operations
- Non-blocking UI updates
- Graceful degradation for optional features
- Async/await error handling

## Timeout Configuration Details

```javascript
const TIMEOUT_CONFIG = {
  default: 10000,      // 10s for standard requests
  upload: 30000,       // 30s for file uploads
  generate: 60000,     // 60s for payload generation
  download: 45000,     // 45s for downloads
};
```

## Error Response Format

All API calls return a consistent format:
```javascript
{
  success: boolean,
  data: any,           // on success
  error: {             // on failure
    error: string,     // error message
    statusCode: number,
    isTimeout?: boolean,
    isNetworkError?: boolean
  }
}
```

## Testing Checklist

- [ ] App loads without errors
- [ ] Techniques load within 10 seconds
- [ ] Fingerprints load (optional feature) within 10 seconds
- [ ] Proxies load (optional feature) within 10 seconds
- [ ] File upload succeeds within 30 seconds
- [ ] Payload generation succeeds within 60 seconds
- [ ] One-click installer generation succeeds within 60 seconds
- [ ] Persistent payload generation succeeds within 60 seconds
- [ ] Download completes within 45 seconds
- [ ] Timeout errors display user-friendly messages
- [ ] Network errors display connectivity messages
- [ ] Error alerts auto-dismiss after 6 seconds (App.jsx)
- [ ] Navigation during request cancels pending operations
- [ ] Component unmount cancels pending operations
- [ ] Multiple simultaneous requests work correctly
- [ ] Loading indicators show during operations
- [ ] Buttons disabled during operations

## Files Modified

1. **Created**: `/src/services/apiService.js` (340 lines)
   - Centralized API service with timeout configuration
   - Consistent error handling
   - All API methods with appropriate timeouts

2. **Modified**: `/src/App.jsx`
   - Import apiService instead of axios
   - Updated all fetch and API call functions
   - Simplified error message extraction

3. **Modified**: `/src/components/OneClickInstaller.jsx`
   - Import apiService instead of axios
   - Added abort controller ref
   - Added error state and display
   - Updated all API calls with proper error handling

4. **Modified**: `/src/components/PersistencePayload.jsx`
   - Import apiService instead of axios
   - Added abort controller ref
   - Added error state and display
   - Updated all API calls with proper error handling

## Benefits

1. **Reliability**: No more hanging requests
2. **Transparency**: Clear timeout and error messages
3. **Maintainability**: Single source of truth for API calls
4. **Performance**: Appropriate timeouts for different operations
5. **User Experience**: Consistent error handling and feedback
6. **Memory Safety**: Proper resource cleanup
7. **Scalability**: Easy to add new API endpoints
8. **Testing**: Easier to mock and test API calls
