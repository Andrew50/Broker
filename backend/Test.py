import ftplib
import os
ftp = ftplib.FTP("ftp.nasdaqtrader.com")
ftp.login("anonymous", "")
ftp.cwd("SymbolDirectory")
files_to_download = ["nasdaqlisted.txt", "otherlisted.txt"]
for file in files_to_download:
  with open(file, "wb") as f:
    print(f)
    #ftp.retrbinary(f"RETR {file}", f.write)
ftp.quit()