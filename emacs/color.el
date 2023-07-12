;; (add-to-list 'custom-theme-load-path (concat config-dir "/themes/solarized-gray")) 
;; (add-to-list 'custom-theme-load-path (concat config-dir "/themes/s3r0"))
(add-to-list 'custom-theme-load-path (concat config-dir "/themes/emacs-color-theme-solarized-master"))
;;(add-to-list 'custom-theme-load-path (concat config-dir "/themes/chriskempson-tomorrow-theme"))
;;(require 'color-theme)
;;(require 'color-theme-solarized)

(load-theme 'solarized t)
(add-hook 'after-make-frame-functions
  	  (set-frame-parameter nil 'background-mode 'dark)
 	  (set-terminal-parameter nil 'background-mode 'dark)
 	  (enable-theme 'solarized))

;; (load-theme 'solarized-gray t)
;; (add-hook 'after-make-frame-functions
;;  	  (set-frame-parameter nil 'background-mode 'dark)
;; 	  (set-terminal-parameter nil 'background-mode 'dark)
;; 	  (enable-theme 'solarized-gray)
	  ;; )
;; (load-theme 's3r0 t)
;; (add-hook 'after-make-frame-functions
;;  	  (set-frame-parameter nil 'background-mode 'dark)
;; 	  (set-terminal-parameter nil 'background-mode 'dark)
;; 	  (enable-theme 's3r0)
;; 	  )

;;(load-theme 'tomorrow-night t)
;;(add-hook 'window-setup-hook
;;	  (set-background-color "#1A1919")
;;	  (set-foreground-color "#BAB6B1")
;;	  ;;(set-cursor-color "#40FF40")
;;	  ) 
(set-face-attribute 'bold nil
                    :weight 'regular)

(make-face 'header-line-grey)
(set-face-attribute 'header-line-grey nil
                    :weight 'medium
                    :foreground "#fff"
                    :background "#000"
                    :box '(:line-width 1 :color "#000"))
(make-face 'header-line-red)
(set-face-attribute 'header-line-red nil
                    :weight 'medium
                    :foreground "#eee"
                    :background "#dc322f";;"#dd7777"
                    :box '(:line-width 1 :color "#dc322f"))

(set-face-attribute 'mode-line nil
                    :height 10
                    :background "#999"
                    :box nil)
(set-face-attribute 'mode-line-inactive nil
                    :height 10
                    :background "#999"
                    :box nil)
(set-face-attribute 'header-line nil
                    :inherit nil
                    :foreground "#95a3a3"
                    :background "#000"
                    :box '(:line-width 3 :color "#000"))

(set-face-attribute 'linum nil
                    :background "#002b36")
                    ;; :background "#121212")
(provide 'color)
