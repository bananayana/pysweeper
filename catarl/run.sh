redis-server --port 12000  >> "redis_logs.txt" 2>> "redis_logs.txt" &
CUDA_VISIBLE_DEVICES="0" catalyst-rl run-trainer --config=configs/basic.yml  >> "trainer_logs.txt"  2>> "trainer_logs.txt" &
CUDA_VISIBLE_DEVICES="" catalyst-rl run-samplers --config=configs/basic.yml  >> "samplers_logs.txt" 2>> "samplers_logs.txt" &