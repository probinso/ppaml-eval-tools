;; .dir-locals.el -- directory-local variables for PPAML client scripts
;; Copyright (C) 2013, 2014  Galois, Inc.
;;
;; This library is free software: you can redistribute it and/or modify it
;; under the terms of the GNU General Public License as published by the Free
;; Software Foundation, either version 3 of the License, or (at your option)
;; any later version.
;;
;; This library is distributed in the hope that it will be useful, but WITHOUT
;; ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
;; FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
;; more details.
;;
;; You should have received a copy of the GNU General Public License along with
;; this library.  If not, see <http://www.gnu.org/licenses/>.
;;
;; To contact Galois, complete the Web form at
;; <http://corp.galois.com/contact/> or write to Galois, Inc., 421 Southwest
;; 6th Avenue, Suite 300, Portland, Oregon, 97204-1622.

((markdown-mode . ((indent-tabs-mode . nil)))
 (python-mode . (; as per PEP 8
		 (python-indent . 4)
		 (indent-tabs-mode . nil)
		 (fill-column . 79))))
