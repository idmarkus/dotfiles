
(setq eshell-scroll-to-bottom-on-input t)

(defalias 'ff 'find-file)
;;(defalias 'up '(eshell/cd ..))

(defun eshell/up (&optional N)
  (unless N (setq N 1))
  (dotimes (i N)
    (eshell/cd "..")))

;(defalias 'ls (concat ls " -FAXh --group-directories-first --color=auto"))
;(add-hook 'eshell-mode-hook
;          (lambda ()
;            ;; The 'ls' executable requires the Gnu version on the Mac
;            ;(let ((ls (if (file-exists-p "/usr/local/bin/gls")
;            ;              "/usr/local/bin/gls"
;                                        ;            "/bin/ls")))
;            ;(let ((ls (eshell/ls))
;            (eshell/alias "ls" "/bin/ls -FAXh --group-directories-first")))
;
(defun eshell/d (&rest args)
  (dired (pop args) "."))

;(defun eshell/lsf (filename &optional dir)
;  "Searches in the current directory for files that match the
;given pattern. A simple wrapper around the standard 'find'
;function."
;  (let ((cmd (concat
;              "find " (or dir ".")
;              "      -not -path '*/.git*'"
;              " -and -not -path '*node_modules*'"
;              " -and -not -path '*classes*'"
;              " -and "
;              " -type f -and "
;              "-iname '" filename "'")))
;    (message cmd)
;    (shell-command-to-string cmd)))
;
(setq eshell-cmpl-cycle-completions nil
      eshell-save-history-on-exit t
      eshell-cmpl-dir-ignore "\\`\\(\\.\\.?\\|CVS\\|\\.svn\\|\\.git\\)/\\'")


;; Setup PROMPT
;(defun curr-dir-git-branch-string (pwd)
;  "Returns current git branch as a string, or the empty string if
;PWD is not in a git repo (or the git command is not found)."
;  (interactive)
;  (when (and (eshell-search-path "git")
;             (locate-dominating-file pwd ".git"))
;    (let ((git-output (shell-command-to-string (concat "cd " pwd " && git branch | grep '\\*' | sed -e 's/^\\* //'"))))
;      (if (> (length git-output) 0)
;          (concat " :" (substring git-output 0 -1))
;        "(no branch)"))))
;
;(defun pwd-replace-home (pwd)
;  "Replace home in PWD with tilde (~) character."
;  (interactive)
;  (let* ((home (expand-file-name (getenv "HOME")))
;         (home-len (length home)))
;    (if (and
;         (>= (length pwd) home-len)
;         (equal home (substring pwd 0 home-len)))
;        (concat "~" (substring pwd home-len))
;      pwd)))
;
;(defun pwd-shorten-dirs (pwd)
;  "Shorten all directory names in PWD except the last two."
;  (let ((p-lst (split-string pwd "/")))
;    (if (> (length p-lst) 2)
;        (concat
;         (mapconcat (lambda (elm) (if (zerop (length elm)) ""
;                               (substring elm 0 1)))
;                    (butlast p-lst 2)
;                    "/")
;         "/"
;         (mapconcat (lambda (elm) elm)
;                    (last p-lst 2)
;                    "/"))
;      pwd  ;; Otherwise, we just return the PWD
;      )))
;
;;; Turn off the default prompt.
;(setq eshell-highlight-prompt nil)
;
;(defun split-directory-prompt (directory)
;  (if (string-match-p ".*/.*" directory)
;      (list (file-name-directory directory) (file-name-base directory))
;    (list "" directory)))
;
;(setq eshell-prompt-function
;      (lambda ()
;        (let* ((directory (split-directory-prompt (pwd-shorten-dirs (pwd-replace-home (eshell/pwd)))))
;               (parent (car directory))
;               (name (cadr directory))
;               (branch (or (curr-dir-git-branch-string (eshell/pwd)) "")))
;
;          (if (eq 'dark (frame-parameter nil 'background-mode))
;              (concat   ;; Prompt for Dark Themes
;               (propertize parent 'face `(:foreground "#8888FF"))
;               (propertize name   'face `(:foreground "#8888FF" :weight bold))
;               (propertize branch 'face `(:foreground "green"))
;               (propertize " $"   'face `(:weight ultra-bold))
;               (propertize " "    'face `(:weight bold)))
;
;            (concat    ;; Prompt for Light Themes
;             (propertize parent 'face `(:foreground "blue"))
;             (propertize name   'face `(:foreground "blue" :weight bold))
;             (propertize branch 'face `(:foreground "dark green"))
;             (propertize " $"   'face `(:weight ultra-bold))
;             (propertize " "    'face `(:weight bold)))))))
;;; END Setup PROMPT

(defun eshell/x ()
  "Closes the EShell session and gets rid of the EShell window."
  (kill-buffer)
  (delete-window))

(defun eshell-here ()
  "Opens up a new shell in the directory associated with the
current buffer's file. The eshell is renamed to match that
directory to make multiple eshell windows easier."
  (interactive)
  (let* ((parent (if (buffer-file-name)
                     (file-name-directory (buffer-file-name))
                   default-directory))
         (height (/ (window-total-height) 3))
         (name   (car (last (split-string parent "/" t)))))
    (split-window-vertically (- height))
    (other-window 1)
    (eshell "new")
    (rename-buffer (concat "*eshell: " name "*"))

    (insert (concat "ls"))
    (eshell-send-input)))

(global-set-key (kbd "M-e") 'eshell-here)

(provide 'eshell-config)
