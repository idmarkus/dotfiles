;; Movement keys
(global-set-key "\M-j" 'next-line)
(global-set-key "\M-k" 'previous-line)
(global-set-key "\M-l" 'forward-char)
(global-set-key "\M-h" 'backward-char)

;; (global-set-key "\C-j" 'forward-paragraph)
;; (global-set-key "\C-k" 'backward-paragraph)
(global-set-key "\C-l" 'forward-word)
(global-set-key "\C-h" 'backward-word)

;; (global-set-key "\M-w" 'move-end-of-line)
;; (global-set-key "\M-q" 'move-beginning-of-line)
(global-set-key "\C-j" 'end-of-buffer)
(global-set-key "\C-k" 'beginning-of-buffer)

(defun jump-to-mark ()
  (interactive)
  (goto-char (mark-marker)))
(global-set-key "\C-p" 'jump-to-mark)
;; (global-set-key "\C-p" 'pop-to-mark-command)


;; Not movement keys?
(global-set-key "\M-c" 'recenter)

(global-set-key [backspace] 'hungry-backward-delete-char)
(global-set-key [C-backspace] 'hungry-backward-kill-word)

(global-set-key "\C-f" 'isearch-forward)
(global-set-key "\C-s" 'save-buffer)
(global-set-key "\M-o" 'find-file)
(global-set-key "\C-u" 'undo-only)
(global-set-key (kbd "C-S-u") 'undo-redo)

(global-set-key "\C-z" 'undo-only)
(global-set-key (kbd "C-S-z") 'undo-redo)

(global-set-key "\M-u" 'universal-argument)

(global-set-key "\M- " 'set-mark-command)

(global-set-key "\M-1" 'delete-other-windows)
(global-set-key "\M-2" 'split-window-below)
(global-set-key "\M-3" 'split-window-right)

(global-set-key "\C-o" 'other-window)

(global-set-key "\M-w" 'kill-ring-save)


(global-set-key "\M-/" 'toggle-comment-on-line-if-not-at-end-of-line-and-no-active-region-else-comment-dwim)
;; (global-set-key "\M-/" 'comment-dwim)

(define-key isearch-mode-map (kbd "C-f") 'isearch-repeat-forward)

(provide 'keys)
