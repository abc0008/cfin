/**
 * Tests for API error handling consistency in the frontend
 */
import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest';
import { ApiError } from '../../lib/errors/ApiError';
import { apiService } from '../../lib/api/apiService';

// Mock fetch
global.fetch = vi.fn();

describe('API Error Handling', () => {
  const mockFetch = global.fetch as jest.Mock;
  
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test('should handle standardized error response format', async () => {
    // Mock standardized error response
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({
        status_code: 404,
        detail: 'Document not found',
        error_type: 'not_found'
      })
    });

    try {
      await apiService.get('/document/123');
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(404);
      expect(apiError.detail).toBe('Document not found');
      expect(apiError.errorType).toBe('not_found');
      expect(apiError.isNotFoundError()).toBe(true);
    }
  });

  test('should handle validation error responses', async () => {
    // Mock validation error response
    const validationErrors = [
      {
        loc: ['body', 'name'],
        msg: 'field required',
        type: 'value_error.missing'
      },
      {
        loc: ['body', 'email'],
        msg: 'invalid email format',
        type: 'value_error.email'
      }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: () => Promise.resolve({
        status_code: 422,
        detail: validationErrors,
        error_type: 'validation_error'
      })
    });

    try {
      await apiService.post('/users', {});
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(422);
      expect(apiError.detail).toEqual(validationErrors);
      expect(apiError.errorType).toBe('validation_error');
      expect(apiError.isValidationError()).toBe(true);
      
      // Test error map functionality
      const errorMap = apiError.getValidationErrorsMap();
      expect(errorMap['body.name']).toBe('field required');
      expect(errorMap['body.email']).toBe('invalid email format');
    }
  });

  test('should handle older error format for backward compatibility', async () => {
    // Mock older error format
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: () => Promise.resolve({
        detail: 'Invalid request parameters'
      })
    });

    try {
      await apiService.get('/documents');
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(400);
      expect(apiError.detail).toBe('Invalid request parameters');
      expect(apiError.errorType).toBe('bad_request');
    }
  });

  test('should handle non-JSON error responses', async () => {
    // Mock non-JSON error response
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.reject(new Error('Invalid JSON')),
      text: () => Promise.resolve('Internal server error occurred')
    });

    try {
      await apiService.get('/analytics');
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(500);
      expect(apiError.detail).toBe('Internal server error occurred');
      expect(apiError.errorType).toBe('server_error');
    }
  });

  test('should not retry client errors', async () => {
    // Setup mocks to track retries
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({
        status_code: 404,
        detail: 'Resource not found',
        error_type: 'not_found'
      })
    });

    const consoleSpy = vi.spyOn(console, 'log');
    
    try {
      await apiService.get('/users/999', undefined, { maxAttempts: 3 });
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Should not retry
      expect(consoleSpy).not.toHaveBeenCalledWith(expect.stringMatching(/Retrying in/));
    }
  });

  test('should retry server errors', async () => {
    // Setup mocks to track retries - first call fails, second succeeds
    mockFetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({
          status_code: 500,
          detail: 'Server temporarily unavailable',
          error_type: 'server_error'
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 1, name: 'Test' })
      });

    const consoleSpy = vi.spyOn(console, 'log');
    
    const result = await apiService.get('/users/1', undefined, { 
      maxAttempts: 2,
      retryDelay: 10 // Small delay for tests
    });
    
    expect(result).toEqual({ id: 1, name: 'Test' });
    expect(mockFetch).toHaveBeenCalledTimes(2); // Should retry once
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringMatching(/Retrying in/));
  });
});
