" Title:        Chatdocu Plugin
" Description:  A plugin to provide answers to user's questions using knowledge extract from chatdocu topics.
" Last Change:  01/21/2024
" Maintainer:   Song Luo <https://github.com/sluosapher>

" Prevents the plugin from being loaded multiple times. If the loaded
" variable exists, do nothing more. Otherwise, assign the loaded
" variable and continue running this instance of the plugin.
if exists("g:loaded_chatdocu")
    finish
endif
let g:loaded_chatdocu = 1

" Exposes the plugin's functions for use as commands in Vim.
command! -nargs=+ Ask call chatdocu#Ask(<f-args>)
command! Hello call chatdocu#PrintHello()
command! Updatedocs call chatdocu#UpdateDocs()
