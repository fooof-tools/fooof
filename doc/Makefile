# Minimal makefile for Sphinx documentation
#   This make is adapted & extended from the original sphinx file

##########################################################################
## Settings

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = fooof
SOURCEDIR     = .
BUILDDIR      = _build

# Custom settings
GITHUBORG     = https://github.com/fooof-tools

##########################################################################
## Standard sphinx tasks (from sphinx)

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

##########################################################################
## Custom tasks

# Custom cleaner that also removes the generated files from sphinx-gallery
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf auto_examples
	rm -rf auto_tutorials
	rm -rf auto_motivations
	rm -rf generated

# Check that builds site with nitpicky checking, and also does post-hoc link check
check:
	make SPHINXOPTS="-n" html
	make linkcheck

# Create the plots used in the FOOOF documentation
plots:
	python make_doc_plots.py

# Deploy the site to github pages site
deploy:
	# Clone, specifically, the gh-pages branch, putting it into '_build/gh_pages/'
	#   -b gh-pages --single-branch fetches specifically and only the gh-pages branch
	#   --no-checkout just fetches the root folder without content
	#   --depth 1 is a speed optimization since we don't need the history prior to the last commit
	git clone -b gh-pages --single-branch --no-checkout --depth 1 $(GITHUBORG)/$(SPHINXPROJ) _build/gh_pages

	# Add a .nojekyll file to tell Github pages to bypass Jekyll processing
	touch _build/gh_pages/.nojekyll

	# Copy site into the gh-pages branch folder, then push to Github to deploy
	cd _build/ && \
	cp -r html/* gh_pages && \
	cd gh_pages && \
	git add * && \
	git add .nojekyll && \
	git commit -a -m 'deploy docsite' && \
	git push

# Clean & rebuild the html site, then deploy docsite
install:
	make clean
	make html
	make deploy
