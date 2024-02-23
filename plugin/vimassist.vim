" Title:        VimAssist Plugin
" Description:  A plugin to provide answers to user's questions using user's own documents.
" Last Change:  02/02/2024
" Maintainer:   Song Luo <https://github.com/sluosapher>

" Prevents the plugin from being loaded multiple times. If the loaded
" variable exists, do nothing more. Otherwise, assign the loaded
" variable and continue running this instance of the plugin.
if exists("g:loaded_vimassist")
    finish
endif
let g:loaded_vimassist = 1

" Exposes the plugin's functions for use as commands in Vim.
command! Ask call vimassist#Ask() " Ask the user a question.
command! Updatedocs call vimassit#UpdateDocs() " Update the plugin's knowledge base.
command! Showdocs call vimassist#ShowDocs() " Display the plugin's document file names in its knowledge base.
" command! Hello call vimassist#PrintHello()

" testing
command! ShowSelection call vimassist#GetSelection() " Display the selected text.

command! TopText call vimassist#GetTextAtTop() " Display the text before the selected text.

command! BottomText call vimassist#GetTextAtBottom() " Display the text after the selected text.


