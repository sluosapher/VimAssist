let s:source_dir = fnamemodify(expand('<sfile>:p'), ':h')
"echo s:source_dir

" define the Ask funcntion
function! chatdocu#Ask(...)
    let args = join(a:000, " ")
    let question = args

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
function! chatdocu#UpdateDocs()
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



function! chatdocu#PrintHello()
" define the PrintHello function
echo "PrintHello function called"
echo s:script_dir

python3 << EOF
import sys
import vim  
# add script directory to the python path
current_dir = vim.eval('s:script_dir') # this should be the autoload directory
# print(f"current_dir: {current_dir}")
script_dir = current_dir+'/../scripts'
sys.path.insert(0, script_dir)

print(f"sys path: {sys.path}")

# call the python function
#import plugin_test
#plugin_test.print_hello()

EOF
endfunction






