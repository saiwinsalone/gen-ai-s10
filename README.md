<<<<<<< HEAD
# Gemini CLI

This project reads `GEMINI_API_KEY` from `.env` and sends a prompt to the Gemini API.

Run it in PowerShell:

```powershell
.\.venv\Scripts\python.exe main.py "Explain machine learning simply"
```

Or run `main.py` without an argument to enter a prompt interactively.

The default model is `gemini-flash-lite-latest`, an alias that follows the latest
Flash Lite release. To use a different available model:

```powershell
.\.venv\Scripts\python.exe main.py --model gemini-3.1-pro-preview "Write a haiku about code"
```

Keep `.env` private; it is already ignored by Git.
=======
# gen-ai-s10
>>>>>>> d12938df0886d2299c30772cbe02b1038f78c776
