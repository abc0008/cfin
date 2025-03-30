import { z } from 'zod';

/**
 * Validates data against a Zod schema and returns the validated data or throws an error
 */
export function validate<T>(schema: z.ZodType<T>, data: unknown): T {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      // Format errors nicely for debugging
      const formattedErrors = error.errors.map(err => {
        return `${err.path.join('.')}: ${err.message}`;
      }).join('\n');
      
      console.error('Validation error:', formattedErrors);
      
      // Throw a more user-friendly error
      throw new Error(`Invalid data received from API: ${formattedErrors}`);
    }
    throw error;
  }
}

/**
 * Safe parse: validates data against a Zod schema and returns the result without throwing
 * Returns { success: true, data: T } or { success: false, error: string }
 */
export function safeParse<T>(schema: z.ZodType<T>, data: unknown): { success: boolean; data?: T; error?: string } {
  try {
    const result = schema.safeParse(data);
    if (result.success) {
      return { success: true, data: result.data };
    } else {
      const formattedErrors = result.error.errors.map(err => {
        return `${err.path.join('.')}: ${err.message}`;
      }).join('\n');
      
      return { success: false, error: formattedErrors };
    }
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown validation error' 
    };
  }
}