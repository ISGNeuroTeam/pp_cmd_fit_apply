#.SILENT:
SHELL = /bin/bash


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"fit_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
"

VERSION := 0.0.1
BRANCH := $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')

pack: make_build
	rm -f *.tar.gz
	echo Create archive \"fit-apply-$(VERSION)-$(BRANCH).tar.gz\"
	cd make_build; tar czf ../fit-apply-$(VERSION)-$(BRANCH).tar.gz fit apply get_coef prophet ts_forecast_venv

clean_pack:
	rm -f *.tar.gz


build: make_build

make_build:
	# required section
	echo make_build
	mkdir make_build
	cp -R ./fit make_build
	cp -R ./apply make_build
	cp -R ./get_coef make_build
	cp -R ./prophet make_build

	cp *.md make_build/fit/
	cp *.md make_build/apply/
	cp *.md make_build/get_coef/

	mkdir -p make_build/ts_forecast_venv/lib/python3.9/site-packages
	cp -R ./ts_forecasting  make_build/ts_forecast_venv/lib/python3.9/site-packages



clean_build:
	rm -rf make_build


clean: clean_build clean_pack

test:
	@echo "Testing..."

clean_test:
	@echo "Clean tests"