# Muhan Maesu V2
무한매수법 자동화 (업데이트/2021/07/28)  
토큰을 잘못 올려서 레포를 다시 생성했습니다(내 모내기...😥)  

## Introduction
Let's automate **infinite buy** method that popular these days  

![image](main.png)  

## Requirements
- requests
- pyupbit

## Use
1. Clone the files on local or AWS instance
2. Make `secret.json` and put access keys (upbit keys and slack token)
3. Also edit type of coins and principals you want in `order.json` or you can just use `python3 order.py` to make your orders easier.
4. Download requirements
5. Run `python3 muhan.py`
6. If you want to execute in one time, use `python3 muhan.py -p order.json`
7. If you execute on aws, use `nohup python3 muhan.py -p order.json > /dev/null 2>&1 &` . Then the process will run on background.
8. In this case, you can check and shut down using `ps -ef | grep .py` and `sudo kill -9 codes(ex : 1118, 1781..)`  

## Update
- now multiple coins can be used at the same time  
  1. by adding an information of ticker, principal, and first buy to 'order.json'  
  2. by writting down and information of ticker, principal, and first buy on the shell 
- now state update execute every second (2021-01-04)
- now you can make order.json by using `order.py` (2021-01-05)
- now you can set environments by using `requirements.sh` (2021-01-06)  
- now you can make secret.json by using `secret.py` (2021-01-06)


## Result
- 10% profit with Bitcoin (2021-07-01)
- 10% profit with Bitcoin (2021-07-25)
- 10% profit with Steam Dollar (2021-07-30)
- 10% profit with Ethereum (2021-07-30)
- ...
