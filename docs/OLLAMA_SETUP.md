# Ollama Setup Guide

The Red Team Actor Simulator supports running local models via Ollama. This allows you to test AI safety using open-source models without API costs.

## Installation

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS
```bash
brew install ollama
```

### Windows
Download from: https://ollama.com/download

## Starting Ollama

```bash
ollama serve
```

This starts the Ollama server on `http://localhost:11434` (default).

## Installing Models

### Recommended Models for Red Team Testing

**Small/Fast Models:**
```bash
ollama pull llama3.2:3b
ollama pull phi3:mini
ollama pull gemma2:2b
```

**Medium Models (Balanced):**
```bash
ollama pull llama3.2:8b
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

**Large Models (Most Capable):**
```bash
ollama pull llama3.1:70b
ollama pull qwen2.5:32b
ollama pull mixtral:8x7b
```

**Specialized Models:**
```bash
ollama pull codellama:13b      # For coding scenarios
ollama pull llava:13b          # For vision tasks
```

## Configuration

The simulator is already configured to use Ollama at `http://localhost:11434`.

If you need to change the URL, update your `.env` file:
```bash
OLLAMA_BASE_URL=http://localhost:11434
```

## Using Ollama Models in the Simulator

1. Start Ollama: `ollama serve`
2. Pull a model: `ollama pull llama3.2`
3. Start the simulator: `./start.sh`
4. In the UI, select **Ollama (Local)** as the provider
5. Choose your model from the dropdown

## Checking Available Models

```bash
ollama list
```

## Performance Tips

- **GPU Acceleration**: Ollama automatically uses your GPU if available (CUDA/Metal)
- **Memory**: Larger models require more RAM (70B models need ~40GB)
- **Context Window**: Most models support 4K-8K tokens by default

## Model Selection for Red Team Testing

### For Actor (Adversarial Persona):
- **Recommended**: `llama3.1:70b`, `qwen2.5:32b`
- **Fast Alternative**: `llama3.2:8b`, `mistral:7b`

### For Subject (Model Being Tested):
- Any model you want to evaluate
- Can use the same or different model than Actor

### For Assessor:
- **Recommended**: `llama3.1:70b` (needs good reasoning)
- **Fast Alternative**: `qwen2.5:14b`

## Troubleshooting

### "Ollama not responding"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### "Model not found"
```bash
# List installed models
ollama list

# Pull the model
ollama pull <model-name>
```

### "Out of memory"
- Use smaller models (3B-8B parameter range)
- Close other applications
- Reduce context window in model settings

## Benefits of Local Models

✅ **No API Costs** - Run unlimited simulations
✅ **Privacy** - Data stays on your machine
✅ **Offline** - No internet required after downloading models
✅ **Customization** - Fine-tune models for specific scenarios
✅ **Speed** - Fast inference with GPU acceleration

## Links

- Ollama Website: https://ollama.com
- Ollama Models Library: https://ollama.com/library
- Ollama GitHub: https://github.com/ollama/ollama
