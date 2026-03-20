from datetime import datetime

str = '2000-11-13'

print(datetime.strptime(str,'%Y-%m-%d').timestamp())