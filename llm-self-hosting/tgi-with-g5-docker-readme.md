## Hosting TGI on G5 using docker
### Launch and prepare EC2 instance
1. Use the command below to find the right image. 
   For the instructions below [sample imge ami-0ba8680ae66b50b7d](g5-image.json) is used.
```
##Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.0.1 (Amazon Linux 2) 20240312
aws ec2 describe-images --region ap-south-1 --owners amazon \
--filters 'Name=name,Values=Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.0.1 (Amazon Linux 2) ????????' 'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
```
2. Launch with 512 GB storage.
3. Create the EC2 instance. For this doc , I created g5.xlarge.
4. SSH to the instance and execute the command below. 
```shell
nvidia-smi
```
```shell
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.129.03             Driver Version: 535.129.03   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA A10G                    On  | 00000000:00:1E.0 Off |                    0 |
|  0%   51C    P0             186W / 300W |  21268MiB / 23028MiB |     96%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|    0   N/A  N/A     14463      C   /opt/conda/bin/python3.10                 21256MiB |
+---------------------------------------------------------------------------------------+
```

### Deploy Llama-7B model
1. Follow https://huggingface.co/docs/text-generation-inference/index and https://github.com/huggingface/text-generation-inference .
2. Following works for Llama2.
```shell
export HF_TOKEN=<HF_TOKEN>
model=meta-llama/Llama-2-7b-chat-hf
volume=$PWD/data 

docker run --gpus all --shm-size 1g -p 8080:80 \
-v $volume:/data \
-e HF_TOKEN=${HF_TOKEN} \
ghcr.io/huggingface/text-generation-inference:1.4 \
--model-id $model
```
To test the model run -
```shell
curl 127.0.0.1:8080/generate   \
  -X POST   \
  -d '{"inputs":"What is LLM ?","parameters":{"max_new_tokens":20}}'   \
  -H 'Content-Type: application/json'

{"generated_text":"\n\nLLM stands for Master of Laws, which is a postgraduate academic degree, purs"}
```