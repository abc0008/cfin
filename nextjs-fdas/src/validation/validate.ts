import { z } from 'zod';

/**
 * Validates data against a schema and returns the validated data or throws an error
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
 * Safe parsing of data against a schema with detailed error info
 */
export function safeParse<T>(schema: z.ZodType<T>, data: unknown): { 
  success: boolean;
  data?: T;
  error?: string;
} {
  const result = schema.safeParse(data);
  if (!result.success) {
    const errorMessage = result.error.errors.map(
      (err) => `${err.path.join('.')}: ${err.message}`
    ).join(', ');
    return {
      success: false,
      error: errorMessage
    };
  }
  return {
    success: true,
    data: result.data
  };
}

/**
 * Validates array data against a schema and returns the validated data or throws an error
 */
export function validateArray<T>(schema: z.ZodType<T>, data: unknown[]): T[] {
  return data.map(item => validate(schema, item));
}
