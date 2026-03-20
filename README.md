<<<<<<< HEAD
# Python Phishing URL Detection
---

### Demo Video: [youtube.com/watch?si=ttLCXu7wOhOWcPMq&v=pR_KcZEQ3M0&feature=youtu.be)

**Python 3.11.9 _(Currently Using)_**


## How to Run?

- Clone or download [python-phishing-url-detection](https://github.com/cybercrimetelangana8-cpu/majorprojectfinal) 

`git clone git@github.com:sannjayy/python-phishing-url-detection.git`


- Create a virtual environment
```bash
python -m venv zenv
source zenv/Scripts/activate # Windows
source zenv/bin/activate # Mac
```


- Install basic requirements
```bash
pip install -r requirements.txt

# OR INITIAL INSTALLATION 
pip install --upgrade pip
pip install --upgrade setuptools

pip install pandas whois httpx
pip install pycaret # It will take sometime.
```

### Replace Domains

```python
if __name__ == "__main__": 
    phishing_url_1 = 'https://bafybeifqd2yktzvwjw5g42l2ghvxsxn76khhsgqpkaqfdhnqf3kiuiegw4.ipfs.dweb.link/'
    phishing_url_2 = 'http://about-ads-microsoft-com.o365.frc.skyfencenet.com'
    real_url_1 = 'https://chat.openai.com'
    real_url_2 = 'https://github.com/'
    
    
    print(predict(phishing_url_1))
    print(predict(phishing_url_2))
    print(predict(real_url_1))
    print(predict(real_url_2))
```

### To Run

```bash
python main.py


# OUTPUT: {'prediction_label': 0, 'prediction_score': 68.39} 

# 0 = False | 1 True
```

---

### To Run GUI

```bash
pip install flask

python app.py
```

Open http://127.0.0.1:5000 in your browser!


 13979c0b1193c28421c6dd500ca4233a83b1095f
