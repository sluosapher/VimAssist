local M = {}

---Make a synchronous request to OpenAI API using plenary.nvim
---@param messages table
---@param api_key string
---@param base_url string
---@param model string
---@param max_tokens number
---@param temperature number
---@return number status_code
---@return table|nil result
function M.openai_request(messages, api_key, base_url, model, max_tokens, temperature)
  local curl = require("plenary.curl")
  local job = require("plenary.job")

  local payload = {
    model = model,
    messages = messages,
    max_tokens = max_tokens,
    temperature = temperature,
  }

  local json_encoded = vim.json.encode(payload)

  local result = nil
  local status_code = 0

  -- Construct the full URL from base URL and endpoint
  local url = base_url .. "/chat/completions"

  -- Debug output
  vim.notify("OpenAI URL: " .. url, vim.log.levels.INFO)
  vim.notify("OpenAI Model: " .. model, vim.log.levels.INFO)

  local response = curl.post(url, {
    headers = {
      ["Content-Type"] = "application/json",
      ["Authorization"] = "Bearer " .. api_key,
    },
    body = vim.json.encode(payload),
  })

  if response.status ~= 200 then
    return response.status, nil
  end

  local decoded = vim.json.decode(response.body)
  return response.status, decoded
end

return M
