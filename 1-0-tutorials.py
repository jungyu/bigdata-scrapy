#Google Colab 將檔案下載至本機檔案系統
from google.colab import files

with open('example.txt', 'w') as f:
  f.write('some content')

files.download('example.txt')


#在 Colab 沒法寫入此檔
import requests
url = 'https://www.python.org/static/img/python-logo.png'
r = requests.get(url)
f = open('python.jpg', 'wb')
# r.content 取得回應內容( byte stream 位元組流)
f.write(r.content)
f.close()
