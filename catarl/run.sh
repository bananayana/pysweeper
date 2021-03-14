redis-server --port 12000 &
CUDA_VISIBLE_DEVICES="0" catalyst-rl run-trainer --config=configs/basic.yml &
CUDA_VISIBLE_DEVICES="" catalyst-rl run-samplers --config=configs/basic.yml &