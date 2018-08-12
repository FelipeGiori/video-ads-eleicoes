# **Pesquisa de Video-Ads com uso de personas**

Article : "I always feel like somebody's watching me: measuring online behavioural advertising", available in https://dl.acm.org/citation.cfm?id=2836098.

## **Getting Started**

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
For run in a Docker, see https://github.com/guilhermesooares/dockselpy.

### **Prerequisites**

##### Mozilla Firefox Browser 56

First, remove any existing version.
```
sudo apt-get purge firefox
```
Then run following command to download firefox 56 source code, which comes as .tar file.
```
wget https://ftp.mozilla.org/pub/firefox/releases/56.0/linux-x86_64/en-US/firefox-56.0.tar.bz2

```
Extract the package.
```
tar -xjf firefox-56.0.tar.bz2 
```
Move firefox to /opt directory.
```
sudo mv firefox /opt/
```
Create symlink in order to set the new firefox as default.
```
sudo ln -s /opt/firefox/firefox /usr/bin/firefox
```

##### XVFB (run Selenium without display hardware and no physical input devices)

```
sudo apt-get install xvfb
```

##### Geckowebdriver (Interface between Selenium and Firefox )
Download, uncompress and move to /usr/local/bin/
```
wget https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz

tar -vzxf geckodriver-v0.16.1-linux64.tar.gz

sudo mv geckodriver /usr/local/bin/
```

##### Python3 

```
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
```
Pip (packpage mannager)
```
sudo apt-get install -y python3-pip
```

### **Installing**
Install Selenium:
```
pip3 install selenium
```
Install Pandas: 
```
pip3 install pandas
```
Install PyVirtualDisplay:
```
pip3 install pyvirtualdisplay
```
Install mysql.connector:
```
pip3 install mysql-connector
```
Install tzupdate (auto Update timezone Geolocating your current IP)
```
pip3 install tzupdate
```
Para realizar backup de qualquer diretório da máquina virtual
```
rsync -avzh persona@{HOST}:{PATH OR FILE} {DESTINATION PATH}
```

### **Execution**
To run the script use
```
python3 run.py
```

## **Built With**

* [Selenium](www.seleniumhq.org/) - Portable software-testing framework for web applications.


## **Authors**
Nothing yet.

## **License**

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


