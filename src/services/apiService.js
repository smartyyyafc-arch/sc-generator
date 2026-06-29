import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

// Timeout configuration (in milliseconds)
const TIMEOUT_CONFIG = {
  default: 10000,      // 10 seconds for standard requests
  upload: 30000,       // 30 seconds for file uploads
  generate: 60000,     // 60 seconds for payload generation
  download: 45000,     // 45 seconds for downloads
};

// Retry configuration with exponential backoff
const RETRY_CONFIG = {
  maxRetries: 3,                    // Maximum number of retry attempts
  initialDelayMs: 1000,             // Initial delay: 1 second
  maxDelayMs: 10000,                // Maximum delay: 10 seconds
  backoffMultiplier: 2,             // Exponential backoff multiplier
  jitterFactor: 0.1,                // Add 10% jitter to prevent thundering herd
};

// HTTP status codes that should trigger a retry
const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504];

// Error codes that should trigger a retry
const RETRYABLE_ERROR_CODES = [
  'ECONNABORTED',     // Connection timeout
  'ENOTFOUND',        // DNS resolution failed
  'ECONNREFUSED',     // Connection refused
  'ENETUNREACH',      // Network unreachable
  'ETIMEDOUT',        // Connection timeout
];

/**
 * Calculate delay with exponential backoff and jitter
 * @param {number} retryCount - Current retry attempt (0-indexed)
 * @returns {number} Delay in milliseconds
 */
const calculateBackoffDelay = (retryCount) => {
  const exponentialDelay = Math.min(
    RETRY_CONFIG.initialDelayMs * Math.pow(RETRY_CONFIG.backoffMultiplier, retryCount),
    RETRY_CONFIG.maxDelayMs
  );

  // Add jitter: randomize delay by ±jitterFactor%
  const jitter = exponentialDelay * RETRY_CONFIG.jitterFactor * (Math.random() * 2 - 1);
  return Math.max(exponentialDelay + jitter, 100); // Minimum 100ms delay
};

/**
 * Check if error is retryable
 * @param {Error} error - The error to check
 * @returns {boolean} Whether the error should trigger a retry
 */
const isRetryableError = (error) => {
  // Check if error code is retryable
  if (error.code && RETRYABLE_ERROR_CODES.includes(error.code)) {
    return true;
  }

  // Check if HTTP status code is retryable
  if (error.response && RETRYABLE_STATUS_CODES.includes(error.response.status)) {
    return true;
  }

  // Timeout errors are retryable
  if (error.code === 'ECONNABORTED') {
    return true;
  }

  // Network errors without response are retryable
  if (error.message === 'Network Error' && !error.response) {
    return true;
  }

  return false;
};

/**
 * Sleep for specified milliseconds
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Create axios instances with different timeout configurations
const createAxiosInstance = (timeout = TIMEOUT_CONFIG.default) => {
  return axios.create({
    baseURL: API_BASE,
    timeout: timeout,
    headers: {
      'Content-Type': 'application/json',
    },
    // Retry logic for network errors
    validateStatus: (status) => {
      // Only resolve if status is less than 500, so we can handle 4xx errors gracefully
      return status < 500;
    },
  });
};

// Default axios instance
const axiosInstance = createAxiosInstance(TIMEOUT_CONFIG.default);

// Helper function to handle API errors consistently
const handleApiError = (error) => {
  // Network timeout errors
  if (error.code === 'ECONNABORTED') {
    return {
      error: 'Request timeout. The server took too long to respond. Please try again.',
      statusCode: 408,
      isTimeout: true,
    };
  }

  // Network connection errors
  if (error.message === 'Network Error' || !error.response) {
    return {
      error: `Network error. Cannot reach the server at ${API_BASE}`,
      statusCode: 0,
      isNetworkError: true,
    };
  }

  // HTTP error responses
  if (error.response) {
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return {
          error: data?.error || 'Bad request. Please check your input.',
          statusCode: 400,
        };
      case 404:
        return {
          error: 'API endpoint not found. Please check the server configuration.',
          statusCode: 404,
        };
      case 408:
        return {
          error: 'Request timeout. The server did not respond in time.',
          statusCode: 408,
          isTimeout: true,
        };
      case 413:
        return {
          error: 'File too large. Please upload a smaller file.',
          statusCode: 413,
        };
      case 429:
        return {
          error: 'Too many requests. Please wait before trying again.',
          statusCode: 429,
        };
      case 500:
        return {
          error: 'Server error. Please try again later.',
          statusCode: 500,
        };
      case 503:
        return {
          error: 'Backend service unavailable. Please check if the server is running.',
          statusCode: 503,
        };
      default:
        return {
          error: data?.error || `Server error (${status}). Please try again.`,
          statusCode: status,
        };
    }
  }

  // Unknown errors
  return {
    error: error.message || 'An unexpected error occurred',
    statusCode: -1,
  };
};

/**
 * Execute HTTP request with exponential backoff retry logic
 * @param {Function} requestFn - Async function that performs the actual request
 * @param {string} operationName - Name of the operation for logging
 * @param {AbortSignal} signal - Abort signal for cancellation
 * @returns {Promise<any>} Response from the API
 */
const executeWithRetry = async (requestFn, operationName, signal) => {
  let lastError;

  for (let retryCount = 0; retryCount <= RETRY_CONFIG.maxRetries; retryCount++) {
    try {
      // Check if the request has been aborted
      if (signal?.aborted) {
        throw new Error('Request was cancelled');
      }

      // Execute the request
      const response = await requestFn();

      // If successful, return immediately
      if (response.status < 500) {
        return response;
      }

      // For 5xx errors, check if we should retry
      lastError = response;
      if (retryCount < RETRY_CONFIG.maxRetries) {
        const delayMs = calculateBackoffDelay(retryCount);
        console.warn(
          `${operationName}: Server error (${response.status}). Retrying in ${Math.round(delayMs)}ms... (attempt ${retryCount + 1}/${RETRY_CONFIG.maxRetries})`
        );
        await sleep(delayMs);
        continue;
      }

      return response;
    } catch (error) {
      lastError = error;

      // Don't retry if request was cancelled
      if (signal?.aborted || error.message === 'Request was cancelled') {
        throw error;
      }

      // Check if error is retryable
      if (!isRetryableError(error)) {
        // Non-retryable error, throw immediately
        throw error;
      }

      // If we've exhausted retries, throw the error
      if (retryCount >= RETRY_CONFIG.maxRetries) {
        console.error(
          `${operationName}: Failed after ${RETRY_CONFIG.maxRetries} retries. Last error:`,
          error.message
        );
        throw error;
      }

      // Calculate backoff delay and retry
      const delayMs = calculateBackoffDelay(retryCount);
      console.warn(
        `${operationName}: ${error.message}. Retrying in ${Math.round(delayMs)}ms... (attempt ${retryCount + 1}/${RETRY_CONFIG.maxRetries})`
      );
      await sleep(delayMs);
    }
  }

  // Should not reach here, but if we do, throw the last error
  throw lastError;
};

// API Service Methods
const apiService = {
  // Techniques
  fetchTechniques: async (signal) => {
    try {
      const response = await executeWithRetry(
        () => axiosInstance.get('/techniques', { signal }),
        'fetchTechniques',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data.techniques || [],
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // Fingerprints
  fetchFingerprints: async (signal) => {
    try {
      const response = await executeWithRetry(
        () => axiosInstance.get('/fingerprints', { signal }),
        'fetchFingerprints',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data.fingerprints || [],
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  createFingerprint: async (name, config, signal) => {
    try {
      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.default).post(
          '/fingerprints',
          { name, config },
          { signal }
        ),
        'createFingerprint',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // Proxies
  fetchProxies: async (signal) => {
    try {
      const response = await executeWithRetry(
        () => axiosInstance.get('/proxies', { signal }),
        'fetchProxies',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data.proxies || [],
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  addProxy: async (url, type, signal) => {
    try {
      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.default).post(
          '/proxies',
          { url, type },
          { signal }
        ),
        'addProxy',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // File Upload
  uploadFile: async (file, signal) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.upload).post(
          '/upload',
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
            signal,
          }
        ),
        'uploadFile',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // Payload Generation
  generatePayload: async (payload, signal) => {
    try {
      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.generate).post(
          '/generate-payload',
          payload,
          { signal }
        ),
        'generatePayload',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // One-Click Styles
  fetchOneClickStyles: async (signal) => {
    try {
      const response = await executeWithRetry(
        () => axiosInstance.get('/one-click-styles', { signal }),
        'fetchOneClickStyles',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data.styles || {},
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // One-Click Generation
  generateOneClick: async (payload, signal) => {
    try {
      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.generate).post(
          '/generate-one-click',
          payload,
          { signal }
        ),
        'generateOneClick',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // Persistence Methods
  fetchPersistenceMethods: async (signal) => {
    try {
      const response = await executeWithRetry(
        () => axiosInstance.get('/persistence-methods', { signal }),
        'fetchPersistenceMethods',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data.methods || {},
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // Persistent Payload Generation
  generatePersistent: async (payload, signal) => {
    try {
      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.generate).post(
          '/generate-persistent',
          payload,
          { signal }
        ),
        'generatePersistent',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },

  // Download
  downloadFile: async (outputId, signal) => {
    try {
      const response = await executeWithRetry(
        () => createAxiosInstance(TIMEOUT_CONFIG.download).get(
          `/download/${outputId}`,
          {
            responseType: 'blob',
            signal,
          }
        ),
        'downloadFile',
        signal
      );

      if (response.status >= 400) {
        throw response;
      }
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        error: handleApiError(error),
        success: false,
      };
    }
  },
};

export default apiService;
export { TIMEOUT_CONFIG, RETRY_CONFIG };
