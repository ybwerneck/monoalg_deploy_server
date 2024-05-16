import numpy as np

def modificar_malha2(arquivo, xEsq, xDir, yBaixo, yCima):
    linhas, colunas = arquivo.shape
    j=0
    for i in range (linhas):
        if(arquivo[i, 0] > xEsq and arquivo[i, 0] < xDir and arquivo[i, 1] < yCima and arquivo[i, 1] > yBaixo):
            j=j+1     
    new_matrix = np.empty((j, colunas))
    l=0
    for k in range(linhas):
        if(arquivo[k, 0] > xEsq and arquivo[k, 0] < xDir and arquivo[k, 1] < yCima and arquivo[k, 1] > yBaixo):
            new_matrix[l,:] = arquivo[k,:]
            l=l+1
    
    caminho_arquivo = 'meshes/'
    filename = caminho_arquivo + 'CBEB_BloqUni.alg'
    np.savetxt(filename, new_matrix, delimiter = ',', fmt='%f')
    return new_matrix
# Exemplo de uso:
arquivo_alg = "meshes/teste.alg"

xEsq = 82500.00 
xDir = 123100.00
yBaixo = 23300.00
yCima = 54900.00

novo_arquivo_alg = np.loadtxt(arquivo_alg, dtype= 'float', delimiter=',', unpack=False, ndmin=0)
arquivo_alg_reduzido = modificar_malha2(novo_arquivo_alg, xEsq, xDir, yBaixo, yCima)

