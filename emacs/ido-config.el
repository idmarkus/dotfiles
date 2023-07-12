(ido-mode 1)
(ido-everywhere 1)

;(require 'ido-vertical-mode)
;(ido-vertical-mode 1)
;(setq ido-vertical-define-keys 'C-n-and-C-p-only)
;(setq ido-vertical-show-count t)
;
;(require 'ido-ubiquitous)
;(ido-ubiquitous-mode 1)


(use-package ido-vertical-mode
  :config
  (ido-vertical-mode 1)
  (setq ido-vertical-define-keys 'C-n-and-C-p-only)
  (setq ido-vertical-show-count t))

(use-package ido-ubiquitous
  :config
  (ido-ubiquitous-mode 1))


(use-package smex
  :config
                                        ;(smex-initialize)
                                        ;(global-set-key "\M-x" 'smex)
  ;;(global-set-key "\M-X" 'smex-major-mode-commands)
  (global-set-key [(meta x)]
                  (lambda ()
                    (interactive)
                    (or (boundp 'smex-cache)
                        (smex-initialize))
                    (global-set-key [(meta x)] 'smex)
                    (smex)))
  (global-set-key [(shift meta x)]
                  (lambda ()
                    (interactive)
                    (or (boundp 'smex-cache)
                        (smex-initialize))
                    (global-set-key [(shift meta x)] 'smex-major-mode-commands)
                    (smex-major-mode-commands)))

;;; Filters ido-matches setting acronynm matches in front of the results
  (defadvice ido-set-matches-1 (after ido-smex-acronym-matches activate)
    (if (and (fboundp 'smex-already-running) (smex-already-running)
             (> (length ido-text) 1))
        (let ((regex (concat "^" (mapconcat 'char-to-string ido-text "[^-]*-")))
              (acronym-matches (list))
              (remove-regexes '("-menu-")))
          ;; Creating the list of the results to be set as first
          (dolist (item items)
            (if (string-match ido-text item) ;; exact match
                (add-to-list 'acronym-matches item)
              (if (string-match (concat regex "[^-]*$") item) ;; strict match
                  (add-to-list 'acronym-matches item)
                (if (string-match regex item) ;; appending relaxed match
                    (add-to-list 'acronym-matches item t)))))

          ;; Filtering ad-return-value
          (dolist (to_remove remove-regexes)
            (setq ad-return-value
                  (delete-if (lambda (item)
                               (string-match to_remove item))
                             ad-return-value)))

          ;; Creating resulting list
          (setq ad-return-value
                (append acronym-matches
                        ad-return-value))

          (delete-dups ad-return-value)
          (reverse ad-return-value))))

  (global-set-key "\C-c \C-c \M-x" 'execute-extended-command))

;;(setq ido-file-extensions-order '(".h", ".hpp", ".c", ".cpp"))

(provide 'ido-config)
