local M = {}

-- Configuration
M.config = {
  openai_api_key = nil, -- Must be set via setup(opts)
  openai_base_url = "https://api.openai.com/v1",
  model = "gpt-4o",
  max_tokens = 2000,
  temperature = 0.7,
}

---@param opts table
function M.setup(opts)
    M.config = vim.tbl_deep_extend("force", M.config, opts or {})

  -- No environment variable checking here. All config values must be passed via opts.

  -- Create commands
  vim.api.nvim_create_user_command("VimAssistAsk", function()
    M.ask()
  end, { desc = "Ask a question about the current buffer" })

  vim.api.nvim_create_user_command("VimAssistRevise", function()
    M.revise()
  end, { range = true, desc = "Revise selected text with context" })

  -- Set up keymaps (optional - users can customize in their config)
  vim.keymap.set("n", "<leader>a", ":VimAssistAsk<CR>", { desc = "VimAssist: Ask question" })
  vim.keymap.set("n", "<leader>r", ":VimAssistRevise<CR>", { desc = "VimAssist: Revise selection" })
  vim.keymap.set("v", "<leader>a", ":VimAssistAsk<CR>", { desc = "VimAssist: Ask about selection" })
  vim.keymap.set("v", "<leader>r", ":VimAssistRevise<CR>", { desc = "VimAssist: Revise selection" })
end

---Get the full content of the current buffer
---@return string
local function get_buffer_content()
  return table.concat(vim.api.nvim_buf_get_lines(0, 0, -1, false), "\n")
end

---Get the currently selected text
---@return string
local function get_selected_text()
  local start_pos = vim.fn.getpos("'<")
  local end_pos = vim.fn.getpos("'>")
  local start_line = start_pos[2] - 1
  local start_col = start_pos[3] - 1
  local end_line = end_pos[2] - 1
  local end_col = end_pos[3] - 1

  local lines = vim.api.nvim_buf_get_lines(0, start_line, end_line + 1, false)

  if #lines == 0 then
    return ""
  end

  if #lines == 1 then
    return string.sub(lines[1], start_col + 1, end_col)
  end

  -- Multi-line selection
  lines[1] = string.sub(lines[1], start_col + 1)
  lines[#lines] = string.sub(lines[#lines], 1, end_col)

  return table.concat(lines, "\n")
end

---Get text before the cursor position
---@return string
local function get_text_before_cursor()
  local current_line = vim.fn.line(".") - 1
  local current_col = vim.fn.col(".") - 1
  local lines = vim.api.nvim_buf_get_lines(0, 0, current_line + 1, false)

  if #lines == 0 then
    return ""
  end

  -- For the last line, only get text up to cursor
  lines[#lines] = string.sub(lines[#lines], 1, current_col)

  return table.concat(lines, "\n")
end

---Get text after the cursor position
---@return string
local function get_text_after_cursor()
  local current_line = vim.fn.line(".") - 1
  local current_col = vim.fn.col(".")
  local total_lines = vim.api.nvim_buf_line_count(0)
  local lines = vim.api.nvim_buf_get_lines(0, current_line, total_lines, false)

  if #lines == 0 then
    return ""
  end

  -- For the first line, only get text after cursor position
  lines[1] = string.sub(lines[1], current_col + 1)

  return table.concat(lines, "\n")
end

---Get the line number of the end of the current paragraph
---@return number
local function get_end_of_paragraph()
  local current_line = vim.fn.line(".") - 1
  local total_lines = vim.api.nvim_buf_line_count(0)
  local lines = vim.api.nvim_buf_get_lines(0, current_line, total_lines, false)

  -- Find the next empty line or end of buffer
  for i = 1, #lines do
    if lines[i] == "" then
      return current_line + i - 1
    end
  end

  -- Return end of buffer if no empty line found
  return total_lines
end

local openai = require("vimassist.openai")

---@param messages table
---@param on_success function
---@param on_error function
local function openai_request_sync(messages, on_success, on_error)
  local status, response = openai.openai_request(
    messages,
    M.config.openai_api_key,
    M.config.model,
    M.config.max_tokens,
    M.config.temperature
  )

  if status ~= 200 then
    if on_error then on_error("API Error: " .. (response or "Unknown error")) end
    return
  end

  if on_success then
    on_success(response)
  end
end

---Ask a question about the current buffer
function M.ask()
  if not M.config.openai_api_key then
    vim.notify("OpenAI API key not set", vim.log.levels.ERROR)
    return
  end

  local question = vim.fn.input("Question: ")
  if question == "" then
    vim.notify("Question cannot be empty", vim.log.levels.WARN)
    return
  end

  local buffer_content = get_buffer_content()
  if buffer_content == "" then
    vim.notify("Buffer is empty", vim.log.levels.WARN)
    return
  end

  local messages = {
    {
      role = "system",
      content = "You are an AI assistant that answers questions about the given document. Be concise and helpful."
    },
    {
      role = "user",
      content = string.format("Document:\n\n%s\n\nQuestion: %s", buffer_content, question)
    }
  }

  vim.notify("Thinking...", vim.log.levels.INFO)

  local status, result = openai.openai_request(
    messages,
    M.config.openai_api_key,
    M.config.openai_base_url,
    M.config.model,
    M.config.max_tokens,
    M.config.temperature
  )

  if status ~= 200 then
    vim.notify("API Error: " .. (result or "Unknown error"), vim.log.levels.ERROR)
    return
  end

  local answer = result.choices[1].message.content
  local lines = vim.split(answer, "\n")

  -- Calculate insertion point (end of current paragraph)
  local end_line = get_end_of_paragraph()

  -- Insert answer after the paragraph
  vim.api.nvim_buf_set_lines(0, end_line, end_line, false, lines)

  -- Select the inserted text
  local start_line = end_line + 1
  local end_line_num = end_line + #lines

  -- Enter visual mode and select the inserted text
  vim.fn.setpos("'<", {0, start_line, 1, 0})
  vim.fn.setpos("'>", {0, end_line_num, #lines[#lines] or 0, 0})

  vim.notify("Answer inserted", vim.log.levels.INFO)
end

---Revise the selected text with context
function M.revise()
  if not M.config.openai_api_key then
    vim.notify("OpenAI API key not set", vim.log.levels.ERROR)
    return
  end

  local selected_text = get_selected_text()
  if selected_text == "" then
    vim.notify("No text selected", vim.log.levels.WARN)
    return
  end

  local request = vim.fn.input("Revision request: ")
  if request == "" then
    -- Use selected text as request if user input is empty
    request = selected_text
  end

  local text_before = get_text_before_cursor()
  local text_after = get_text_after_cursor()

  local messages = {
    {
      role = "system",
      content = "You are a writing assistant that helps revise text. Consider the context before and after the selected text. Only return the revised text, no explanations."
    },
    {
      role = "user",
      content = string.format(
        "Context before selection:\n%s\n\nSelected text:\n%s\n\nContext after selection:\n%s\n\nRevision request: %s",
        text_before,
        selected_text,
        text_after,
        request
      )
    }
  }

  vim.notify("Revising text...", vim.log.levels.INFO)

  local status, result = openai.openai_request(
    messages,
    M.config.openai_api_key,
    M.config.openai_base_url,
    M.config.model,
    M.config.max_tokens,
    M.config.temperature
  )

  if status ~= 200 then
    vim.notify("API Error: " .. (result or "Unknown error"), vim.log.levels.ERROR)
    return
  end

  local revised_text = result.choices[1].message.content
  local lines = vim.split(revised_text, "\n")

  -- Get selection boundaries
  local start_pos = vim.fn.getpos("'<")
  local end_pos = vim.fn.getpos("'>")
  local end_line = end_pos[2]

  -- Replace selection with revised text
  vim.api.nvim_buf_set_lines(0, start_pos[2] - 1, end_pos[2], false, lines)

  -- Select the revised text
  local start_line = start_pos[2]
  local end_line = start_pos[2] + #lines - 1

  vim.fn.setpos("'<", {0, start_line, 1, 0})
  vim.fn.setpos("'>", {0, end_line, #lines[#lines] or 0, 0})

  vim.notify("Text revised", vim.log.levels.INFO)
end

return M
