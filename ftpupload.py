from ftplib import FTP
from credentials import ftplogin, ftppassword, ftpserver
import os


# print(ftpserver + ftplogin + ftppassword)

def ftpupload(folderpath='data/dwcharts/'):
    ftp = FTP(ftpserver)
    ftp.login(ftplogin, ftppassword)
    directory = os.fsencode(folderpath)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        print(file)
        print(filename)
        with open(f'{folderpath}{filename}', 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        print (f'{filename} hochgeladen')
    ftp.quit()
    print(f'ftp upload an {ftpserver} erfolgreich')
