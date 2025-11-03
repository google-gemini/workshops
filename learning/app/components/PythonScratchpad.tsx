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

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

type PythonScratchpadProps = {
  starterCode?: string;
  onExecute?: (code: string, output: string, error: string | null) => void;
  onCodeChange?: (code: string) => void;
};

export default function PythonScratchpad({ 
  starterCode = '', 
  onExecute,
  onCodeChange
}: PythonScratchpadProps) {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const pyodideRef = useRef<any>(null);

  // Initialize Pyodide on mount
  useEffect(() => {
    async function loadPyodide() {
      try {
        // @ts-ignore - Pyodide loads from CDN
        const pyodide = await window.loadPyodide({
          indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
        });
        
        // Load commonly used packages for math/algorithms
        await pyodide.loadPackage(['numpy', 'micropip']);
        
        pyodideRef.current = pyodide;
        setIsLoading(false);
        console.log('✅ Pyodide loaded successfully');
      } catch (err) {
        console.error('Failed to load Pyodide:', err);
        setError('Failed to initialize Python environment');
        setIsLoading(false);
      }
    }

    loadPyodide();
  }, []);

  const runCode = async () => {
    if (!pyodideRef.current) {
      setError('Python environment not ready');
      return;
    }

    setIsRunning(true);
    setError(null);
    setOutput('');

    try {
      const pyodide = pyodideRef.current;
      
      // Capture stdout
      pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
      `);

      // Run user code
      await pyodide.runPythonAsync(code);

      // Get captured output
      const stdout = pyodide.runPython('sys.stdout.getvalue()');
      
      setOutput(stdout || '(no output)');
      onExecute?.(code, stdout, null);
      
    } catch (err: any) {
      const errorMsg = err.message || 'Execution error';
      setError(errorMsg);
      onExecute?.(code, '', errorMsg);
    } finally {
      setIsRunning(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl/Cmd + Enter to run
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runCode();
    }
    
    // Tab support in textarea
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.target as HTMLTextAreaElement;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      setCode(code.substring(0, start) + '    ' + code.substring(end));
      
      // Move cursor after inserted spaces
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }
  };

  return (
    <div className="flex flex-col h-full border rounded-lg bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b bg-slate-800 text-white rounded-t-lg">
        <span className="text-sm font-medium">🐍 Python Workspace</span>
        <div className="flex gap-2">
          <Button
            onClick={runCode}
            disabled={isLoading || isRunning}
            size="sm"
            className="bg-green-600 hover:bg-green-700"
          >
            {isRunning ? '⏳ Running...' : '▶️ Run (Ctrl+Enter)'}
          </Button>
          <Button
            onClick={() => {
              setCode(starterCode);
              setOutput('');
              setError(null);
            }}
            size="sm"
            variant="outline"
            className="text-slate-300 border-slate-600 hover:bg-slate-700"
          >
            🔄 Reset
          </Button>
        </div>
      </div>

      {/* Code editor */}
      <div className="flex-1 p-3">
        <Textarea
          value={code}
          onChange={(e) => {
            const newCode = e.target.value;
            // If current code is still the starter code and user is typing,
            // clear it and use only what they typed (like placeholder behavior)
            if (code === starterCode && newCode.length > code.length) {
              const typedChar = newCode.charAt(newCode.length - 1);
              setCode(typedChar);
              onCodeChange?.(typedChar);
            } else {
              setCode(newCode);
              onCodeChange?.(newCode);
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder={isLoading ? "Loading Python..." : starterCode}
          disabled={isLoading}
          className="font-mono text-sm h-full resize-none bg-white"
          style={{ minHeight: '200px' }}
        />
      </div>

      {/* Output area */}
      {(output || error) && (
        <div className="border-t p-3 bg-slate-900 text-white rounded-b-lg">
          <div className="text-xs font-medium mb-1 text-slate-400">OUTPUT:</div>
          {error ? (
            <pre className="text-xs text-red-400 font-mono whitespace-pre-wrap">{error}</pre>
          ) : (
            <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap">{output || '(no output)'}</pre>
          )}
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="border-t p-3 bg-yellow-50 text-yellow-800 text-sm">
          ⏳ Loading Python environment... (first time only, ~10-15 seconds)
        </div>
      )}
    </div>
  );
}
