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

'use client';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

import {
  ConceptState,
  Memory,
  loadConceptStates,
  saveConceptStates,
  batchUpdateFSRS,
  ConceptAssessment,
} from '@/lib/memory-store';
import {
  DueConcept,
  calculateRetrievability,
  calculateNextInterval,
} from '@/lib/spaced-repetition';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  conceptsProbed?: ConceptProbed[];
};

type ConceptProbed = {
  conceptId: string;
  understanding: number;
  new_memory?: {
    content: string;
    understanding: number;
    context?: string;
  };
};

type ReviewDialogueProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  dueConcepts: DueConcept[];
  conceptNames: Map<string, string>;  // conceptId -> name mapping
  libraryId: string;
  onReviewComplete?: (assessments: ConceptAssessment[]) => void;
};

export default function ReviewDialogue({
  open,
  onOpenChange,
  dueConcepts,
  conceptNames,
  libraryId,
  onReviewComplete,
}: ReviewDialogueProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [reviewComplete, setReviewComplete] = useState(false);
  const [allAssessments, setAllAssessments] = useState<ConceptAssessment[]>([]);
  const [conceptStates, setConceptStates] = useState<Map<string, ConceptState>>(new Map());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load concept states on mount
  useEffect(() => {
    if (open) {
      const states = loadConceptStates(libraryId);
      setConceptStates(states);
    }
  }, [libraryId, open]);

  // Auto-focus textarea when loading completes
  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  // Start the dialogue when modal opens
  useEffect(() => {
    if (open && !hasStarted && dueConcepts.length > 0) {
      startDialogue();
    }
  }, [open, hasStarted, dueConcepts]);

  // Reset when modal closes
  useEffect(() => {
    if (!open) {
      setMessages([]);
      setHasStarted(false);
      setInput('');
      setReviewComplete(false);
      setAllAssessments([]);
    }
  }, [open]);

  const startDialogue = async () => {
    setIsLoading(true);
    setHasStarted(true);

    // Prepare due concepts with memories
    const dueConceptsWithMemories = dueConcepts.map(dc => ({
      conceptId: dc.conceptId,
      conceptName: conceptNames.get(dc.conceptId) || dc.conceptId,
      retrievability: dc.retrievability,
      memories: dc.state.memories,
    }));

    try {
      const response = await fetch('/api/review-dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversationHistory: [],
          dueConcepts: dueConceptsWithMemories,
          libraryId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start review');
      }

      const data = await response.json();
      
      // Process any concepts probed in the opening
      if (data.concepts_probed?.length > 0) {
        processConceptsProbed(data.concepts_probed);
      }
      
      setMessages([{ 
        role: 'assistant', 
        content: data.message,
        conceptsProbed: data.concepts_probed,
      }]);
      
      setReviewComplete(data.review_complete);
    } catch (error) {
      console.error('Error starting review:', error);
      setMessages([
        {
          role: 'assistant',
          content: error instanceof Error 
            ? `Error: ${error.message}` 
            : 'Sorry, I encountered an error starting the review.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const processConceptsProbed = (conceptsProbed: ConceptProbed[]) => {
    const newAssessments: ConceptAssessment[] = conceptsProbed.map(cp => ({
      conceptId: cp.conceptId,
      understanding: cp.understanding,
      newMemory: cp.new_memory,
    }));
    
    setAllAssessments(prev => [...prev, ...newAssessments]);
  };

  const sendMessage = async () => {
    const currentInput = input.trim();
    if (!currentInput || isLoading) return;

    const userMessage: Message = { role: 'user', content: currentInput };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    // Prepare due concepts with memories
    const dueConceptsWithMemories = dueConcepts.map(dc => ({
      conceptId: dc.conceptId,
      conceptName: conceptNames.get(dc.conceptId) || dc.conceptId,
      retrievability: dc.retrievability,
      memories: dc.state.memories,
    }));

    try {
      const conversationHistory = updatedMessages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch('/api/review-dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversationHistory,
          dueConcepts: dueConceptsWithMemories,
          libraryId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Process any concepts probed
      if (data.concepts_probed?.length > 0) {
        processConceptsProbed(data.concepts_probed);
      }
      
      setMessages([...updatedMessages, { 
        role: 'assistant', 
        content: data.message,
        conceptsProbed: data.concepts_probed,
      }]);
      
      if (data.review_complete) {
        setReviewComplete(true);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: `⚠️ **Error:** ${errorMessage}\n\nPlease try again.`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFinishReview = () => {
    // Save all assessments to localStorage
    if (allAssessments.length > 0) {
      const updatedStates = batchUpdateFSRS(conceptStates, allAssessments);
      saveConceptStates(libraryId, updatedStates);
      console.log('💾 Saved review assessments:', allAssessments.length);
    }
    
    // Notify parent
    if (onReviewComplete) {
      onReviewComplete(allAssessments);
    }
    
    onOpenChange(false);
  };

  if (dueConcepts.length === 0) return null;

  // Calculate review progress
  const conceptsReviewed = new Set(allAssessments.map(a => a.conceptId));
  const progressPercent = Math.round((conceptsReviewed.size / dueConcepts.length) * 100);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[100vw] md:max-w-3xl w-[100vw] md:w-auto h-[100vh] md:!h-[90vh] flex flex-col p-2 md:p-4">
        <DialogHeader className="pb-2">
          <DialogTitle className="text-lg md:text-xl">Review Session</DialogTitle>
          <DialogDescription className="text-sm">
            {dueConcepts.length} concept{dueConcepts.length > 1 ? 's' : ''} to review
          </DialogDescription>
        </DialogHeader>

        {/* Progress indicator - matches SocraticDialogue style */}
        <div className="px-3 md:px-4 py-2 bg-slate-50 rounded-lg space-y-2 text-sm">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Progress:</span>
            <span className="text-slate-600">
              {conceptsReviewed.size} / {dueConcepts.length} concepts reviewed
            </span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          
          {/* Concept pills showing status */}
          <div className="flex flex-wrap gap-1.5 pt-2">
            {dueConcepts.map(dc => {
              const isReviewed = conceptsReviewed.has(dc.conceptId);
              const assessment = allAssessments.find(a => a.conceptId === dc.conceptId);
              const understanding = assessment?.understanding;
              
              return (
                <span
                  key={dc.conceptId}
                  className={`px-2 py-0.5 rounded-full text-xs font-medium transition-colors duration-200 ${
                    isReviewed
                      ? understanding && understanding >= 0.7
                        ? 'bg-green-100 text-green-700'
                        : understanding && understanding >= 0.4
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-red-100 text-red-700'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  {conceptNames.get(dc.conceptId) || dc.conceptId}
                  {isReviewed && understanding !== undefined && (
                    <span className="ml-1">{Math.round(understanding * 100)}%</span>
                  )}
                </span>
              );
            })}
          </div>
          
          {reviewComplete && (
            <div className="pt-3 border-t space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-green-600 font-medium">
                  ✅ Review session complete!
                </span>
                <Button 
                  onClick={handleFinishReview}
                  variant="default"
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  Finish Review
                </Button>
              </div>
              
              {/* Show next review schedule */}
              {allAssessments.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-xs font-medium text-blue-700 mb-2">📅 Next Reviews Scheduled:</p>
                  <div className="space-y-1">
                    {allAssessments.map((assessment) => {
                      const currentState = dueConcepts.find(dc => dc.conceptId === assessment.conceptId)?.state;
                      const currentStability = currentState?.stability || 1;
                      const newStability = calculateNextInterval(
                        currentStability,
                        assessment.understanding,
                        currentState?.difficulty || 0.3
                      );
                      const daysUntilNext = Math.round(newStability);
                      
                      return (
                        <div key={assessment.conceptId} className="flex items-center justify-between text-xs">
                          <span className="text-blue-800">
                            {conceptNames.get(assessment.conceptId) || assessment.conceptId}
                          </span>
                          <span className="text-blue-600 font-medium">
                            {daysUntilNext === 1 ? 'Tomorrow' : `in ${daysUntilNext} days`}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Messages area - matches SocraticDialogue style */}
        <div className="flex-1 overflow-y-auto space-y-4 py-4 px-2">
          {messages.map((msg, idx) => (
            <div key={idx} className="space-y-2">
              <div
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-100 text-slate-900'
                  }`}
                >
                  <div className={`text-sm prose prose-sm max-w-none prose-p:my-2 prose-pre:my-2 ${
                    msg.role === 'user' ? 'prose-invert' : 'prose-slate'
                  }`}>
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({ node, inline, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={oneDark}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code 
                              className={`${className} px-1 py-0.5 rounded text-xs ${
                                msg.role === 'user' 
                                  ? 'bg-blue-600 text-white' 
                                  : 'bg-slate-200 text-slate-900'
                              }`} 
                              {...props}
                            >
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 rounded-lg px-4 py-2">
                <p className="text-sm text-slate-600">Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area - matches SocraticDialogue style */}
        <div className="space-y-2 pt-4 border-t">
          <div className="flex gap-2">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your response... (Enter to send, Shift+Enter for new line)"
              className="flex-1 min-h-[60px] max-h-[120px]"
              disabled={isLoading}
            />
            <div className="flex flex-col gap-2">
              <Button onClick={sendMessage} disabled={isLoading || !input.trim()}>
                Send
              </Button>
              {!reviewComplete && (
                <Button 
                  variant="outline" 
                  onClick={handleFinishReview}
                  size="sm"
                  className="text-xs"
                >
                  End Early
                </Button>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
