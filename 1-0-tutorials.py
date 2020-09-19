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

#以下能處理比較大的檔案
def download_file(url, filename):
    # NOTE the stream=True parameter below
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)

        files.download(filename)
        return filename
    except:
        print("Error")
        return 0

url = 'https://imageproxy.icook.network/resize?height=600&nocrop=false&stripmeta=true&type=auto&url=http%3A%2F%2Ftokyo-kitchen.icook.tw.s3.amazonaws.com%2Fuploads%2Frecipe%2Fcover%2F349975%2Fcee4707cbbbf4852.jpg&width=800'
filename = '奶油炒綜合時蔬.jpg'
download_file(url, filename)


