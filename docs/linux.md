# linux
You will need ollama running on the host or another remote server. By default, ollama only listens on 127.0.0.1, so you will need to modify it to listen on all interfaces:
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo vim /etc/systemd/system/ollama.service
# add add this to your ollama service file 
[SERVICE]
Environment="OLLAMA_HOST=0.0.0.0"
# additionally, Flash Attention has just been added: 
# Environment="OLLAMA_FLASH_ATTENTION=1"
# daemon-reload to take the changes
sudo systemctl daemon-reload
sudo systemctl restart ollama
# whatever model you want to use, mistral nemo generally works the best, but gemma2 is much smaller and performs well.
ollama pull gemma2:2b
```
For the best performance, you will need an NVIDIA card with CUDA support and docker with gpu passthrough enabled.
Specifically, you will need the NVIDIA drivers and CUDA toolkit (tested with 11.x and 12.1). For Ubuntu refer 
[here](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/).
  
I personally use PopOS 22.04 LTS due to their awesome NVIDIA support out-of-the-box. It has the advantages of Ubuntu
without the bloat. The CUDA setup docs are [here](https://support.system76.com/articles/cuda/).
```bash
# in PopOS
sudo apt install nvidia-cuda-toolkit
```
  
Once your drivers are installed, run:
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
  
At this point, you need to decide what data you want to ingest.  If you want to test with the data user in this project, 
click [here](https://github.com/strf0x1/vxug-papers), click the green **Code** button, and choose **Download Zip**. Just unpack it a folder called data in 
the root of this project.
  
If you want to use a different directory, modify the **DATA_DIR** directory to point to your 
data folder.
```bash
vim run_container.sh
chmod +x run_container.sh
./run_container.sh
```
  
Once you're in the container, refer to [usage](usage.md).