import sys


f = open('countries','r')
d = {}
for x in f:
	alpha = x.split('\t')
	if len(alpha) > 1:
		d[alpha[1].strip().lower()] = alpha[0]
print d["CONGO, THE DEMOCRATIC REPUBLIC OF THE".strip().lower()]
