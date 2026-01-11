extension -i -d 1111 --csp 0 -l 1
extension -i -d 2222 --csp 1 -l 1
extension -i -d 3333 --csp 5 -l 1
extension -i -d 4444 --csp 5 -l 1
ip_extension -i -d 1111 --protocol sip
ip_extension -i -d 2222 --protocol sip
ip_extension -i -d 3333 --protocol sip
ip_extension -i -d 4444 --protocol sip
name -i -d 1111 --name1 "First Name" --name2 "Second name" --number-type dir
name -i -d 2222 --name1 "F." --name2 "SEC" --number-type dir
name -i -d 3333 --name1 "First only" --number-type dir
name -i -d 4444 --name1 "First name very very" --name2 "Second very long lon" --number-type dir
auth_code -i -d 1111 --csp 0 --cil 1111 --customer 0 --hash-type md5a1 --auth-code renGk7aqkjvSWZ
auth_code -i -d 2222 --csp 1 --cil 2222 --customer 0 --hash-type md5a1 --auth-code W8g7bWIWhThsKs
auth_code -i -d 3333 --csp 5 --cil 3333 --customer 0 --hash-type md5a1 --auth-code eLa7vIaqjWDdie
auth_code -i -d 4444 --csp 5 --cil 4444 --customer 0 --hash-type md5a1 --auth-code NaNNWOzCubf8iJ
