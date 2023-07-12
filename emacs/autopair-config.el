;;(require 'autopair)
;;(autopair-global-mode 1)
;;(setq autopair-autowrap t)
;(require 'elec-pair)
;(electric-pair-mode 1)
;(setq electric-pair-preserve-balance t)
;(setq electric-pair-delete-adjacent-pairs t)
;(setq electric-pair-open-newline-between-pairs t)
;(setq electric-pair-skip-whitespace t)

(use-package elec-pair
  :config
  (electric-pair-mode 1)
  (setq electric-pair-preserve-balance t)
  (setq electric-pair-delete-adjacent-pairs t)
  (setq electric-pair-open-newline-between-pairs t)
  (setq electric-pair-skip-whitespace t))

(provide 'autopair-config)
