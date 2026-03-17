import hashlib

md5 = input("软件id：")
Password = hashlib.md5((md5+"415263").encode("gb2312")).hexdigest()


print('密码：'+ Password)
file = open('password.txt','w')
file.write(Password)
file.close()