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

CONDA = conda/miniconda/bin/conda


conda/miniconda.sh:
	echo Download Miniconda
	mkdir -p conda
	wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh -O conda/miniconda.sh; \

conda/miniconda: conda/miniconda.sh
	bash conda/miniconda.sh -b -p conda/miniconda; \

install_conda: conda/miniconda

conda/miniconda/bin/conda-pack: conda/miniconda
	conda/miniconda/bin/conda install conda-pack -c conda-forge  -y

install_conda_pack: conda/miniconda/bin/conda-pack

clean_conda:
	rm -rf ./conda
pack: make_build
	rm -f *.tar.gz
	echo Create archive \"fit-apply-$(VERSION)-$(BRANCH).tar.gz\"
	cd make_build; tar czf ../fit-apply-$(VERSION)-$(BRANCH).tar.gz fit apply get_coeffs prophet model ts_forecast_venv

clean_pack:
	rm -f *.tar.gz


build: make_build

make_build:
	# required section
	echo make_build
	mkdir make_build
	cp -R ./fit make_build
	cp -R ./apply make_build
	cp -R ./get_coeffs make_build
	cp -R ./prophet make_build
	cp -R ./model make_build

	cp *.md make_build/fit/
	cp *.md make_build/apply/
	cp *.md make_build/get_coeffs/
	cp *.md make_build/prophet/
	cp *.md make_build/model/

	mkdir -p make_build/ts_forecast_venv/lib/python3.9/site-packages
	cp -R ./ts_forecasting  make_build/ts_forecast_venv/lib/python3.9/site-packages

conda_venv: conda/miniconda
	$(CONDA) env create -f build_environment.yml -p ./conda_venv
	./conda_venv/bin/python3.9 -m pip  install postprocessing_sdk --extra-index-url http://s.dev.isgneuro.com/repository/ot.platform/simple --trusted-host s.dev.isgneuro.com


venv.tar.gz: conda_venv conda/miniconda/bin/conda-pack
	$(CONDA) pack -p ./conda_venv -o ./venv.tar.gz

venv: venv.tar.gz
	mkdir -p ./venv
	tar -xzf ./venv.tar.gz -C ./venv

clean_venv:
	rm -rf ./venv
	rm -rf ./conda_venv
	rm -rf ./venv.tar.gz

venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/fit: venv
	ln -r -s ./fit venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/fit

venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/apply: venv
	ln -r -s ./apply venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/apply

venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/prophet: venv
	ln -r -s ./prophet venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/prophet

venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/get_coeffs: venv
	ln -r -s ./get_coeffs venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/get_coeffs

venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/model: venv
	ln -r -s ./model venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/model

venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/otl_v1/config.ini:
	cp ./venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/otl_v1/config.example.ini ./venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/otl_v1/config.ini

venv/lib/python3.9/site-packages/ts_forecasting:
	ln -r -s ./ts_forecasting ./venv/lib/python3.9/site-packages/ts_forecasting

dev: venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/fit venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/apply venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/prophet venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/get_coeffs venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/otl_v1/config.ini venv/lib/python3.9/site-packages/ts_forecasting
	@echo "!!!IMPORTANT!!!. Configure otl_v1 config.ini"
	@echo "   !!!!    "
	@echo "   vi venv/lib/python3.9/site-packages/postprocessing_sdk/pp_cmd/otl_v1/config.ini"
	@echo "   !!!!    "
	touch ./dev


clean_build:
	rm -rf make_build


clean: clean_build clean_pack

clean_dev: clean_venv
	rm -f ./dev

test:
	@echo "Testing..."

clean_test:
	@echo "Clean tests"