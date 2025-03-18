import { z } from 'zod';

/**
 * Validate a request object against a Zod schema
 * This is useful for validating data before sending to API endpoints
 */
export function validateRequest<T>(schema: z.ZodType<T>, data: unknown): T {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      // Format error message for better debugging
      const formattedError = error.errors.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ).join(', ');
      console.error(`Validation error: ${formattedError}`);
      throw new Error(`Request validation failed: ${formattedError}`);
    }
    throw error;
  }
}

/**
 * Safe parse: validates data against a Zod schema and returns the result without throwing
 */
export function safeValidateRequest<T>(schema: z.ZodType<T>, data: unknown): { 
  success: boolean; 
  data?: T; 
  error?: string 
} {
  try {
    const result = schema.safeParse(data);
    if (result.success) {
      return { success: true, data: result.data };
    } else {
      // Format error message for better debugging
      const formattedError = result.error.errors.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ).join(', ');
      console.error(`Validation error: ${formattedError}`);
      return { success: false, error: formattedError };
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return { success: false, error: errorMessage };
  }
}
