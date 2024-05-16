import os
import numpy as np

pastaBase = 'output_batch/'

resultados = []



for i in os.listdir(pastaBase):
    caminho_pasta = os.path.join(pastaBase, i)
    print(caminho_pasta)

    if os.path.isdir(caminho_pasta):
        nomeDoArquivo = "resultado.csv"
        caminhoProArquivo = os.path.join(caminho_pasta, nomeDoArquivo)

        if os.path.exists(caminhoProArquivo):
            data = np.genfromtxt(caminhoProArquivo, delimiter=',', dtype=None, names=True, encoding=None)

            with open(caminhoProArquivo, 'r') as file:
                lines = file.readlines()

            if 0<= 2 < len(lines):
                del lines[2]
                with open(caminhoProArquivo) as file:
                    file.writelines(lines)

            indexMaiorValor = np.argmax(data[Element_Reentry_Rate])
            LinhaMaiorValor = data[indexMaiorValor]
            resultados.append(LinhaMaiorValor)


caminhoArquivoCSV = '/output_batch/resultado.csv'
np.savetxt(caminhoArquivoCSV, resultados, delimiter=',', fmt='%s')
