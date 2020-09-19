#Google Colab 將檔案下載至本機檔案系統
from google.colab import files

with open('example.txt', 'w') as f:
  f.write('some content')

files.download('example.txt')
