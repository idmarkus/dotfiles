; C++ indentation style
(defconst base-c-style
  '((c-electric-pound-behavior   . 'alignleft)
    (c-tab-always-indent         . t)
    (c-comment-only-line-offset  . 0)
    (c-hanging-braces-alist      . ((class-open)
                                    (class-close)
                                    (defun-open)
                                    (defun-close)
                                    (inline-open)
                                    (inline-close)
                                    (brace-list-open)
                                    (brace-list-close)
                                    (brace-list-intro)
                                    (brace-list-entry)
                                    (block-open)
                                    (block-close)
                                    (substatement-open)
                                    (statement-case-open)
                                    (class-open)))
    (c-hanging-colons-alist      . ((inher-intro)
                                    (case-label)
                                    (label)
                                    (access-label)
                                    (access-key)
                                    (member-init-intro)))
    (c-cleanup-list              . (scope-operator
                                    list-close-comma
                                    defun-close-semi))
    (c-offsets-alist             . ((arglist-close         .  c-lineup-arglist)
                                    (label                 . -4)
                                    (access-label          . -4)
                                    (substatement-open     .  0)
                                    (statement-case-intro  .  4)
                                    (statement-block-intro .  c-lineup-for)
                                    (case-label            .  4)
                                    (block-open            .  0)
                                    (inline-open           .  0)
                                    (topmost-intro-cont    .  0)
                                    (knr-argdecl-intro     . -4)
                                    (brace-list-open       .  0)
                                    (brace-list-intro      .  4)))
    (c-echo-syntactic-information-p . nil))
    "Base C/C++ Style")

;; Functions

(defun my-electric-brace ()
  (interactive)
  (insert "{")
  (let ((pps (syntax-ppss)))
    (when (and (eolp) (not (or (nth 3 pps) (nth 4 pps)))) ;; EOL and not in string or comment
      (c-indent-line)
      (insert "\n\n}")
      (c-indent-line)
      (forward-line -1)
      (c-indent-line))))

(defun delete-block ()
  (search-backward "{")
  (zap-to-char 1 ?}))

(defun delete-block-or-hungry-backward-char ()
  (interactive)
  (if (and (looking-at "[\n[:space:]]*}")
           (looking-back "{[\n[:space:]]*"))
      (delete-block)           ; then
    (hungry-backward-delete-char))) ; else

(defun insert-block-or-normal-brace ()
  (interactive)
  (if (looking-back "\n[? ?\t]*")
      (my-electric-brace)
    (c-electric-brace 1))) 

;; (defun smart-backward-c-block ()
;;   (interactive)
;;   (if (looking-back "{[:space:]*")
;;       ((while (not (or (looking-back "}")
;;                        (looking-back "\n\n")))
;;          (backward-char 1))
;;        (if (looking-back "\n[:space:]*}")
;;            ((forward-line -1)
;;             (back-to-indentation))))
;;     ) 

;; Hook

(defun c-common-hook-setup ()

  ;; Set style for buffer
  (c-add-style "Base" base-c-style t)
  ;; 4-space tabs
  (setq tab-width 4 indent-tabs-mode nil)

  (c-set-offset 'member-init-intro '++)

  ;; Hungry delete
  ;;(c-toggle-auto-hungry-state 1)
  
  ;;(define-key c-mode-base-map "{" 'my-electric-brace)
  (define-key c-mode-base-map "{" 'insert-block-or-normal-brace)
  (define-key c-mode-base-map [backspace] 'delete-block-or-hungry-backward-char)
  (define-key c-mode-base-map [C-backspace] 'hungry-backward-kill-word)

  (define-key c-mode-base-map (kbd "C-c o") 'ff-find-other-file)

  ;; No semi-colon indent
  (setq c-hanging-semi&comma-criteria '((lambda () 'stop))))

(add-hook 'c-mode-common-hook 'c-common-hook-setup)
