import { NextRequest, NextResponse } from 'next/server';

type Message = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

export async function POST(request: NextRequest) {
  try {
    const { conceptId, conversationHistory, conceptData } = await request.json();

    // Get API key from environment (prefer GOOGLE_API_KEY)
    const apiKey = process.env.GOOGLE_API_KEY;
    
    if (!apiKey) {
      return NextResponse.json(
        { error: 'API key not configured. Please add GOOGLE_API_KEY to .env.local' },
        { status: 500 }
      );
    }

    // Build system prompt using concept's pedagogical data
    const systemPrompt = buildSocraticPrompt(conceptData);

    // Convert conversation history to Gemini format
    // Gemini doesn't support system role, so we prepend it to the first user message
    const geminiContents = convertToGeminiFormat(systemPrompt, conversationHistory);

    // Call Google Gemini API with structured output
    const model = 'gemini-2.5-flash'; // Fast and intelligent model with best price-performance
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
            maxOutputTokens: 800,
            responseMimeType: 'application/json',
            responseSchema: {
              type: 'object',
              properties: {
                message: {
                  type: 'string',
                  description: 'The Socratic dialogue response to the student',
                },
                mastery_assessment: {
                  type: 'object',
                  properties: {
                    indicators_demonstrated: {
                      type: 'array',
                      items: { type: 'string' },
                      description: 'Array of skill IDs that the student demonstrated in this exchange',
                    },
                    confidence: {
                      type: 'number',
                      description: 'Confidence level (0-1) in the assessment',
                    },
                    ready_for_mastery: {
                      type: 'boolean',
                      description: 'True if student has demonstrated sufficient mastery to complete the concept',
                    },
                    next_focus: {
                      type: 'string',
                      description: 'Which skill or area to focus on next',
                    },
                  },
                  required: ['indicators_demonstrated', 'confidence', 'ready_for_mastery'],
                },
              },
              required: ['message', 'mastery_assessment'],
            },
          },
        }),
      }
    );

    if (!response.ok) {
      const error = await response.text();
      console.error('Gemini API error:', error);
      return NextResponse.json(
        { error: 'Failed to get response from Gemini' },
        { status: response.status }
      );
    }

    const data = await response.json();
    const responseText = data.candidates[0].content.parts[0].text;
    
    // Parse the JSON response
    let parsedResponse;
    try {
      parsedResponse = JSON.parse(responseText);
    } catch (e) {
      console.error('Failed to parse JSON response:', responseText);
      // Fallback: treat as plain text
      parsedResponse = {
        message: responseText,
        mastery_assessment: {
          indicators_demonstrated: [],
          confidence: 0,
          ready_for_mastery: false,
          next_focus: 'Continue the dialogue',
        },
      };
    }

    return NextResponse.json({
      message: parsedResponse.message,
      mastery_assessment: parsedResponse.mastery_assessment,
      usage: data.usageMetadata,
    });

  } catch (error) {
    console.error('Socratic dialogue error:', error);
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
    const firstUserMessage = conversationHistory.find((msg) => msg.role === 'user');
    const firstUserIndex = conversationHistory.findIndex((msg) => msg.role === 'user');
    
    conversationHistory.forEach((msg, index) => {
      if (msg.role === 'user') {
        // Add system prompt to first user message only
        const text = index === firstUserIndex
          ? `${systemPrompt}\n\n---\n\nStudent: ${msg.content}`
          : msg.content;
        
        contents.push({
          role: 'user',
          parts: [{ text }],
        });
      } else if (msg.role === 'assistant') {
        contents.push({
          role: 'model', // Gemini uses 'model' instead of 'assistant'
          parts: [{ text: msg.content }],
        });
      }
    });
  }

  return contents;
}

// Build a Socratic teaching prompt using the concept's pedagogical data
function buildSocraticPrompt(conceptData: any): string {
  const { name, description, learning_objectives, mastery_indicators, examples, misconceptions } = conceptData;

  return `You are a Socratic tutor teaching the concept: "${name}".

**Concept Description:** ${description}

**Learning Objectives:**
${learning_objectives?.map((obj: string, i: number) => `${i + 1}. ${obj}`).join('\n') || 'Not specified'}

**Mastery Indicators (skills to assess):**
${mastery_indicators?.map((ind: any) => `- ${ind.skill}: ${ind.description} (${ind.difficulty})`).join('\n') || 'Not specified'}

**Common Misconceptions to Watch For:**
${misconceptions?.map((m: any) => `- "${m.misconception}" → Reality: ${m.reality}`).join('\n') || 'None specified'}

**Teaching Approach:**
1. Use the Socratic method: ask probing questions rather than lecturing
2. Guide the student to discover answers themselves
3. Check understanding of each learning objective through dialogue
4. Gently correct misconceptions when they arise
5. Use examples from the concept data when helpful
6. Be encouraging and patient
7. Keep responses concise (2-3 sentences with one focused question)
8. When the student demonstrates mastery of the core skills, conclude with encouragement

**Mastery Assessment Instructions:**
After each student response, evaluate which mastery indicators they demonstrated:
- Set "indicators_demonstrated" to array of skill IDs (e.g., ["quote_syntax", "evaluation_blocking"])
- Set "confidence" between 0-1 based on how clearly they showed understanding
- Set "ready_for_mastery" to true only when student has demonstrated ALL critical basic indicators and most intermediate ones
- Set "next_focus" to suggest which skill to probe next, or congratulate if mastery achieved

**Response Format:**
Return JSON with:
{
  "message": "Your Socratic response here",
  "mastery_assessment": {
    "indicators_demonstrated": ["skill_id1", "skill_id2"],
    "confidence": 0.85,
    "ready_for_mastery": false,
    "next_focus": "Let's explore X next..."
  }
}

**Example Interaction Pattern:**
- Start with an open question about their understanding
- Ask follow-up questions based on their answers
- Probe deeper when answers are incomplete or incorrect
- Celebrate correct reasoning
- Guide them toward the correct understanding without simply giving the answer

Begin the dialogue by asking them an opening question to gauge their current understanding.`;
}
