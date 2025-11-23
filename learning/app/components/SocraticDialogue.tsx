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
import PythonScratchpad from './PythonScratchpad';
import LispScratchpad from './LispScratchpad';
import { MarkdownViewer } from './MarkdownViewer';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

type ChunkSource = {
  text: string;
  topic: string;
  chunk_type: string;
  similarity: number;
  
  // Markdown metadata
  source_file?: string;
  heading_path?: string[];
  markdown_anchor?: string;
  start_line?: number;
  end_line?: number;
  
  // Video metadata
  video_id?: string;
  timestamp?: number;
  segment_index?: number;
  frame_path?: string;
  audio_text?: string;
  audio_start?: number;
  audio_end?: number;
};

type Message = {
  role: 'user' | 'assistant';
  content: string;
  assessment?: MasteryAssessment;
  sources?: ChunkSource[];
};

type MasteryAssessment = {
  indicators_demonstrated: string[];
  confidence: number;
  ready_for_mastery: boolean;
  next_focus?: string;
};

type SocraticDialogueProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  conceptData: any;
  embeddingsPath: string;
  workspaceType?: 'python' | 'lisp';
  sourceFile?: string;
  libraryType?: string;
  onMasteryAchieved?: (conceptId: string) => void;
};

export default function SocraticDialogue({
  open,
  onOpenChange,
  conceptData,
  embeddingsPath,
  workspaceType = 'python',
  sourceFile = '/data/pytudes/tsp.md',
  libraryType,
  onMasteryAchieved,
}: SocraticDialogueProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [demonstratedSkills, setDemonstratedSkills] = useState<Set<string>>(new Set());
  const [readyForMastery, setReadyForMastery] = useState(false);
  const [textbookContext, setTextbookContext] = useState<string | null>(null);
  const [code, setCode] = useState<string>('');
  const [evaluation, setEvaluation] = useState<{
    output: string;
    error: string | null;
  } | null>(null);
  const [lastFailedMessage, setLastFailedMessage] = useState<{
    input: string;
    code: string;
    evaluation: any;
    conversationHistory: any[];
  } | null>(null);
  const [lastSentCode, setLastSentCode] = useState<string>('');
  const [lastSentEvaluation, setLastSentEvaluation] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'workspace' | 'source'>('workspace');
  const [mobileActiveTab, setMobileActiveTab] = useState<'chat' | 'workspace'>('chat');
  const [objectivesExpanded, setObjectivesExpanded] = useState(false);
  const [sourceAnchor, setSourceAnchor] = useState<string | undefined>();
  const [sourceFile, setSourceFile] = useState<string | undefined>();
  const [sourceVideoId, setSourceVideoId] = useState<string | undefined>();
  const [sourceTimestamp, setSourceTimestamp] = useState<number | undefined>();
  const [videoAutoplay, setVideoAutoplay] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-load first video source for video libraries (but don't autoplay)
  useEffect(() => {
    if (libraryType === 'video' && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && lastMessage.sources) {
        const firstVideoSource = lastMessage.sources.find(s => s.video_id);
        if (firstVideoSource && firstVideoSource.video_id) {
          setSourceVideoId(firstVideoSource.video_id);
          setSourceTimestamp(firstVideoSource.audio_start);
          setVideoAutoplay(false); // Don't autoplay on auto-load
          setSourceFile(undefined);
          setSourceAnchor(undefined);
        }
      }
    }
  }, [messages, libraryType]);

  // Auto-focus textarea when loading completes
  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  // Start the dialogue when modal opens
  useEffect(() => {
    if (open && !hasStarted) {
      startDialogue();
    }
  }, [open, hasStarted]);

  // Reset when modal closes
  useEffect(() => {
    if (!open) {
      setMessages([]);
      setHasStarted(false);
      setInput('');
      setDemonstratedSkills(new Set());
      setReadyForMastery(false);
      setTextbookContext(null);
      setCode('');
      setEvaluation(null);
      setLastSentCode('');
      setLastSentEvaluation(null);
      setActiveTab('workspace');
      setSourceAnchor(undefined);
      setSourceFile(undefined);
      setSourceVideoId(undefined);
      setSourceTimestamp(undefined);
      setVideoAutoplay(false);
    }
  }, [open]);

  const startDialogue = async () => {
    setIsLoading(true);
    setHasStarted(true);

    try {
      const response = await fetch('/api/socratic-dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conceptId: conceptData.id,
          conversationHistory: [],
          conceptData,
          textbookContext: null, // Signal: please do semantic search
          embeddingsPath,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start dialogue');
      }

      const data = await response.json();
      
      // Cache the textbook context for subsequent turns
      if (data.textbookContext) {
        setTextbookContext(data.textbookContext);
        console.log('📦 Cached textbook context:', data.textbookContext.length, 'characters');
      }
      
      // Update demonstrated skills if assessment provided
      if (data.mastery_assessment) {
        const newSkills = new Set(demonstratedSkills);
        data.mastery_assessment.indicators_demonstrated.forEach((skill: string) => 
          newSkills.add(skill)
        );
        setDemonstratedSkills(newSkills);
        setReadyForMastery(data.mastery_assessment.ready_for_mastery);
      }
      
      setMessages([{ 
        role: 'assistant', 
        content: data.message,
        assessment: data.mastery_assessment,
        sources: data.sources || []
      }]);
    } catch (error) {
      console.error('Error starting dialogue:', error);
      setMessages([
        {
          role: 'assistant',
          content: error instanceof Error 
            ? `Error: ${error.message}` 
            : 'Sorry, I encountered an error starting the dialogue. Please check that your API key is configured in .env.local',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (retryData?: {
    input: string;
    code: string;
    evaluation: any;
    conversationHistory: any[];
  }) => {
    const currentInput = retryData?.input ?? input.trim();
    const currentCode = retryData?.code ?? code.trim();
    const currentEval = retryData?.evaluation ?? evaluation;
    
    const hasText = currentInput.length > 0;
    const hasCode = currentCode.length > 0;
    
    if ((!hasText && !hasCode) || isLoading) return;

    // Check what actually changed since last turn
    const codeChanged = currentCode !== lastSentCode;
    const evalChanged = JSON.stringify(currentEval) !== JSON.stringify(lastSentEvaluation);

    // For UI display: just show the text (code is already visible in workspace)
    const workspaceName = workspaceType === 'lisp' ? 'Lisp' : 'Python';
    const displayContent = hasText ? currentInput : `(working in ${workspaceName} workspace)`;
    
    // For API: only include code/evaluation if they changed
    let apiContent = currentInput || '(sharing code)';
    
    if (codeChanged && currentCode) {
      const codeLanguage = workspaceType === 'lisp' ? 'lisp' : 'python';
      apiContent += `\n\n**My Code:**\n\`\`\`${codeLanguage}\n${currentCode}\n\`\`\``;
    }
    
    if (evalChanged && currentEval) {
      if (currentEval.error) {
        apiContent += `\n\n**Error:**\n${currentEval.error}`;
      } else {
        apiContent += `\n\n**Output:**\n${currentEval.output || '(no output)'}`;
      }
    }

    // Display clean version in UI
    const userMessage: Message = { role: 'user', content: displayContent };
    const updatedMessages = retryData 
      ? [...messages.slice(0, -1), userMessage] // Replace error message
      : [...messages, userMessage];
    setMessages(updatedMessages);
    
    // Clear input only if not retrying
    if (!retryData) {
      setInput('');
    }
    
    setIsLoading(true);
    setLastFailedMessage(null); // Clear any previous failure

    try {
      // Send full context to API
      const conversationHistory = retryData?.conversationHistory ?? 
        updatedMessages.slice(0, -1).map((msg) => ({
          role: msg.role,
          content: msg.content,
        }));
      
      // Add current message with full context (code + eval)
      conversationHistory.push({
        role: 'user',
        content: apiContent
      });

      const response = await fetch('/api/socratic-dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conceptId: conceptData.id,
          conversationHistory,
          conceptData,
          textbookContext,
          embeddingsPath,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Update demonstrated skills if assessment provided
      if (data.mastery_assessment) {
        const newSkills = new Set(demonstratedSkills);
        data.mastery_assessment.indicators_demonstrated.forEach((skill: string) => 
          newSkills.add(skill)
        );
        setDemonstratedSkills(newSkills);
        setReadyForMastery(data.mastery_assessment.ready_for_mastery);
      }
      
      // Update tracking for next turn - only if they were actually sent
      if (codeChanged) setLastSentCode(currentCode);
      if (evalChanged) setLastSentEvaluation(currentEval);
      
      setMessages([...updatedMessages, { 
        role: 'assistant', 
        content: data.message,
        assessment: data.mastery_assessment,
        sources: data.sources || []
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Save failed message for retry
      setLastFailedMessage({
        input: currentInput,
        code: currentCode,
        evaluation: currentEval,
        conversationHistory: updatedMessages.slice(0, -1).map((msg) => ({
          role: msg.role,
          content: msg.content,
        })),
      });
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: `⚠️ **Error:** ${errorMessage}\n\nYour message was saved. Click the retry button below to try again.`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const retryLastMessage = () => {
    if (lastFailedMessage) {
      sendMessage(lastFailedMessage);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleMarkAsMastered = () => {
    console.log('Concept mastered:', conceptData.id);
    
    // Call the parent callback to update mastery state
    if (onMasteryAchieved) {
      onMasteryAchieved(conceptData.id);
    }
    
    // Show success message and close dialogue
    alert(`🎉 Concept "${conceptData.name}" marked as mastered!\n\nThe graph has been updated!`);
    onOpenChange(false);
  };

  if (!conceptData) return null;

  // Calculate progress
  const totalIndicators = conceptData.mastery_indicators?.length || 0;
  const demonstratedCount = demonstratedSkills.size;
  const progressPercent = totalIndicators > 0 ? (demonstratedCount / totalIndicators) * 100 : 0;

  // Show Python scratchpad by default (can opt-out with hide_editor: true)
  const showPythonEditor = conceptData.hide_editor !== true;

  // Send button: enabled if text OR code exists
  const canSend = !isLoading && (input.trim().length > 0 || code.trim().length > 0);

  // Dynamic source tab label based on library type
  const sourceTabLabel = libraryType === 'video' ? '🎥 Video' : 
                         libraryType === 'book' ? '📚 Source' : 
                         '📖 Reference';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={`
        ${showPythonEditor ? 'max-w-[100vw] md:!max-w-[96vw] w-[100vw] md:!w-[96vw]' : 'max-w-[100vw] md:max-w-3xl w-[100vw] md:w-auto'}
        h-[100vh] md:!h-[90vh] 
        flex flex-col p-2 md:p-4
      `}>
        <DialogHeader className="pb-2">
          <DialogTitle className="text-lg md:text-xl">Learning: {conceptData.name}</DialogTitle>
          <DialogDescription className="text-sm">{conceptData.description}</DialogDescription>
        </DialogHeader>

        {/* Mobile-only top-level tabs */}
        {showPythonEditor && (
          <div className="flex md:hidden border-b border-slate-200 -mx-2 px-2">
            <button
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                mobileActiveTab === 'chat'
                  ? 'border-b-2 border-blue-500 text-blue-600 -mb-px'
                  : 'text-slate-600'
              }`}
              onClick={() => setMobileActiveTab('chat')}
            >
              💬 Chat
            </button>
            <button
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                mobileActiveTab === 'workspace'
                  ? 'border-b-2 border-blue-500 text-blue-600 -mb-px'
                  : 'text-slate-600'
              }`}
              onClick={() => setMobileActiveTab('workspace')}
            >
              🐍 Workspace
            </button>
          </div>
        )}

        {/* Progress indicator - always visible */}
        {totalIndicators > 0 ? (
          <div className="px-3 md:px-4 py-2 bg-slate-50 rounded-lg space-y-2 text-sm">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Progress:</span>
              <span className="text-slate-600">
                {demonstratedCount} / {totalIndicators} skills demonstrated
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            {readyForMastery && (
              <div className="flex items-center justify-between pt-2 border-t">
                <span className="text-sm text-green-600 font-medium">
                  ✨ Ready for mastery!
                </span>
                <Button 
                  onClick={handleMarkAsMastered}
                  variant="default"
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  Mark as Mastered
                </Button>
              </div>
            )}
          </div>
        ) : (
          // Fallback for concepts without explicit mastery indicators
          readyForMastery && (
            <div className="px-4 py-2 bg-slate-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-green-600 font-medium">
                  ✨ Ready for mastery!
                </span>
                <Button 
                  onClick={handleMarkAsMastered}
                  variant="default"
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  Mark as Mastered
                </Button>
              </div>
            </div>
          )
        )}

        {/* Main content area */}
        <div className="flex-1 flex gap-4 overflow-auto">
          {/* Messages area (left side on desktop, full width on mobile when chat tab active) */}
          <div className={`
            ${showPythonEditor ? 'md:flex-1 md:min-w-0' : 'w-full'} 
            ${showPythonEditor && mobileActiveTab === 'workspace' ? 'hidden md:flex' : 'flex'}
            flex-col w-full
          `}>
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
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex]}
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
              
              {/* Show sources for assistant messages */}
              {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                <div className="ml-4 text-xs space-y-1">
                  <details className="group">
                    <summary className="cursor-pointer text-slate-500 hover:text-slate-700 flex items-center gap-1">
                      📚 {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''} used
                      <span className="text-slate-400 group-open:rotate-90 transition-transform">▶</span>
                    </summary>
                    <div className="mt-2 pl-4 space-y-2 border-l-2 border-slate-200">
                      {msg.sources.map((source, sourceIdx) => (
                        <div key={sourceIdx} className="bg-slate-50 rounded p-2 space-y-1">
                          <div className="font-medium text-slate-700">
                            {source.topic}
                          </div>
                          
                          {source.heading_path && source.heading_path.length > 0 && (
                            <div className="text-slate-500 text-xs">
                              📍 {source.heading_path.join(' › ')}
                            </div>
                          )}
                          
                          {/* Video source */}
                          {source.video_id && source.audio_start !== undefined && (
                            <div className="flex items-center gap-2 text-xs">
                              <span className="text-slate-400">
                                📹 Video @ {Math.floor(source.audio_start / 60)}:{String(Math.floor(source.audio_start % 60)).padStart(2, '0')}
                                {source.audio_text && ` - "${source.audio_text.substring(0, 50)}..."`}
                              </span>
                              <button
                                className="text-blue-500 hover:text-blue-700 underline text-left"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setSourceVideoId(source.video_id);
                                  setSourceTimestamp(source.audio_start);
                                  setVideoAutoplay(true); // Autoplay when user explicitly clicks
                                  setSourceAnchor(undefined); // Clear markdown state
                                  setSourceFile(undefined);
                                  setActiveTab('source');
                                }}
                              >
                                View in context →
                              </button>
                            </div>
                          )}
                          
                          {/* Markdown source */}
                          {source.source_file && (
                            <div className="flex items-center gap-2 text-xs">
                              <span className="text-slate-400">
                                {source.source_file}
                                {source.start_line && ` (lines ${source.start_line}-${source.end_line})`}
                              </span>
                              {source.markdown_anchor && (
                                <button
                                  className="text-blue-500 hover:text-blue-700 underline text-left"
                                  onClick={(e) => {
                                    e.preventDefault();
                                    setSourceAnchor(source.markdown_anchor);
                                    setSourceFile(source.source_file);
                                    setSourceVideoId(undefined); // Clear video state
                                    setSourceTimestamp(undefined);
                                    setVideoAutoplay(false);
                                    setActiveTab('source');
                                  }}
                                >
                                  View in context →
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}
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

            {/* Input area */}
            <div className="space-y-2 pt-4 border-t">
              {lastFailedMessage && (
                <div className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <span className="text-sm text-amber-800">
                    💬 Previous message failed - click retry to send again
                  </span>
                  <Button 
                    onClick={retryLastMessage}
                    variant="default"
                    size="sm"
                    className="bg-amber-600 hover:bg-amber-700"
                    disabled={isLoading}
                  >
                    Retry
                  </Button>
                </div>
              )}
              
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
                <Button onClick={() => sendMessage()} disabled={!canSend}>
                  Send
                </Button>
              </div>
            </div>
          </div>

          {/* Right side: Tabbed pane (Workspace / Source) - shown by default, controlled by mobile tab on mobile */}
          {showPythonEditor && (
            <div className={`
              md:flex-1 md:min-w-0 md:border-l md:pl-3 flex flex-col
              ${mobileActiveTab === 'chat' ? 'hidden md:flex' : 'flex'}
              w-full
            `}>
              {/* Tab Headers (Python/Video) - hidden on mobile, shown on desktop */}
              <div className="hidden md:flex border-b border-slate-200 bg-slate-50 mb-2">
                <button
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'workspace' 
                      ? 'border-b-2 border-blue-500 text-blue-600 bg-white -mb-px' 
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  onClick={() => setActiveTab('workspace')}
                >
                  {workspaceType === 'lisp' ? '🎨 Lisp' : '🐍 Python'}
                </button>
                <button
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'source' 
                      ? 'border-b-2 border-blue-500 text-blue-600 bg-white -mb-px' 
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  onClick={() => {
                    setActiveTab('source');
                    // Autoplay video when switching to Video tab (if video is loaded)
                    if (sourceVideoId) {
                      setVideoAutoplay(true);
                    }
                  }}
                >
                  {sourceTabLabel}
                </button>
              </div>

              {/* Mobile: Show active tab selector when in workspace mode */}
              <div className="flex md:hidden border-b border-slate-200 bg-slate-50 mb-2">
                <button
                  className={`flex-1 px-3 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'python'
                      ? 'border-b-2 border-blue-500 text-blue-600 -mb-px'
                      : 'text-slate-600'
                  }`}
                  onClick={() => setActiveTab('python')}
                >
                  🐍 Python
                </button>
                <button
                  className={`flex-1 px-3 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'source'
                      ? 'border-b-2 border-blue-500 text-blue-600 -mb-px'
                      : 'text-slate-600'
                  }`}
                  onClick={() => {
                    setActiveTab('source');
                    if (sourceVideoId) {
                      setVideoAutoplay(true);
                    }
                  }}
                >
                  {sourceTabLabel}
                </button>
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-hidden">
                {activeTab === 'workspace' ? (
                  workspaceType === 'lisp' ? (
                    <LispScratchpad
                      starterCode={`;;; Common Lisp scratchpad for exploring ${conceptData.name}
;;; 
;;; Feel free to experiment here! You can:
;;; - Test out ideas in code
;;; - Answer questions by implementing solutions
;;; - Work through examples
;;; 
;;; Your code and output will be visible to your tutor.
`}
                      onExecute={(execCode, output, error) => {
                        setEvaluation({ output, error });
                      }}
                      onCodeChange={(newCode) => {
                        setCode(newCode);
                      }}
                    />
                  ) : (
                    <PythonScratchpad
                      starterCode={`# 🧮 Python scratchpad for exploring ${conceptData.name}
# 
# Feel free to experiment here! You can:
# - Test out ideas in code
# - Answer questions by implementing solutions
# - Work through examples
# 
# Your code and output will be visible to your tutor.
`}
                      onExecute={(execCode, output, error) => {
                        setEvaluation({ output, error });
                      }}
                      onCodeChange={(newCode) => {
                        setCode(newCode);
                      }}
                    />
                  )
                ) : sourceVideoId ? (
                  <div className="w-full h-full flex flex-col bg-black rounded-lg overflow-hidden">
                    <iframe
                      className="w-full h-full"
                      src={`https://www.youtube.com/embed/${sourceVideoId}?start=${Math.floor(sourceTimestamp || 0)}${videoAutoplay ? '&autoplay=1' : ''}`}
                      title="YouTube video player"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                      allowFullScreen
                    />
                    <div className="p-2 bg-slate-800 text-white text-sm flex items-center justify-between">
                      <span>
                        📹 {sourceVideoId} @ {Math.floor((sourceTimestamp || 0) / 60)}:{String(Math.floor((sourceTimestamp || 0) % 60)).padStart(2, '0')}
                      </span>
                      <a
                        href={`https://www.youtube.com/watch?v=${sourceVideoId}&t=${Math.floor(sourceTimestamp || 0)}s`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 underline"
                      >
                        Open in YouTube →
                      </a>
                    </div>
                  </div>
                ) : sourceFile ? (
                  <MarkdownViewer 
                    sourceFile={sourceFile}
                    scrollToAnchor={sourceAnchor}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-slate-50 rounded-lg border-2 border-dashed border-slate-300">
                    <div className="text-center p-8">
                      <div className="text-4xl mb-4">📚</div>
                      <h3 className="text-lg font-semibold mb-2">No Source Selected</h3>
                      <p className="text-slate-600">
                        Click <span className="text-blue-500 font-medium">"View in context →"</span> on any source below the assistant's messages to view it here.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Learning objectives reference - collapsible on mobile */}
        {conceptData.learning_objectives && (
          <details 
            className="text-xs text-slate-500 pt-2 border-t md:open"
            open={objectivesExpanded}
            onToggle={(e) => setObjectivesExpanded((e.target as HTMLDetailsElement).open)}
          >
            <summary className="cursor-pointer font-semibold mb-1 md:cursor-default md:mb-0">
              <span className="md:hidden">📋 Objectives</span>
              <span className="hidden md:inline">Objectives:</span>
            </summary>
            <div className="mt-1 md:mt-0 md:inline">
              <span className="hidden md:inline"> </span>
              {conceptData.learning_objectives.join(' • ')}
            </div>
          </details>
        )}
      </DialogContent>
    </Dialog>
  );
}
