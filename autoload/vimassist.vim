let s:source_dir = fnamemodify(expand('<sfile>:p'), ':h')
"echo s:source_dir

" define the Ask funcntion
function! vimassist#Ask()
    let question = input('Please enter your question: ')

python3 << EOF
import vim
import os

# add script directory to the python path
source_dir = vim.eval('s:source_dir') # this should be the autoload directory
script_dir = os.path.join(source_dir, '../scripts')
sys.path.insert(0, script_dir)
# print(f"sys path: {sys.path}")

import command_functions as cf
from utilities import config_file_name

question = vim.eval('question')
if question == "":
    print("Question is empty.")
else:

    answer = cf.send_message_to_assistant(question, config_dir=script_dir)

    cursor = vim.current.window.cursor
    answer_lines = answer.split('\n')

    # Start appending from the first line of the answer
    for i, line in enumerate(answer_lines):
        vim.current.buffer.append(line, cursor[0] + i)

    end_line = cursor[0] + len(answer_lines)
    vim.command('normal! ' + str(cursor[0]) + 'GV' + str(end_line) + 'G')
    vim.current.window.cursor = (end_line, len(answer_lines[-1]))
EOF
endfunction

" define the UpdateDocs function
function! vimassist#UpdateDocs()
" get the full directory path of the current file, using vimscript
let s:doc_dir = expand('%:p:h')

" confirm with the user that they want to use this directory to update the documentation; provide yes, no, cancel options
let confirm = confirm("Do you want to use the directory ".s:doc_dir." to update the documentation?", "&Yes\n&No\n&Cancel")

if confirm == 1 " yes
    " keep the script directory, do nothing
elseif confirm == 2 " no
    " ask the user to provide the directory to use
    let s:doc_dir = input("Please provide the directory to use: ")
elseif confirm == 3 " cancel
    " do nothing
    return
endif

" the path of plugin's autoload folder
" let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

" call python function to update the documents in the script directory
python3 << EOF
import vim
import os
# add script directory to the python path
source_dir = vim.eval('s:source_dir')
script_dir = os.path.join(source_dir, '../scripts')
# print(f"script_dir: {script_dir}")
sys.path.insert(0, script_dir)

import command_functions as cf

doc_dir = vim.eval('s:doc_dir')
print(f"doc_dir: {doc_dir}")
status = cf.update_docs(doc_dir, config_dir=script_dir)

if status == 0:
    print("Documentation updated successfully")
else:
    print("Documentation update failed")
EOF
endfunction

" define the ShowDocs function
function! vimassist#ShowDocs()
" call the python function to print the documentation
python3 << EOF
import vim
import os
# add script directory to the python path
source_dir = vim.eval('s:source_dir')
script_dir = os.path.join(source_dir, '../scripts')
sys.path.insert(0, script_dir)

import command_functions as cf
cf.print_all_file_names(config_dir=script_dir)
EOF
endfunction

" define a function to get the selected text in visual mode
function! vimassist#GetSelection()
    " Save the current cursor position
    let l:save_pos = getpos(".")
  
    " Get the start and end positions of the visual selection
    let l:start_pos = getpos("'<")
    let l:end_pos = getpos("'>")
  
    " Calculate the start and end lines and columns
    let l:start_line = l:start_pos[1]
    let l:end_line = l:end_pos[1]
    let l:start_col = l:start_pos[2]
    let l:end_col = l:end_pos[2]
  
    " Initialize variable to store the selected text
    let l:selected_text = ''
  
    " Check if selection is on the same line
    if l:start_line == l:end_line
      let l:selected_text = getline(l:start_line)[l:start_col - 1 : l:end_col - 1]
    else
      " Add the text from the first selected line
      let l:selected_text = getline(l:start_line)[l:start_col - 1 :]
  
      " Add the text from any lines fully within the selection
      for l:line_num in range(l:start_line + 1, l:end_line - 1)
        let l:selected_text .= "\n" . getline(l:line_num)
      endfor
  
      " Add the text from the last selected line
      if l:start_line < l:end_line
        let l:selected_text .= "\n" . getline(l:end_line)[:l:end_col - 1]
      endif
    endif
  
    " Restore the cursor position
    call setpos('.', l:save_pos)

    "echo "echo selected text: " . l:selected_text
  
    return l:selected_text

endfunction

" define a function to get the text before the cursor
function! vimassist#GetTextAtTop()
    " Initialize variable to store the text
    let l:text_before_cursor = ''
    
    " Determine the mode and set variables accordingly
    " let l:visual_mode = mode() ==# 'v' || mode() ==# 'V' || mode() ==# "\<C-V>"
    " let l:start_pos = l:visual_mode ? getpos("'<")[1:2] : getpos(".")[1:2]
    let l:start_pos = getpos(".")[1:2]
    
    " Extract positions
    let [l:start_line, l:start_col] = l:start_pos

    " echo "echo start line: " . l:start_line
    " echo "echo start col: " . l:start_col

    " Add the text from each line before the start line
    for l:line_num in range(1, l:start_line - 1)
        let l:text_before_cursor .= getline(l:line_num) . "\n"
    endfor
    
    " For the start line, add the text up to (but not including) the adjusted start column
    if l:start_col > 1
        let l:text_before_cursor .= getline(l:start_line)[:l:start_col - 2]
    endif " we do nothing is the start column is 1

    return l:text_before_cursor
endfunction
      

    
function! vimassist#GetTextAtBottom(mode)
    " Initialize variable to store the text
    let l:text_after_cursor = ''

    if a:mode == 'visual'
        let l:visual_mode = 1
        let l:end_pos = getpos("'>")[1:2]
    else
        let l:visual_mode = 0
        let l:end_pos = getpos(".")[1:2]
    endif
    
    " echo "echo visual mode: " . l:visual_mode

    " Extract positions
    let [l:end_line, l:end_col] = l:end_pos

    " echo "echo end line: " . l:end_line
    " echo "echo end col: " . l:end_col

    " Adjust end position to not include selected text or character under cursor
    " In visual mode, move start from next character; in normal mode, start from next character if not at end of line
    if l:visual_mode || (!l:visual_mode && l:end_col <= strlen(getline(l:end_line)))
        let l:end_col += 1
    endif

    " Handle case when adjustment moves beyond line length (only relevant for visual mode)
    if l:end_col > strlen(getline(l:end_line))
        let l:end_col = 1
        let l:end_line += 1
    endif

    " Add the text from the adjusted position
    if l:end_line <= line("$")
        if l:end_col <= strlen(getline(l:end_line))
            let l:text_after_cursor = getline(l:end_line)[l:end_col - 1:]
        endif
        " Add the text from each line after the adjusted end line
        for l:line_num in range(l:end_line + 1, line("$"))
            let l:text_after_cursor .= "\n" . getline(l:line_num)
        endfor
    endif

    return l:text_after_cursor
endfunction

" define a function to capture the user request, selected text, context, and send it to the revise_content function
function! vimassist#ReviseContent(mode)
" get the user request
let l:user_request = input("Please enter your request: ")

" get the selected text
let l:selected_text = vimassist#GetSelection()

" get the text before the cursor
let l:text_at_top = vimassist#GetTextAtTop()

" get the text after the cursor
let l:text_at_bottom = vimassist#GetTextAtBottom(a:mode)

" call the python function to revise the content
python3 << EOF
import vim
import os
import json
# add script directory to the python path
source_dir = vim.eval('s:source_dir')
script_dir = os.path.join(source_dir, '../scripts')
sys.path.insert(0, script_dir)

import command_functions as cf

user_request = vim.eval('l:user_request')
selected_text = vim.eval('l:selected_text')
text_at_top = vim.eval('l:text_at_top')
text_at_bottom = vim.eval('l:text_at_bottom')

# call revise_content function from command_functions
revised_text = cf.revise_content(
    config_dir = script_dir,
    selected_text = selected_text,
    text_at_top = text_at_top,
    text_at_bottom = text_at_bottom,
    user_request = user_request
)

revised_text_lines = revised_text.split('\n')

# Determine the mode and insert the text accordingly
mode = vim.eval('a:mode')
if mode == 'visual':
    # Visual mode: Find the end of the selection and insert text
    end_line = vim.eval("getpos(\"\'>\")[1]")
    end_line = int(end_line)  # Convert to integer
    vim.current.buffer.append(revised_text_lines, end_line)

    # Move cursor to start of inserted text and enter Visual mode to select it
    vim.command(f'normal! {end_line + 1}G')
    vim.command('normal! V')
    # Correctly calculate the end of the inserted text to extend the selection
    # Need to subtract one because 'j' command moves down an extra line
    if len(revised_text_lines) > 1:
        vim.command(f'normal! {len(revised_text_lines) - 1}j')
else:
    # Normal mode: Insert after the current line
    current_line = vim.eval('line(".")')
    current_line = int(current_line)  # Convert to integer
    vim.current.buffer.append(revised_text_lines, current_line)

    # Move cursor to start of inserted text and enter Visual mode to select it
    vim.command(f'normal! {current_line + 1}G')
    vim.command('normal! V')
    # Correctly calculate the end of the inserted text to extend the selection
    # Need to subtract one because 'j' command moves down an extra line
    if len(revised_text_lines) > 1:
        vim.command(f'normal! {len(revised_text_lines) - 1}j')

EOF

endfunction




    




