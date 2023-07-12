(defun sudo-edit (&optional arg)
  "Edit currently visited file as root.

With a prefix ARG prompt for a file to visit.
Will also prompt for a file to visit if current
buffer is not visiting a file."
  (interactive "P")
  (if (or arg (not buffer-file-name))
      (find-file (concat "/sudo:root@localhost:"
                         (ido-read-file-name "Find file(as root): ")))
    (find-alternate-file (concat "/sudo:root@localhost:" buffer-file-name))))


(defun toggle-comment-on-line ()
  "comment or uncomment current line"
  (interactive)
  (comment-or-uncomment-region (line-beginning-position) (line-end-position)))

(defun toggle-comment-on-line-if-not-at-end-of-line-and-no-active-region-else-comment-dwim (arg)
  (interactive "P")
  (if (not (or (use-region-p)
               (looking-at "[? ?\t]*\n")))
      (toggle-comment-on-line)
    (comment-dwim arg)))

(defun smart-beginning-of-line ()
  "Move point to first non-whitespace character or beginning-of-line.

Move point to the first non-whitespace character on this line.
If point was already at that position, move point to beginning of line."
  (interactive)
  (let ((oldpos (point)))
    (back-to-indentation)
    (and (= oldpos (point))
         (beginning-of-line))))
(global-set-key "\C-a" 'smart-beginning-of-line)


(defun newline-below ()
  (interactive)
  (end-of-line)
  (newline))
(global-set-key [(shift return)] 'newline-below)


(defun rename-file-and-buffer (new-name)
  "Renames both current buffer and file it's visiting to NEW-NAME."
  (interactive "sNew name: ")
  (let ((name (buffer-name))
 (filename (buffer-file-name)))
    (if (not filename)
 (message "Buffer '%s' is not visiting a file!" name)
      (if (get-buffer new-name)
   (message "A buffer named '%s' already exists!" new-name)
 (progn
   (rename-file name new-name 1)
   (rename-buffer new-name)
   (set-visited-file-name new-name)
   (set-buffer-modified-p nil))))))

(defun shell-command-on-buffer ()
  "Asks for a command and executes it in inferior shell with current buffer
as input."
  (interactive)
  (shell-command-on-region
   (point-min) (point-max)
   (read-shell-command "Shell command on buffer: ")
   t
   t))
(global-set-key (kbd "M-\"") 'shell-command-on-buffer)

;;(defun blockfmt-buffer ()
;;  "Asks for a command and executes it in inferior shell with current buffer
;;as input."
;;  (interactive)
;;  (shell-command-on-region
;;   (point-min) (point-max)
;;   (concat (getenv "HOME") "/bin/blockfmt")
;;   t
;;   t))
;;(global-set-key (kbd "M-\\") 'blockfmt-buffer)


;(defun backward-kill-word-or-delete-ws-or-symbols-except-delimiters ()
  ;(while (not (looking-back "[({\[a-zA-Z0-9]"))
    ;(delete-char -1)))

;; We want this to:
;;  if we are looking back at ?\n
;;  then delete all whitespace backwards until we are looking at [anything]\n\n (i.e. so that we are on the first empty line)
;;  else delete all whitespace backwards until we hit a ?\n
(defun backward-delete-ws-iter (&optional newline_disable)
  (let
      ((no_ws nil)
       (newline_count (if newline_disable -1 0)))
    (if (eq (char-before) ?\n)
        (while (or (eq (char-before) ? ) ; then
                   (eq (char-before) ?\n)
                   (eq (char-before) ?\t)
                   (eq (char-before) ?\r))
          ;;(message "dc-1")
          (if (and (>= newline_count 0)(eq (char-before) ?\n))
              (setq newline_count (+ newline_count 1)))
          (setq no_ws t)
          (delete-char -1))
      (while (or (eq (char-before) ? ) ; else
                 (eq (char-before) ?\t)
                 (eq (char-before) ?\r))
        ;;(message "dc-1")
        (setq no_ws t)
        (delete-char -1)))
    (if (> newline_count 1)
        (insert ?\n))
    no_ws))

;; (defun is-matching-pair ()
;;   (or (and (eq (char-before) ?\() (eq (char-after) ?\)))
;;       (and (eq (char-before) ?\<) (eq (char-after) ?\>))
;;       (and (eq (char-before) ?\{) (eq (char-after) ?\}))
;;       (and (eq (char-before) ?\[) (eq (char-after) ?\]))
;;       (and (eq (char-before) ?\") (eq (char-after) ?\"))
;;       (and (eq (char-before) ?\') (eq (char-after) ?\'))))


;; (defun pair-opposite-from-closing (str)
;;   (let ((char (string-to-char str)))
;;     (cond ((eq char ?\)) ?\()
;;           ((eq char ?>) ?<)
;;           ((eq char ?}) ?{)
;;           ((eq char ?\]) ?\[)
;;           (t char))))

;; (defun electric-pair-regexp-match ()
;;   (and (looking-at "[ \n\r\t]*\\([])}\"'>]\\)") ;; [:space:]*([])}"'])
;;        (eq (char-before) (pair-opposite-from-closing (match-string 1)))))
;;       ;; (message "%S" (match-string 1))))

(defun char-before-pair-opener ()
  (cond ((eq (char-before) ?\() "[ \n\r\t]*)")
        ((eq (char-before) ?<) "[ \n\r\t]*>")
        ((eq (char-before) ?{) "[ \n\r\t]*}")
        ((eq (char-before) ?\[) "[ \n\r\t]*]")
        ((eq (char-before) ?\") "[ \n\r\t]*\"")
        ((eq (char-before) ?') "[ \n\r\t]*'")
        (t "^+")))                      ; this will never match

(defun delete-char-and-if-electric-pair-delete-forward-with-whitespace (n)
  (if (looking-at (char-before-pair-opener))
      (replace-match "" nil nil))
  (delete-char n))

(defun hungry-backward-delete-char ()
  (interactive)
  (if (not (backward-delete-ws-iter))
      (delete-char-and-if-electric-pair-delete-forward-with-whitespace -1)
      ;; (delete-char -1)
    t))

(defun hungry-backward-kill-word ()
  (interactive)
  (if (eq (char-before) ? ) (delete-char -1))
  (if (not (backward-delete-ws-iter t))
      (backward-kill-word 1)
    t))

(defun forward-move-word (&optional pattern-construct-str-addition)
  (interactive)
  (let ((word-pattern (concat "[a-zA-Z0-9\n" pattern-construct-str-addition "]")))
  (if (looking-at word-pattern)
      (while (looking-at word-pattern)
        (forward-char))
    (while (not (looking-at word-pattern))
      (forward-char)))))

(defun backward-delete-char-selective (chars-to-delete)
  (let ((deleted nil))
    (while (looking-back (concat "[" chars-to-delete "]"))
      (delete-char -1)
      (setq deleted t))
    deleted))

(defun smart-backward-kill-word ()
  (interactive)
  (let (oldpos (point))
    ))

(provide 'funcs)
