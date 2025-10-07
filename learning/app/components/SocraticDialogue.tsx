'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type SocraticDialogueProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  conceptData: any;
};

export default function SocraticDialogue({
  open,
  onOpenChange,
  conceptData,
}: SocraticDialogueProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start dialogue');
      }

      const data = await response.json();
      setMessages([{ role: 'assistant', content: data.message }]);
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

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      // Convert to OpenAI format
      const conversationHistory = updatedMessages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch('/api/socratic-dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conceptId: conceptData.id,
          conversationHistory,
          conceptData,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setMessages([...updatedMessages, { role: 'assistant', content: data.message }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
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

  if (!conceptData) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Learning: {conceptData.name}</DialogTitle>
          <DialogDescription>{conceptData.description}</DialogDescription>
        </DialogHeader>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto space-y-4 py-4 px-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-100 text-slate-900'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
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

        {/* Input area */}
        <div className="flex gap-2 pt-4 border-t">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your response... (Enter to send, Shift+Enter for new line)"
            className="flex-1 min-h-[60px] max-h-[120px]"
            disabled={isLoading}
          />
          <Button onClick={sendMessage} disabled={isLoading || !input.trim()}>
            Send
          </Button>
        </div>

        {/* Learning objectives reference */}
        {conceptData.learning_objectives && (
          <div className="text-xs text-slate-500 pt-2 border-t">
            <strong>Objectives:</strong>{' '}
            {conceptData.learning_objectives.join(' • ')}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
