(use-package flycheck
  :ensure t
  :defer t
  :init
  ;; Enable flycheck for all buffers.
  (add-hook 'after-init-hook 'global-flycheck-mode)
  :config
  (progn
    ;; Highlight whole line with error.
    ;; (setq flycheck-highlighting-mode 'lines)

    ;; Display error messages on one line in minibuffer and by new lines
    ;; separated in `flycheck-error-message-buffer'.

    ;; (use-package subr-x)
    ;; (use-package dash)
    (require 'subr-x)
    (require 'dash)

    (defun flycheck-diplay-error-messages-one-line (errors)
      (-when-let (messages (-keep #'flycheck-error-message errors))
        (when (flycheck-may-use-echo-area-p)
          (message (string-join messages " | "))
          (with-current-buffer (get-buffer-create flycheck-error-message-buffer)
            (erase-buffer)
            (insert (string-join messages "\n\n"))))))

    (setq flycheck-display-errors-function
          'flycheck-diplay-error-messages-one-line)

    ;; Use c++14 standard.
    (setq-default flycheck-clang-language-standard "c++20"
                  flycheck-gcc-language-standard "c++20")))

(provide 'flycheck-config)
