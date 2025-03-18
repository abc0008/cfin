/**
 * Standard API error class that maps to backend error response structure
 */
export interface ValidationErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export type ErrorDetail = string | ValidationErrorDetail[] | Record<string, any>;

export interface ApiErrorOptions {
  statusCode: number;
  detail: ErrorDetail;
  errorType?: string;
  originalError?: unknown;
}

export class ApiError extends Error {
  statusCode: number;
  detail: ErrorDetail;
  errorType: string;
  originalError?: unknown;

  constructor(options: ApiErrorOptions) {
    // Create a human-readable message from the error detail
    const message = ApiError.formatErrorMessage(options.detail);
    super(message);
    
    this.name = 'ApiError';
    this.statusCode = options.statusCode;
    this.detail = options.detail;
    this.errorType = options.errorType || ApiError.getDefaultErrorType(options.statusCode);
    this.originalError = options.originalError;
    
    // Preserve the stack trace in modern JS engines
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  /**
   * Format error details into a human-readable string
   */
  private static formatErrorMessage(detail: ErrorDetail): string {
    if (typeof detail === 'string') {
      return detail;
    } else if (Array.isArray(detail)) {
      // Handle validation error details
      return detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
    } else {
      return JSON.stringify(detail);
    }
  }

  /**
   * Get a default error type based on HTTP status code
   */
  private static getDefaultErrorType(statusCode: number): string {
    const errorTypes: Record<number, string> = {
      400: 'bad_request',
      401: 'unauthorized',
      403: 'forbidden',
      404: 'not_found',
      409: 'conflict',
      422: 'validation_error',
      429: 'too_many_requests',
      500: 'server_error',
      503: 'service_unavailable'
    };
    
    return errorTypes[statusCode] || 'unknown_error';
  }

  /**
   * Check if this error is of a specific type
   */
  isType(errorType: string): boolean {
    return this.errorType === errorType;
  }

  /**
   * Check if this error is a validation error
   */
  isValidationError(): boolean {
    return this.isType('validation_error') || this.statusCode === 422;
  }

  /**
   * Check if this error is a "not found" error
   */
  isNotFoundError(): boolean {
    return this.isType('not_found') || this.statusCode === 404;
  }
  
  /**
   * Get validation errors as a simple object map for form handling
   * Returns an object with field paths as keys and error messages as values
   */
  getValidationErrorsMap(): Record<string, string> {
    if (!this.isValidationError() || !Array.isArray(this.detail)) {
      return {};
    }
    
    return (this.detail as ValidationErrorDetail[]).reduce((acc, error) => {
      // Create a field name from the location path
      const fieldName = error.loc.join('.');
      acc[fieldName] = error.msg;
      return acc;
    }, {} as Record<string, string>);
  }
}
