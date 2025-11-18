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

/**
 * Type declarations for browser globals loaded from CDN
 */

interface Window {
  // Pyodide - Python in the browser
  loadPyodide: (config?: { indexURL: string }) => Promise<unknown>;
  
  // JSCL - Common Lisp in the browser
  jscl?: {
    evaluateString: (code: string) => unknown;
  };
}
