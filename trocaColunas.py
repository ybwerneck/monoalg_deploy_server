import numpy as np

arquivo_alg = "meshes/paciente2_fatia5.alg"

novo_arquivo_alg = np.loadtxt(arquivo_alg, dtype= 'float', delimiter=',', unpack=False, ndmin =0) 

#novo_arquivo_alg[:, [8,6]] = novo_arquivo_alg[:, [6,8]]
#novo_arquivo_alg[:, [9,7]] = novo_arquivo_alg[:, [7,9]]
#novo_arquivo_alg[:, [10,8]] = novo_arquivo_alg[:, [8,10]]
#novo_arquivo_alg[:, [10,9]] = novo_arquivo_alg[:, [9,10]]

novo_arquivo_alg[:, [7,6]] = novo_arquivo_alg[:, [6,7]]

caminho_arquivo = 'meshes/'
filename = caminho_arquivo + 'Teste_paciente2_fatia5.alg'
np.savetxt(filename, novo_arquivo_alg, delimiter = ',', fmt='%f')
