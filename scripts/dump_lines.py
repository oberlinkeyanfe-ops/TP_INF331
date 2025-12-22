p='Backend/routes/dashboard.py'
with open(p,'rb') as f:
    data=f.read().splitlines()
for i in range(1072,1088):
    try:
        print(i+1, repr(data[i]))
    except IndexError:
        print('no line', i+1)
