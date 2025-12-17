# VimAssist

VimAssist is a Neovim plugin that provides AI-powered writing assistance using OpenAI's GPT models. It helps you write better by answering questions about your content and revising selected text with contextual awareness.

## Features

- **Ask**: Ask questions about the current buffer content and get AI-generated answers
- **Revise**: Select text and ask the AI to revise it, considering context before and after the selection
- **Context-aware**: The AI understands the full context of your document
- **Lazy.nvim integration**: Easy installation and configuration

## Installation

Using [lazy.nvim](https://github.com/folke/lazy.nvim):

```lua
{
  "sluosapher/VimAssist",
  dependencies = {
    "nvim-lua/plenary.nvim",
  },
  config = function()
    require("vimassist").setup({
      -- Optional: Set your OpenAI API key here or use environment variable OPENAI_API_KEY
      openai_api_key = vim.env.OPENAI_API_KEY or "your-api-key",

      -- Optional: Customize model (default: gpt-4o)
      model = "gpt-4o",

      -- Optional: Customize generation parameters
      max_tokens = 2000,
      temperature = 0.7,
    })
  end,
  keys = {
    { "<leader>a", ":VimAssistAsk<CR>", mode = { "n", "v" }, desc = "VimAssist: Ask question" },
    { "<leader>r", ":VimAssistRevise<CR>", mode = { "n", "v" }, desc = "VimAssist: Revise selection" },
  },
}
```

## Requirements

- Neovim >= 0.8.0
- plenary.nvim
- OpenAI API key (set via `OPENAI_API_KEY` environment variable or in config)

## Usage

### Commands

- `:VimAssistAsk` - Ask a question about the current buffer
- `:VimAssistRevise` - Revise selected text with context

### Keymaps (Default)

- `<leader>a` - Ask a question (works in normal and visual mode)
- `<leader>r` - Revise selected text (works in normal and visual mode)

### Example Usage

1. **Ask a question about your text**:
   - Place cursor where you want the answer inserted
   - Press `<leader>a` or run `:VimAssistAsk`
   - Type your question (e.g., "What are the main points of this document?")
   - The answer will be inserted at the cursor position

2. **Revise selected text**:
   - Select text in visual mode
   - Press `<leader>r` or run `:VimAssistRevise`
   - Type your revision request (e.g., "Make this more concise")
   - The selected text will be replaced with the revised version

### Custom Configuration Example

```lua
{
  "sluosapher/VimAssist",
  dependencies = {
    "nvim-lua/plenary.nvim",
  },
  opts = {
    openai_api_key = vim.env.OPENAI_API_KEY,
    model = "gpt-4-turbo",  -- Use a specific model
    max_tokens = 3000,       -- Allow longer responses
    temperature = 0.5,       -- Make responses more focused
  },
  keys = {
    { "<leader>qa", ":VimAssistAsk<CR>", mode = { "n", "v" }, desc = "Ask about content" },
    { "<leader>qr", ":VimAssistRevise<CR>", mode = { "n", "v" }, desc = "Revise selected text" },
  },
}
```

## API

### `setup(opts)`

Configure the plugin with the following options:

- `openai_api_key` (string) - Your OpenAI API key
- `model` (string) - Model to use (default: `"gpt-4o"`)
- `max_tokens` (number) - Maximum tokens in response (default: 2000)
- `temperature` (number) - Randomness of output (default: 0.7)

### `ask()`

Ask a question about the current buffer content. The answer is inserted at the cursor position.

### `revise()`

Revise the selected text with context-aware suggestions. Only works in visual mode.

## Development

### Project Structure

```
VimAssist/
├── lua/
│   └── vimassist/
│       ├── init.lua          # Main plugin module
│       └── openai.lua        # OpenAI API wrapper
├── plugin/
│   └── vimassist.lua         # Plugin entry point
└── README.md
```

### Key Functions

The plugin is built with a modular architecture:

- **`init.lua`**: Main plugin module with setup, configuration, and command handlers
- **`openai.lua`**: OpenAI API wrapper using plenary.nvim's curl module

## Troubleshooting

### OpenAI API Key Not Set

If you get an error about the API key, make sure to:
1. Set the `OPENAI_API_KEY` environment variable, or
2. Pass the key in the config: `openai_api_key = "your-key"`

### API Errors

- Check your API key is valid
- Verify you have enough credits in your OpenAI account
- Check your internet connection

### Buffer Issues

- Make sure you're in a writable buffer
- For `:VimAssistRevise`, ensure you've made a visual selection first

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Changelog

### v1.0.0 (Current)
- Rewrote from Python/VimL to pure Lua
- Removed file upload and document management features
- Simplified to focus on current buffer content
- Added Lazy.nvim support
- Uses plenary.nvim for API calls
