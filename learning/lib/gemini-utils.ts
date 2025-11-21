import { z } from "zod";

/**
 * Convert Zod schema to Gemini-compatible JSON schema
 * 
 * Uses Zod's native z.toJSONSchema() and strips out fields that Gemini doesn't support.
 * Only includes: type, properties, description, enum, items, required
 */
export function zodToGeminiSchema(zodSchema: z.ZodType): any {
  const jsonSchema = z.toJSONSchema(zodSchema);
  
  function cleanSchema(schema: any): any {
    if (typeof schema !== 'object' || schema === null) {
      return schema;
    }
    
    // Start with empty object and only add supported fields
    const cleaned: any = {};
    
    // Fields that Gemini API accepts
    if ('type' in schema) cleaned.type = schema.type;
    if ('description' in schema) cleaned.description = schema.description;
    if ('enum' in schema) cleaned.enum = schema.enum;
    if ('items' in schema) cleaned.items = cleanSchema(schema.items);
    if ('required' in schema) cleaned.required = schema.required;
    
    // Recursively clean properties
    if ('properties' in schema) {
      cleaned.properties = {};
      for (const [key, value] of Object.entries(schema.properties)) {
        cleaned.properties[key] = cleanSchema(value);
      }
    }
    
    return cleaned;
  }
  
  return cleanSchema(jsonSchema);
}
