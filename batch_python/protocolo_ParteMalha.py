import os
import subprocess
import shutil
import time
import argparse
import csv
def generateIni(stim, simulation_time, output_dir, save_state, restore_state, print_rate, mesh_print_rate, sigma_factor, sigma, num_volumes, mesh_file, library_file, period_stim1, min_x, max_x, min_y, max_y, num_stim1, dt_pde, dt_ode, use_gpu):
    ini =  """
[main]
num_threads = 6
dt_pde = """ + str(dt_pde) + """
simulation_time = """ + str(simulation_time) + """
abort_on_no_activity = false
use_adaptivity = false
quiet=true

[save_result]
print_rate = """ + str(print_rate) + """
output_dir = """ + str(output_dir) + """
binary = true
init_function = init_save_with_activation_times
main_function = save_with_activation_times
end_function = end_save_with_activation_times
mesh_format = ensight
mesh_print_rate = """ + str(mesh_print_rate) + """
file_prefix = V
library_file = ./shared_libs/libdefault_save_mesh.so

""" + str(save_state) + """

""" + str(restore_state) + """

[update_monodomain]
main_function = update_monodomain_default

[assembly_matrix]
sigma_C =""" + str(sigma) + """
init_function = set_initial_conditions_fvm
sigma_factor = """ + str(sigma_factor) + """
sigma_l = 0.000136842
sigma_n = 0.0000136842
sigma_t = 0.0000136842
library_file = shared_libs/libdefault_matrix_assembly.so
main_function=anisotropic_sigma_assembly_matrix_for_hu_mesh
fibers_in_mesh = true

[linear_system_solver]
tolerance = 1e-16
use_preconditioner = no
use_gpu = """ + str(use_gpu) + """
max_iterations = 200
library_file = shared_libs/libdefault_linear_system_solver.so
main_function = conjugate_gradient
init_function = init_conjugate_gradient
end_function = end_conjugate_gradient

[domain]
name = HU Mesh
original_discretization = 200.0
desired_discretization = 200.0
num_volumes = """ + str(num_volumes) + """
main_function = initialize_grid_with_hu_mesh_with_scar
mesh_file = """ + str(mesh_file) + """
num_extra_fields = 5

[ode_solver]
dt = """ + str(dt_ode) + """
use_gpu = """ + str(use_gpu) + """
gpu_id = 0
library_file = """ + str(library_file) + """

[extra_data]
library_file = shared_libs/libdefault_extra_data.so
main_function = set_extra_data_for_scv_mesh

"""

    stim1_sections = ""
    for i in range(num_stim1):
        stim1_sections += f"""
[stim_1_{i + 1}]
start = {stim[i]}
duration = 2.0
current = -38.0
min_x = {min_x}.0
max_x = {max_x}.0
min_y = {min_y}.0
max_y = {max_y}.0
main_function = stim_x_y_limits

"""

    stim_sections = ""
    for i in range(num_stim1, len(stim)):
        stim_sections += f"""
[stim_{i - num_stim1 + 2}]
start = {stim[i]}
duration = 2.0
current = -38.0
min_x = {min_x}.0
max_x = {max_x}.0
min_y = {min_y}.0
max_y = {max_y}.0
main_function = stim_x_y_limits

"""
    return ini + stim1_sections + stim_sections


def create_dir(dir):
    try:
        print("Writing ", dir)
        os.mkdir(dir)
    except:
        print("Rewriting ", dir)

def delete_dir(dir):
    cmd = "rm -r " + dir
    cmd = "rm -r " + dir
    print(cmd)

    process = subprocess.Popen(cmd, shell = True)
    process.wait()

# Constantes (para uma execução do protocolo)

parser = argparse.ArgumentParser(description = 'Protocolo de Estudo Eletrofisiológico Simulado')

parser.add_argument('--print_rate', action = 'store', dest = 'print_rate', default = '100', required = False, help = 'Taxa de print dos resultados')
parser.add_argument('--mesh_print_rate', action = 'store', dest = 'mesh_print_rate', default = '100', required = False, help = 'Taxa de print da malha')
parser.add_argument('--sigma_factor', action = 'store', dest = 'sigma_factor', default = '0.0125', required = False, help = 'Porcentagem inicial de condutividade na região com fibrose')
parser.add_argument('--sigma', action = 'store', dest = 'sigma', default = '1.00', required = False, help = 'Condutividade na malha')
parser.add_argument('--num_volumes', action = 'store', dest = 'num_volumes', default = '79250', required = False, help = 'Número de elementos na malha')
#parser.add_argument('--mesh_file', action = 'store', dest = 'mesh_file', default = 'meshes/teste.alg', required = False, help = 'Caminho até a malha usada')
parser.add_argument('--mesh_file', action = 'store', dest = 'mesh_file', default = 'meshes/CBEB_corte3.alg', required = False, help = 'Caminho até a malha usada')
parser.add_argument('--library_file', action = 'store', dest = 'library_file', default = 'shared_libs/libtt3_mixed.so', required = False, help = 'Modelo celular adotado')
#parser.add_argument('--library_file', action = 'store', dest = 'library_file', default = 'shared_libs/libten_tusscher_2006.so', required = False, help = 'Modelo celular adotado')
parser.add_argument('--min_x', action = 'store', dest = 'min_x', default = '99100', required = False, help = 'Coordenada inferior do ponto de aplicação do estímulo no eixo x ')
parser.add_argument('--max_x', action = 'store', dest = 'max_x', default = '101100', required = False, help = 'Coordenada superior do ponto de aplicação do estímulo no eixo x ')
parser.add_argument('--min_y', action = 'store', dest = 'min_y', default = '29900', required = False, help = 'Coordenada inferior do ponto de aplicação do estímulo no eixo y ')
parser.add_argument('--max_y', action = 'store', dest = 'max_y', default = '31900', required = False, help = 'Coordenada superior do ponto de aplicação do estímulo no eixo y ')
parser.add_argument('--period_stim1', action = 'store', dest = 'period_stim1', default = '600', required = False, help = 'Intervalo entre aplicações sucessivas do primeiro estímulo')
parser.add_argument('--num_stim1', action = 'store', dest = 'num_stim1', default = '8', required = False, help = 'Número de aplicações do primeiro estímulo')
parser.add_argument('--output_dir_save', action = 'store', dest = 'output_dir_save', default = 'outputs/saveSeptoBatch/', required = False, help = 'Diretório onde os arquivos do save_state vão ser armazenados')
parser.add_argument('--output_dir_restore', action = 'store', dest = 'output_dir_restore', default = 'outputs/restoreSeptoBatch/', required = False, help = 'Diretório onde os arquivos do restore_state vão ser armazenados')
parser.add_argument('--dt_pde', action = 'store', dest = 'dt_pde', default = '0.02', required = False, help = 'Passo de tempo das EDPs')
parser.add_argument('--dt_ode', action = 'store', dest = 'dt_ode', default = '0.02', required = False, help = 'Passo de tempo das EDOs')
parser.add_argument('--nome_arquivo', action = 'store', dest = 'nome_arquivo', default = 'resultado.txt', required = False, help = 'Nome do arquivo onde são salvos os resultados do protocolo')
parser.add_argument('--use_gpu', action = 'store', dest = 'use_gpu', default = 'yes', required = False, help = 'Setar execução em GPU (yes) ou CPU (no)')
parser.add_argument('--inc_sigma_factor', action = 'store', dest = 'inc_sigma_factor', default = 'False', required = False, help = 'Booleano para setar se a porcentagem inicial de condutividade na região com fibrose vai ser incrementada (True) ou decrementada (False) ao longo do tempo')
parser.add_argument('--dir_protocolo', action = 'store', dest = 'dir_protocolo', default = 'outputs/saveSeptoBatch/', required = False, help = 'Diretório onde os .ini finais encontrados vão ser armazenados, junto com os resultados do protocolo')
#parser.add_argument('--caminho_arquivo', action = 'store', dest = 'caminho_arquivo',default = 'resultadoSepto.txt',  required = False, help = '')

arguments = parser.parse_args()

print_rate = int(arguments.print_rate)
mesh_print_rate = int(arguments.mesh_print_rate)
sigma_factor_0 = float(arguments.sigma_factor)
sigma = float(arguments.sigma)
num_volumes = int(arguments.num_volumes)
mesh_file = arguments.mesh_file
library_file = arguments.library_file
min_x = int(arguments.min_x)
min_x = int(arguments.min_x)
max_x = int(arguments.max_x)
min_y = int(arguments.min_y)
max_y = int(arguments.max_y)
period_stim1 = int(arguments.period_stim1)
num_stim1 = int(arguments.num_stim1)
output_dir_save = arguments.output_dir_save
output_dir_restore = arguments.output_dir_restore
dt_pde = float(arguments.dt_pde)
dt_ode = float(arguments.dt_ode)
nome_arquivo = arguments.nome_arquivo
use_gpu = arguments.use_gpu
inc_sigma_factor = bool(arguments.inc_sigma_factor)
dir_protocolo = arguments.dir_protocolo

# Número Máximo de Estímulos
stim_max = 4

# Definição dos Sigma_Factor Avaliados
sigmas_factor = [sigma_factor_0 ]
fator = 1

caminho_arquivo = dir_protocolo+"/" + nome_arquivo

#for j in range(1):
 # if inc_sigma_factor == False:
 #   sigmas_factor.append(sigma_factor_0 / fator)
 # else:
  #  sigmas_factor.append(sigma_factor_0 * fator)
  #fator = fator + 0.25
 
with open(caminho_arquivo, mode='w', newline='') as csv_file:
  csv_writer = csv.writer(csv_file, delimiter=',')
  csv_writer.writerow(['Sigma_Factor', 'Sigma', 'Stimulation_Index', 'Interval', 'Element_Reentry_Rate', 'Element_Block_Rate', 'Element_Normal_Rate', 'Event_Type'])
  csv_writer.writerow([sigmas_factor,sigma])

  #arquivo.write('---------------------------------------------------------------------\n')
  #arquivo.write(f'Protocolo de Estudo Eletrofisológico\n')
  #arquivo.write(dir_protocolo)
  #arquivo.write('---------------------------------------------------------------------\n')

for sigma_factor in sigmas_factor:
 # with open(caminho_arquivo, mode='a', newline='') as csv_file:
  #             sv_writer = csv.writer(csv_file, delimiter=',')
       #        csv_writer.writerow([sigma_factor,sigma])
    #arquivo.write('---------------------------------------------------------------------\n')
    #arquivo.write(f'Sigma_Factor: {sigma_factor} Sigma:{sigma} \n')
    #arquivo.write('---------------------------------------------------------------------\n')
                  
  # Parâmetros Iniciais

  # save assume valor True se estiver rodando o save_state e False se for o restore_state
  save = True
  # end assume valor True se todo o protocolo já foi realizado e False se não
  end = False
  # Lista com os instantes de aplicação de todos os estímulos
  stim = []

  for s in range(num_stim1):
    stim.append(s * period_stim1)

  # Número de estímulos dados (considera os estímulos aplicados a partir do S2)
  i = 2

  start_time = time.time()

  while not end:

      if save:
          simulation_time = stim[-1] + 100

          save_state = '[save_state]\nmain_function = save_simulation_state_with_activation_times\nlibrary_file = ./shared_libs/libdefault_save_state.so\noutput_dir = ' +dir_protocolo+ output_dir_save
          restore_state = ';[restore_state]\n;main_function = restore_simulation_state_with_activation_times\n;input_dir = '+dir_protocolo + output_dir_save

          output_dir = dir_protocolo+output_dir_save

          delete_dir(output_dir)

          create_dir(output_dir)

          ini = generateIni(stim, simulation_time, output_dir, save_state, restore_state, print_rate, mesh_print_rate, sigma_factor, sigma, num_volumes, mesh_file, library_file, period_stim1, min_x, max_x, min_y, max_y, num_stim1, dt_pde, dt_ode, use_gpu)

          file = open(output_dir + "protocolo.ini", 'w')
          file.write(ini)
          file.close()

          cmd = "bin/MonoAlg3D -c " + output_dir + "protocolo.ini"
          print(cmd)

          process = subprocess.Popen(cmd, shell = True)
          process.wait()

          save = False

          # if stim[-1] == (num_stim1 - 1) * period_stim1:
              #with open(caminho_arquivo, "a+") as arquivo:
               #   arquivo.write(f'S1: Aplicação de {num_stim1} estímulos com ciclo de {period_stim1}\n')
                #  arquivo.write('---------------------------------------------------------------------\n')

          file_path = output_dir_save + "activation_info_it_0.acm"

          # num_total_antes = -1
          # value = -1

          # with open(file_path, "r") as file:
          #     for line in file:
          #         num_total_antes += 1
          #         index = line.find("[")
          #         if index != -1:
          #             value_part = line[:index].strip()
          #             parts = value_part.split()
          #             if len(parts) > 0:
          #                 value = int(parts[-1])
          #         if value != -1:
          #             print(value)
          #             if value > len(stim):
          #                 num_espiral_antes += 1
          #             else:
          #                 if value == len(stim):
          #                     num_normal_antes += 1
          #                 else:
          #                     num_bloqueio_antes += 1
      else:
          simulation_time = stim[-1] + 800

          save_state = ';[save_state]\n;main_function = save_simulation_state_with_activation_times\n;library_file = ./shared_libs/libdefault_save_state.so\n;output_dir = '+dir_protocolo + output_dir_save
          restore_state = '[restore_state]\nmain_function = restore_simulation_state_with_activation_times\ninput_dir = ' +dir_protocolo+ output_dir_save

          output_dir = dir_protocolo+output_dir_restore

          delete_dir(output_dir)

          create_dir(output_dir)

          deltas = [stim[-1] + 380 - 10 * i for i in range(19)]
          print(deltas)

          for d in range(len(deltas)):
              f = output_dir + str(deltas[d]) + '/'
              create_dir(f)

              if d == 0:
                  stim.append(deltas[d])
              else:
                  stim[-1] = deltas[d]

              ini = generateIni(stim, simulation_time, f, save_state, restore_state, print_rate, mesh_print_rate, sigma_factor, sigma, num_volumes, mesh_file, library_file, period_stim1, min_x, max_x, min_y, max_y, num_stim1, dt_pde, dt_ode, use_gpu)

              file = open(f + "protocolo.ini", 'w')
              file.write(ini)
              file.close()

              cmd = "bin/MonoAlg3D -c " + f + "protocolo.ini"
              print(cmd)

              process = subprocess.Popen(cmd, shell=True)
              process.wait()

              soma_normal = 0
              soma_bloqueio = 0
              soma_espiral = 0

              taxa_normal = 0
              taxa_bloqueio = 0
              taxa_espiral = 0

              total = -1
              value = -1

              file_path = f + "activation_info_it_0.acm"

              with open(file_path, "r") as file:
                  for line in file:
                      total += 1
                      index = line.find("[")
                      if index != -1:
                          value_part = line[:index].strip()
                          parts = value_part.split()
                          if len(parts) > 0:
                              value = int(parts[-1])
                      if value != -1:
                          if value > len(stim):
                              soma_espiral += 1
                          else:
                              if value == len(stim):
                                  soma_normal += 1
                              else:
                                  soma_bloqueio += 1
              # Por volume
              taxa_normal = soma_normal * 100 / total
              taxa_bloqueio = soma_bloqueio  * 100 / total
              taxa_espiral = soma_espiral * 100 / total

              print(taxa_normal, taxa_bloqueio, taxa_espiral)

              with open(caminho_arquivo, mode='a', newline='') as csv_file:
               csv_writer = csv.writer(csv_file, delimiter=',')
               csv_writer.writerow([sigma_factor, sigma, len(stim) - num_stim1 + 1, stim[-1] - stim[-2], taxa_espiral, taxa_bloqueio, taxa_normal, ('Bloqueio' if taxa_bloqueio > 70.0 else 'Propagação_Normal') if taxa_espiral<20 else 'Espiral'])

              #with open(caminho_arquivo, "a+") as arquivo:
               #   arquivo.write(f'S{len(stim) - num_stim1 + 1} - Intervalo: {stim[-1] - stim[-2]}: Taxa de Elementos com Reentrada em {stim[-1]}: = {str(taxa_espiral)} %\n')
                #  arquivo.write(f'S{len(stim) - num_stim1 + 1} - Intervalo: {stim[-1] - stim[-2]}: Taxa de Elementos com Bloqueio em {stim[-1]}: = {str(taxa_bloqueio)} %\n')
                 # arquivo.write(f'S{len(stim) - num_stim1 + 1} - Intervalo: {stim[-1] - stim[-2]}: Taxa de Elementos com Propagação Normal em {stim[-1]}: = {str(taxa_normal)} %\n')

              if taxa_bloqueio > 50.0 or stim[-1] == 200:
                  #with open(caminho_arquivo, "a+") as arquivo:
                   #   arquivo.write(f'S{len(stim) - num_stim1 + 1}  - Intervalo: {stim[-1] - stim[-2]} = Bloqueio em {stim[-1]}\n')
                   #   arquivo.write('---------------------------------------------------------------------\n')

                  save = True														
                  stim[-1] += 20

                  break
              #else:
                  #if taxa_normal > 90.0:
                      #with open(caminho_arquivo, "a+") as arquivo:
                       #   arquivo.write(f'S{len(stim) - num_stim1 + 1} - Intervalo: {stim[-1] - stim[-2]} = Propagação Normal em {stim[-1]}\n')
                        #  arquivo.write('---------------------------------------------------------------------\n')
                  #else:
                  #  if taxa_espiral >= 10.0:
                  #      with open(caminho_arquivo, "a+") as arquivo:
                  #          arquivo.write(f'S{len(stim) - num_stim1 + 1} - Intervalo: {stim[-1] - stim[-2]} = Espiral em {stim[-1]}\n')
                  #          arquivo.write('---------------------------------------------------------------------\n')
          i += 1
      if i > stim_max:
        end = True

  end_time = time.time()

  #with open(caminho_arquivo, "a+") as arquivo:
      #arquivo.write(f'Tempo de Execução: = {str(end_time - start_time)}\n')

