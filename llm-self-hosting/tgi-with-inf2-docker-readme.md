## Hosting TGI on Inferentia2 using docker
### Launch and prepare EC2 instance
1. Use the command below to find the right image. Refer https://docs.aws.amazon.com/dlami/latest/devguide/launch.html. 
For the instructions below [sample imge ami-06e474e6305e475ac](image.json) is used. 
```
aws ec2 describe-images --region ap-south-1 --owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Amazon Linux 2) Version ??.?' 'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
```
2. Launch with 512 GB storage. 
3. Create the EC2 instance. For this doc , I created inf2.xlarge which just one Inferentia2 chip and 2 core. Refer https://aws.amazon.com/ec2/instance-types/inf2/ 
4. SSH to the instance and execute the command below. Refer https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/devflows/inference/ec2-then-ec2-devflow-inf2.html
```shell
sudo yum remove aws-neuron-dkms -y
sudo yum install kernel-devel-$(uname -r) kernel-headers-$(uname -r) -y
sudo yum versionlock delete aws-neuronx-dkms
sudo yum install aws-neuronx-dkms -y
lsmod | grep neuron
source activate
```
5. List neuron devices. 
```shell
neuron-ls
```
```shell
# Sample output
[ec2-user@ip-10-0-137-174 ~]$ neuron-ls
+--------+--------+--------+---------+
| NEURON | NEURON | NEURON |   PCI   |
| DEVICE | CORES  | MEMORY |   BDF   |
+--------+--------+--------+---------+
| 0      | 2      | 32 GB  | 00:1f.0 |
+--------+--------+--------+---------+
```
### Deploy Mistral-7B model
1. Follow https://github.com/huggingface/optimum-neuron/tree/main/text-generation-inference to deploy the neuron model. Look at https://huggingface.co/aws-neuron for exported models for neuron. Find the model which is exported for 2 cores. 
2. Following works for Mistral-7B model. 
```shell
export HF_TOKEN=<HF_TOKEN>
docker run -p 8080:80    \
     -v $(pwd)/data:/data       \
     --device=/dev/neuron0      \
     -e HF_TOKEN=${HF_TOKEN}    \
     ghcr.io/huggingface/neuronx-tgi:latest       \
     --model-id aws-neuron/Mistral-7B-Instruct-v0.2-seqlen-2048-bs-1-cores-2     \
     --max-batch-size 1       \
     --max-input-length 1024   \
     --max-total-tokens 2048
```
Following is the sample input and output to test the model -  
```shell
curl 127.0.0.1:8080/generate    \
 -X POST    \
 -d '{"inputs":"What is LLM ?","parameters":{"max_new_tokens":20}}'    \
 -H 'Content-Type: application/json'

{"generated_text":"\nLaw is a very vast subject and it is not possible to learn all the aspects of law"}

```
### Deploy Llama-7B model
1. Follow https://github.com/huggingface/optimum-neuron/tree/main/text-generation-inference to deploy the neuron model. Look at https://huggingface.co/aws-neuron for exported models for neuron. Find the model which is exported for 2 cores.
2. Following works for Llama2.
```shell
export HF_TOKEN=<HF_TOKEN>
docker run -p 8080:80           \
     -v $(pwd)/data:/data       \
     --device=/dev/neuron0      \
     -e HF_TOKEN=${HF_TOKEN}    \
     ghcr.io/huggingface/neuronx-tgi:latest       \
     --model-id aws-neuron/Llama-2-7b-hf-neuron-budget     \
     --max-batch-size 1       \
     --max-input-length 1024   \
     --max-total-tokens 2048   
```
To test the model run -
```shell
curl 127.0.0.1:8080/generate   \
  -X POST   \
  -d '{"inputs":"What is LLM ?","parameters":{"max_new_tokens":20}}'   \
  -H 'Content-Type: application/json'

{"generated_text":"\n\nLLM stands for Master of Laws, which is a postgraduate academic degree, purs"}
```
### Deploy Llama-2-7b-chat-hf model 4096 Sequence Length
1. Following works for Llama2.
```shell
export HF_TOKEN=<HF_TOKEN>

docker run -p 8080:80 \
       -v $(pwd)/data:/data \
       --device=/dev/neuron0 \
       -e HF_TOKEN=${HF_TOKEN} \
       -e HF_BATCH_SIZE=1 \
       -e HF_SEQUENCE_LENGTH=4096 \
       -e HF_AUTO_CAST_TYPE="fp16" \
       -e HF_NUM_CORES=2 \
       ghcr.io/huggingface/neuronx-tgi:latest \
       --model-id meta-llama/Llama-2-7b-chat-hf \
       --max-batch-size 1 \
       --max-input-length 4000 \
       --max-total-tokens 4096  
```
To test the model run -
```shell
curl 127.0.0.1:8080/generate   \
  -X POST   \
  -d '{"inputs":"What is LLM ?","parameters":{"max_new_tokens":4000}}'   \
  -H 'Content-Type: application/json'

{"generated_text":"\n\nLLM (Master of Laws) is a postgraduate degree in law. It is typically a one-year program that is designed for students who have already completed a law degree, such as a Juris Doctor (JD) or Bachelor of Laws (LLB). The LLM program provides advanced education in a specific area of law, such as corporate law, intellectual property law, or international law.\n\nThe LLM program typically includes coursework, research, and sometimes, clinical work. Students in an LLM program can expect to take classes from experienced faculty members and engage in discussions and debates with their peers. The program also provides opportunities for students to network with professionals in their chosen area of law.\n\nEarning an LLM degree can provide several benefits, including:\n\n1. Specialized knowledge: An LLM degree allows students to gain advanced knowledge in a specific area of law, which can be helpful for those who want to specialize in a particular area of practice.\n2. Career advancement: An LLM degree can help lawyers advance their careers by providing them with specialized knowledge and skills that can be applied in their practice.\n3. Networking opportunities: LLM programs provide opportunities for students to network with professionals in their chosen area of law, which can be helpful for building a professional network.\n4. Personal fulfillment: Pursuing an LLM degree can be a personally fulfilling experience, as it allows students to delve deeper into a specific area of law and gain a deeper understanding of the subject matter.\n\nIt's worth noting that an LLM degree is not a requirement for practicing law, and it is not a substitute for a JD or LLB degree. It is a supplemental degree that provides additional education and training in a specific area of law.</s>"}
```