import eurostat

dic = eurostat.get_dic('nama_10_co3_p3', 'coicop', frmt='df')

print(dic)

