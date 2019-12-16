from random import choice

def generate_password(m):
    a = ''
    lst = '23456789qwertyuipasdfghjkzxcvbnmQWERTYUPASDFGHJKLZXCVBNM'
    b = ''
    for i in range(m):
        if i != 0:
            while b in list(a):
                b = choice(lst)
            a += b
        else:
            b = choice(lst)
            a += b
    return a

def main(n, m):
    k = []
    h = ''
    for i in range(n):
        if i != 0:
            while h in k:
                h = generate_password(m)
            k.append(h)
        else:
            h = generate_password(m)
            k.append(h)
    return k
