import os
import subprocess
from zipfile import ZipFile
import lambda_config

role = lambda_config.role
functions = lambda_config.functions

def zipDir(zipObj, dirName):
    for folderName, _, filenames in os.walk(dirName):
       for filename in filenames:
           filePath = os.path.join(folderName, filename)
           zipObj.write(filePath)

for f in functions:
    zipName = "zips/" + f + ".zip"

    zipObj = ZipFile(zipName, "w")
    zipObj.write(f + ".py")
    zipObj.write("rds_config.py")
    zipObj.write("mysql_connector.py")
    zipDir(zipObj, "pymysql")
    zipDir(zipObj, "PyMySQL-0.9.3.dist-info")
    zipObj.close()

    p = subprocess.run("aws lambda get-function --function-name {}".format(f), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if p.returncode == 255:
        subprocess.run("aws lambda create-function --function-name {} --runtime python3.8 --role {} --handler {}.handler --zip-file fileb://{} --timeout 5".format(f, role, f, zipName), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f,"created")
    else:
        subprocess.check_output("aws lambda update-function-code --function-name {} --zip-file fileb://{}".format(f, zipName))
        print(f,"updated")