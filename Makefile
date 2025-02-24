install:
	sudo python3 -m pip install -Ue .

eacg:
	sudo python3 demo/sampler_eacg.py
	
gpt-2:
	/home/txx/data/miniconda3/envs/eACGM/bin/python demo/pytorch_example.py