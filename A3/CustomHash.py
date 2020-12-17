import hashlib
from string import ascii_lowercase

def foo():
  for i1 in ascii_lowercase :
    for i2 in ascii_lowercase :
      for i3 in ascii_lowercase :
        for i4 in ascii_lowercase :
          for i5 in ascii_lowercase :
            temp = i1+i2+i3+i4+i5
            string = temp
            string = hashlib.md5(str(string).encode())
            for i in range(99):
              string = hashlib.md5(str(string.hexdigest()).encode())

            for i in range(100):
              string = hashlib.sha256(str(string.hexdigest()).encode())

            for i in range(100):
              string = hashlib.sha512(str(string.hexdigest()).encode())

            print(temp, " = ",string.hexdigest())

            if string.hexdigest() == "57ddee0bcd826d34d610b3c7cf44976c2de67e96084b4f6561eae63dd026b4e161fdf27f288963507bbc4cc677e3fe283bf7d09fb7ad218995cbea1c040241e4":
              print("!!!!!!!!!!!!!!!! ",temp)
              return
            else:
              print("xxxxxxxxxxxxxxx")
foo()
