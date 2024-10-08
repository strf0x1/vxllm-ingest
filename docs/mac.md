# mac
```bash
brew install python@3.10
git clone git@github.com:strf0x1/vxllm.git
cd vxllm
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```
At this point, you need to decide what data you want to ingest.  If you want to test with the data used in this project, 
click [here](https://github.com/strf0x1/vxug-papers), click the green **Code** button, and choose **Download Zip**. Unpack
the zip file to the root of this project in a folder called **data**.
   
For usage see [usage](usage.md)