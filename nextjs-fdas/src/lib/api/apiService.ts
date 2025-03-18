import { z } from 'zod';
import { ApiError, ErrorDetail } from '../errors/ApiError';

// API base URL - would be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Configuration for retries
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 1000;

/**
 * Validates data against a schema and returns the validated data
 */
export function validate<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    const errorMessage = result.error.errors.map(
      (err) => `${err.path.join('.')}: ${err.message}`
    ).join(', ');
    throw new Error(`Validation error: ${errorMessage}`);
  }
  return result.data;
}

/**
 * API Service class providing standardized methods for API interactions
 * with error handling, validation, and retry functionality
 */
class ApiService {
  /**
   * Send a request to the API with validation
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData,
    schema?: z.ZodType<T>,
    retryOptions?: {
      maxAttempts?: number;
      retryDelay?: number;
    }
  ): Promise<T> {
    // Configuration
    const maxAttempts = retryOptions?.maxAttempts || MAX_RETRY_ATTEMPTS;
    const retryDelay = retryOptions?.retryDelay || RETRY_DELAY_MS;
    
    // Ensure endpoint starts with /
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Ensure URL doesn't have duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}${endpoint}`;
      
    console.log(`Sending ${method} request to ${finalUrl}`);
    
    // Create request options
    const options: RequestInit = {
      method,
      headers: {
        'Accept': 'application/json'
      }
    };
    
    // Add request body if provided
    if (data) {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json'
      };
      options.body = JSON.stringify(data);
    }
    
    // Add form data if provided
    if (formData) {
      // Remove Content-Type header to let the browser set it with the boundary
      if (options.headers && typeof options.headers === 'object') {
        const headers = options.headers as Record<string, string>;
        delete headers['Content-Type'];
      }
      options.body = formData;
    }
    
    // Implementation of retry logic
    let lastError: any;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await fetch(finalUrl, options);
        
        // Handle non-OK responses
        if (!response.ok) {
          // Try to parse error response as our standard format
          try {
            const errorData = await response.json();
            
            // Check if the response matches our standard error format
            if (errorData.status_code !== undefined && errorData.detail !== undefined) {
              throw new ApiError({
                statusCode: errorData.status_code,
                detail: errorData.detail,
                errorType: errorData.error_type,
                originalError: new Error(`API error: ${response.status} ${response.statusText}`)
              });
            } 
            // Fallback for older API endpoints not yet updated
            else if (errorData.detail) {
              let detail: ErrorDetail = errorData.detail;
              throw new ApiError({
                statusCode: response.status,
                detail,
                originalError: new Error(`API error: ${response.status} ${response.statusText}`)
              });
            } else {
              // Generic JSON error without our expected structure
              throw new ApiError({
                statusCode: response.status,
                detail: JSON.stringify(errorData),
                originalError: new Error(`API error: ${response.status} ${response.statusText}`)
              });
            }
          } catch (e) {
            // If error is already an ApiError, just rethrow it
            if (e instanceof ApiError) {
              throw e;
            }
            
            // If JSON parsing failed, try to get plain text
            try {
              const errorText = await response.text();
              throw new ApiError({
                statusCode: response.status,
                detail: errorText || `API error: ${response.status} ${response.statusText}`,
                originalError: e
              });
            } catch (textError) {
              // If all else fails, create a generic API error
              throw new ApiError({
                statusCode: response.status,
                detail: `API error: ${response.status} ${response.statusText}`,
                originalError: textError
              });
            }
          }
        }
        
        // Parse the response
        const responseData = await response.json();
        
        // Validate the response if a schema is provided
        if (schema) {
          return validate(schema, responseData);
        }
        
        return responseData as T;
        
      } catch (error) {
        console.error(`API request error (attempt ${attempt}/${maxAttempts}):`, error);
        lastError = error;
        
        // If we have more attempts and this isn't a client error (4xx), retry
        // Don't retry client errors like 400, 404, etc.
        const isClientError = error instanceof ApiError && error.statusCode >= 400 && error.statusCode < 500;
        
        if (attempt < maxAttempts && !isClientError) {
          const delay = retryDelay * Math.pow(2, attempt - 1);
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        } else {
          // No more retries or client error, throw the last error
          throw lastError;
        }
      }
    }
    
    // If we've exhausted all retry attempts, throw the last error
    console.error('All retry attempts failed');
    throw lastError;
  }
  
  /**
   * Performs a GET request to the API
   */
  async get<T>(endpoint: string, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'GET', undefined, undefined, schema, retryOptions);
  }
  
  /**
   * Performs a POST request to the API
   */
  async post<T>(endpoint: string, data?: any, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'POST', data, undefined, schema, retryOptions);
  }
  
  /**
   * Performs a POST request with multipart/form-data to the API
   */
  async postFormData<T>(endpoint: string, formData: FormData, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'POST', undefined, formData, schema, retryOptions);
  }
  
  /**
   * Performs a PUT request to the API
   */
  async put<T>(endpoint: string, data?: any, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'PUT', data, undefined, schema, retryOptions);
  }
  
  /**
   * Performs a DELETE request to the API
   */
  async delete<T>(endpoint: string, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'DELETE', undefined, undefined, schema, retryOptions);
  }
  
  /**
   * Uploads a file to the API with progress tracking
   */
  async uploadWithProgress<T>(
    endpoint: string, 
    formData: FormData,
    onProgress?: (progress: number) => void,
    schema?: z.ZodType<T>
  ): Promise<T> {
    // Ensure endpoint starts with /
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Ensure URL doesn't have duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}${endpoint}`;
      
    console.log(`Uploading file to ${finalUrl}`);
    
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // Set up progress tracking
      if (onProgress) {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            onProgress(progress);
          }
        };
      }
      
      xhr.open('POST', finalUrl);
      
      xhr.onload = async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            
            // Validate the response if a schema is provided
            if (schema) {
              try {
                const validatedData = validate(schema, response);
                resolve(validatedData);
              } catch (validationError) {
                reject(validationError);
              }
            } else {
              resolve(response as T);
            }
          } catch (parseError) {
            reject(new Error('Failed to parse response as JSON'));
          }
        } else {
          let errorMessage = `Upload failed with status ${xhr.status}`;
          
          try {
            const errorData = JSON.parse(xhr.responseText);
            if (errorData.detail) {
              errorMessage = errorData.detail;
            } else {
              errorMessage = JSON.stringify(errorData);
            }
          } catch (e) {
            // If the response isn't JSON, use the response text
            if (xhr.responseText) {
              errorMessage = xhr.responseText;
            }
          }
          
          reject(new Error(errorMessage));
        }
      };
      
      xhr.onerror = () => {
        reject(new Error('Network error during upload'));
      };
      
      xhr.onabort = () => {
        reject(new Error('Upload was aborted'));
      };
      
      xhr.send(formData);
    });
  }
  
  /**
   * Performs a streaming request to the API and processes the chunks
   * This is especially useful for LLM-generated content that comes as a stream
   */
  async stream<T>(
    endpoint: string, 
    data: any, 
    onChunk: (chunk: any) => void, 
    onComplete: (fullResponse: T) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    // Ensure endpoint starts with /
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Ensure URL doesn't have duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(finalUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        let errorMessage = `API error: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          }
        } catch (e) {
          // If we can't parse JSON, try to get text
          try {
            const errorText = await response.text();
            if (errorText) errorMessage = errorText;
          } catch (textError) {
            // Keep original error message
          }
        }
        throw new Error(errorMessage);
      }
      
      // Check if the response is actually a stream
      if (response.headers.get('content-type')?.includes('event-stream')) {
        // Handle server-sent events
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullResponseText = '';
        
        if (!reader) {
          throw new Error('Stream reader could not be created');
        }
        
        let done = false;
        
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          
          if (done) break;
          
          // Convert the chunk to text
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          fullResponseText += chunk;
          
          // Process any complete events in the buffer
          let eventEnd = buffer.indexOf('\n\n');
          while (eventEnd >= 0) {
            const event = buffer.substring(0, eventEnd);
            buffer = buffer.substring(eventEnd + 2);
            
            // Process the event (typically 'data: {...}')
            if (event.startsWith('data:')) {
              const data = event.substring(5).trim();
              try {
                // Try to parse as JSON
                const parsedData = JSON.parse(data);
                onChunk(parsedData);
              } catch (e) {
                // If not valid JSON, just pass the raw data
                onChunk(data);
              }
            }
            
            eventEnd = buffer.indexOf('\n\n');
          }
        }
        
        // Attempt to parse the full response as JSON
        try {
          const fullResponse = JSON.parse(fullResponseText);
          onComplete(fullResponse as T);
        } catch (e) {
          console.warn('Could not parse full response as JSON:', e);
          onComplete(fullResponseText as unknown as T);
        }
      } else {
        // If not a stream, handle as regular JSON response
        const data = await response.json();
        onComplete(data as T);
      }
    } catch (error) {
      console.error('Stream request error:', error);
      onError(error instanceof Error ? error : new Error(String(error)));
    }
  }
  
  /**
   * Polls an endpoint until a condition is met or max attempts are reached
   * Useful for checking the status of long-running operations
   */
  async poll<T>(
    endpoint: string,
    checkCondition: (data: T) => boolean,
    options: {
      interval?: number,
      maxAttempts?: number,
      initialDelay?: number
    } = {}
  ): Promise<T> {
    const {
      interval = 2000,
      maxAttempts = 30,
      initialDelay = 0
    } = options;
    
    // Wait for initial delay if specified
    if (initialDelay > 0) {
      await new Promise(resolve => setTimeout(resolve, initialDelay));
    }
    
    // Start polling
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const data = await this.get<T>(endpoint);
      
      if (checkCondition(data)) {
        return data;
      }
      
      // Wait before the next attempt
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }
    
    throw new Error(`Polling timed out after ${maxAttempts} attempts`);
  }
}

// Create a singleton instance of the ApiService
export const apiService = new ApiService();

// In development, expose the API service to the window object for debugging
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  (window as any).__apiService = apiService;
  
  console.log(
    '%c🌐 API Service Available',
    'background: #edf8ff; color: #0066cc; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 4px;'
  );
  console.log('Use __apiService to access the API directly in the console');
}
