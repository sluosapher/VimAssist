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
command! Ask call vimassist#Ask()
command! Updatedocs call vimassit#UpdateDocs()
" command! Hello call vimassist#PrintHello()
