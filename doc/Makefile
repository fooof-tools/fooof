# Minimal makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = fooof
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom cleaner that also removes the generated files from sphinx-gallery
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf auto_examples
	rm -rf auto_tutorials

## make install:
# Build the html site, and push it to gh-pages branch of repo to deploy
install:
	rm -rf _build/doctrees _build/tmp_html
	# Clone, specifically, the gh-pages branch:
	#   --no-checkout just fetches the root folder without content
	#   --depth 1 is a speed optimization since we don't need the
	#     history prior to the last commit
	#   -b gh-pages fetches only the branch for the gh-pages
	git clone -b gh-pages --single-branch --no-checkout --depth 1 https://github.com/fooof-tools/fooof _build/tmp_html
	touch _build/tmp_html/.nojekyll
	make html
	cd _build/ && \
	cp -r html/* tmp_html && \
	cd tmp_html && \
	git add * && \
	git add .nojekyll && \
	git commit -a -m 'Make install' && \
	git push