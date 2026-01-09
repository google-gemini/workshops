/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { NextRequest, NextResponse } from 'next/server';

type Message = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

// Memory type from memory-store
type Memory = {
  id: string;
  conceptId: string;
  content: string;
  understanding: number;
  timestamp: number;
  context?: string;
};

// Due concept with memories for review
type DueConceptForReview = {
  conceptId: string;
  conceptName: string;
  retrievability: number;
  memories: Memory[];
};

// Response types
type ConceptProbed = {
  conceptId: string;
  understanding: number;
  new_memory?: {
    content: string;
    understanding: number;
    context?: string;
  };
};

export async function POST(request: NextRequest) {
  try {
    const { 
      conversationHistory, 
      dueConcepts,
      libraryId,
    } = await request.json();

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🔄 NEW REVIEW DIALOGUE REQUEST');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📌 Library ID:', libraryId);
    console.log('📌 Conversation turns:', conversationHistory.length);
    console.log('📌 Due concepts:', dueConcepts?.length || 0);
    
    if (dueConcepts?.length > 0) {
      console.log('📌 Concepts to review:');
      dueConcepts.forEach((c: DueConceptForReview, i: number) => {
        console.log(`   ${i + 1}. ${c.conceptName} (${Math.round(c.retrievability * 100)}% retained, ${c.memories.length} memories)`);
      });
    }

    // Get API key from environment
    const apiKey = process.env.GOOGLE_API_KEY;
    
    if (!apiKey) {
      return NextResponse.json(
        { error: 'API key not configured. Please add GOOGLE_API_KEY to .env.local' },
        { status: 500 }
      );
    }

    // Build system prompt for review conversation
    const systemPrompt = buildReviewPrompt(dueConcepts as DueConceptForReview[]);
    
    console.log('\n📝 SYSTEM PROMPT CONSTRUCTED:');
    console.log(`   - Total length: ${systemPrompt.length} characters`);

    // Convert conversation history to Gemini format
    const geminiContents = convertToGeminiFormat(systemPrompt, conversationHistory);
    
    console.log('\n📤 SENDING TO GEMINI:');
    console.log(`   - Total messages: ${geminiContents.length}`);

    // Call Google Gemini API with structured output
    const model = 'gemini-2.5-flash';
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: geminiContents,
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 1500,
            responseMimeType: 'application/json',
            responseSchema: {
              type: 'object',
              properties: {
                message: {
                  type: 'string',
                  description: 'The conversational response to the student',
                },
                concepts_probed: {
                  type: 'array',
                  description: 'Array of concepts that were probed in this exchange',
                  items: {
                    type: 'object',
                    properties: {
                      conceptId: {
                        type: 'string',
                        description: 'The ID of the concept that was probed',
                      },
                      understanding: {
                        type: 'number',
                        description: 'Understanding level demonstrated (0-1)',
                      },
                      new_memory: {
                        type: 'object',
                        description: 'Optional memory note about this interaction',
                        properties: {
                          content: {
                            type: 'string',
                            description: 'Note about what the student demonstrated or struggled with',
                          },
                          understanding: {
                            type: 'number',
                            description: 'Understanding level (0-1)',
                          },
                          context: {
                            type: 'string',
                            description: 'What prompted this observation',
                          },
                        },
                        required: ['content', 'understanding'],
                      },
                    },
                    required: ['conceptId', 'understanding'],
                  },
                },
                review_complete: {
                  type: 'boolean',
                  description: 'True if all key concepts have been sufficiently probed and the review can end naturally',
                },
              },
              required: ['message', 'concepts_probed', 'review_complete'],
            },
          },
        }),
      }
    );

    if (!response.ok) {
      const error = await response.text();
      console.error('\n❌ GEMINI API ERROR:');
      console.error(error);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
      return NextResponse.json(
        { error: 'Failed to get response from Gemini' },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    console.log('\n📥 RECEIVED FROM GEMINI:');
    console.log('   - Usage metadata:', JSON.stringify(data.usageMetadata, null, 2));
    
    // Find the text response
    const textPart = data.candidates[0].content.parts.find(
      (part: any) => part.text !== undefined
    );
    
    if (!textPart) {
      console.error('\n❌ No text part found in response');
      return NextResponse.json(
        { error: 'Invalid response structure from Gemini' },
        { status: 500 }
      );
    }
    
    const responseText = textPart.text;
    console.log('\n📄 RAW RESPONSE TEXT:');
    console.log(responseText.substring(0, 500) + (responseText.length > 500 ? '...' : ''));
    
    // Parse the JSON response
    let parsedResponse;
    try {
      parsedResponse = JSON.parse(responseText);
      console.log('\n✅ PARSED RESPONSE:');
      console.log('   - Message length:', parsedResponse.message.length);
      console.log('   - Concepts probed:', parsedResponse.concepts_probed?.length || 0);
      console.log('   - Review complete:', parsedResponse.review_complete);
      
      if (parsedResponse.concepts_probed?.length > 0) {
        parsedResponse.concepts_probed.forEach((cp: ConceptProbed) => {
          console.log(`   - ${cp.conceptId}: understanding ${Math.round(cp.understanding * 100)}%`);
        });
      }
    } catch (e) {
      console.error('\n❌ JSON PARSE ERROR:', e);
      
      parsedResponse = {
        message: '⚠️ I encountered an error. Please click retry to try again.',
        concepts_probed: [],
        review_complete: false,
      };
    }

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    return NextResponse.json({
      message: parsedResponse.message,
      concepts_probed: parsedResponse.concepts_probed || [],
      review_complete: parsedResponse.review_complete || false,
      usage: data.usageMetadata,
    });

  } catch (error) {
    console.error('\n💥 UNEXPECTED ERROR:');
    console.error(error);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Convert OpenAI-style messages to Gemini format
function convertToGeminiFormat(systemPrompt: string, conversationHistory: Message[]) {
  const contents: any[] = [];

  // If conversation is empty, add system prompt as first user message
  if (conversationHistory.length === 0) {
    contents.push({
      role: 'user',
      parts: [{ text: systemPrompt }],
    });
  } else {
    // Prepend system prompt to the first user message
    const firstUserIndex = conversationHistory.findIndex((msg) => msg.role === 'user');
    
    conversationHistory.forEach((msg, index) => {
      if (msg.role === 'user') {
        const text = index === firstUserIndex
          ? `${systemPrompt}\n\n---\n\nStudent: ${msg.content}`
          : msg.content;
        
        contents.push({
          role: 'user',
          parts: [{ text }],
        });
      } else if (msg.role === 'assistant') {
        contents.push({
          role: 'model',
          parts: [{ text: msg.content }],
        });
      }
    });
  }

  return contents;
}

// Build a review-focused prompt for multi-concept conversations
function buildReviewPrompt(dueConcepts: DueConceptForReview[]): string {
  // Format concepts with their memories
  const conceptsList = dueConcepts.map((c, i) => {
    const retentionPercent = Math.round(c.retrievability * 100);
    const memorySummary = c.memories.length > 0
      ? c.memories.slice(-3).map(m => `"${m.content}"`).join('; ')
      : 'No previous notes';
    
    return `${i + 1}. **${c.conceptName}** (ID: ${c.conceptId})
   - Current retention: ${retentionPercent}%
   - Past notes: ${memorySummary}`;
  }).join('\n\n');

  return `You are a friendly tutor having a review conversation with a student. Your job is to naturally probe their recall of concepts they've learned previously.

**CONCEPTS DUE FOR REVIEW:**

${conceptsList}

**YOUR OBJECTIVES:**

1. Start with a casual greeting, then naturally ask about the concepts
2. Focus on concepts with lower retention first (they need the most reinforcement)
3. Use your past notes to personalize questions - reference specific struggles or successes
4. Probe understanding through questions, not by lecturing
5. If they struggle, give hints rather than answers
6. Assess their understanding from their responses (0-1 scale)
7. Write new memory notes when you observe something notable about their understanding
8. When you've adequately probed the key concepts, wrap up the conversation naturally

**CONVERSATION GUIDELINES:**

- Be conversational and encouraging, not clinical
- Don't make it feel like a test - it should feel like catching up with a tutor
- Weave between concepts naturally based on the conversation flow
- You don't have to cover every concept - focus on the most important ones
- Keep responses concise (2-4 sentences with a question)
- Set review_complete to true when you've covered the key concepts and it's a natural ending point

**ASSESSMENT GUIDELINES:**

- 0.0-0.3: Major confusion, forgot key points, needs significant review
- 0.4-0.6: Partial recall, got the gist but missing details
- 0.7-0.9: Good recall, understood with minor gaps
- 1.0: Perfect recall, quick and confident response

**MEMORY WRITING GUIDELINES:**

- Write a new_memory when the student shows notable understanding or confusion
- Keep notes concise but specific: what they understood, what they confused
- Include context about what prompted the observation
- Don't write a memory for every interaction - only when noteworthy

**RESPONSE FORMAT:**

Return JSON with:
{
  "message": "Your conversational response here",
  "concepts_probed": [
    {
      "conceptId": "concept_id",
      "understanding": 0.75,
      "new_memory": {
        "content": "Student explained X clearly but still confuses Y with Z",
        "understanding": 0.75,
        "context": "When asked about recursion"
      }
    }
  ],
  "review_complete": false
}

Begin with a friendly opening that leads into probing their recall of the first concept.`;
}
