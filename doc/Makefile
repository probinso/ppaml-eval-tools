# Makefile for PPAML client script documentation
# Copyright (C) 2014  Galois, Inc.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# To contact Galois, complete the Web form at <http://corp.galois.com/contact/>
# or write to Galois, Inc., 421 Southwest 6th Avenue, Suite 300, Portland,
# Oregon, 97204-1622.

PANDOC = pandoc

ifeq ($(V),1)
X :=
else
X := @
endif

all:	getting-started.html

clean:
	@echo "  RM      getting-started.html"
	$(X)$(RM) getting-started.html

%.html: %.md template.html
	@echo "  PANDOC  $@"
	$(X)$(PANDOC) $< --standalone --to html5 --base-header-level=2 --template=template.html --toc -o $@

.PHONY: all clean
