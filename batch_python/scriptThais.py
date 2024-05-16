import os
import subprocess
import time
import argparse
import csv

def generateIni(stim, simulation_time, output_dir, save_state, restore_state, print_rate, mesh_print_rate, sigma_factor, sigma, num_volumes, mesh_file, library_file, min_x, max_x, min_y, max_y, min_z, max_z, num_stim1, dt_pde, dt_ode, use_gpu, sigma_c, discretization, num_extra_fields, main_function_domain, main_function_assembly_matrix, fibers_in_mesh, extra_data):
    ini =  """
[main]
num_threads = 6
dt_pde = """ + str(dt_pde) + """
simulation_time = """ + str(simulation_time) + """
abort_on_no_activity = false
use_adaptivity = false
;quiet = true

[save_result]
print_rate = """ + str(print_rate) + """
output_dir = """ + str(output_dir) + """
binary = true
init_function = init_save_with_activation_times
main_function = save_with_num_activation_times
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
sigma_C = """ + str(sigma_c) + """
init_function = set_initial_conditions_fvm
sigma_factor = """ + str(sigma_factor) + """
sigma_l = """ + str(sigma) + """
sigma_t = """ + str(sigma) + """
sigma_n = """ + str(sigma) + """
library_file = shared_libs/libdefault_matrix_assembly.so
main_function = """ + str(main_function_assembly_matrix) + """
fibers_in_mesh = """ + str(fibers_in_mesh) + """

main_function_assembly_matrix

[linear_system_solver]
tolerance = 1e-9
use_preconditioner = no
use_gpu = """ + str(use_gpu) + """
max_iterations = 200
library_file = shared_libs/libdefault_linear_system_solver.so
main_function = conjugate_gradient
init_function = init_conjugate_gradient
end_function = end_conjugate_gradient

[domain]
name = HU Mesh 3D
original_discretization = """ + str(discretization) + """
desired_discretization = """ + str(discretization) + """
num_volumes = """ + str(num_volumes) + """
main_function = """ + str(main_function_domain) + """
mesh_file = """ + str(mesh_file) + """
num_extra_fields = """ + str(num_extra_fields) + """

[ode_solver]
dt = """ + str(dt_ode) + """
use_gpu = """ + str(use_gpu) + """
gpu_id = 0
library_file = """ + str(library_file) + """

""" + str(extra_data) + """

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
min_z = {min_z}.0
max_z = {max_z}.0
main_function = stim_x_y_z_limits

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
min_z = {min_z}.0
max_z = {max_z}.0
main_function = stim_x_y_z_limits

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
    print(cmd)

    process = subprocess.Popen(cmd, shell = True)
    process.wait()

# Constantes (para uma execução do protocolo)

parser = argparse.ArgumentParser(description = 'Protocolo de Estudo Eletrofisiológico Simulado')

parser.add_argument('--pr', action = 'store', dest = 'print_rate', default = '100', required = False, help = 'Taxa de print dos resultados')
parser.add_argument('--mpr', action = 'store', dest = 'mesh_print_rate', default = '100', required = False, help = 'Taxa de print da malha')
parser.add_argument('--sf', action = 'store', dest = 'sigma_factor', default = '0.0125', required = False, help = 'Porcentagem inicial de condutividade na região com fibrose')
parser.add_argument('--s', action = 'store', dest = 'sigma', default = '0.0001847575058', required = False, help = 'Condutividade na malha')
parser.add_argument('--nv', action = 'store', dest = 'num_volumes', default = '23194', required = False, help = 'Número de elementos na malha')
parser.add_argument('--mf', action = 'store', dest = 'mesh_file', default = 'meshes/paciente7_fatia5_f1.alg', required = False, help = 'Caminho até a malha usada')
parser.add_argument('--lf', action = 'store', dest = 'library_file', default = 'shared_libs/libtt3_mixed_with_activations_times.so', required = False, help = 'Modelo celular adotado')
parser.add_argument('--min_x', action = 'store', dest = 'min_x', default = '68300', required = False, help = 'Coordenada inferior do ponto de aplicação do estímulo no eixo x ')
parser.add_argument('--max_x', action = 'store', dest = 'max_x', default = '70300', required = False, help = 'Coordenada superior do ponto de aplicação do estímulo no eixo x ')
parser.add_argument('--min_y', action = 'store', dest = 'min_y', default = '115700', required = False, help = 'Coordenada inferior do ponto de aplicação do estímulo no eixo y ')
parser.add_argument('--max_y', action = 'store', dest = 'max_y', default = '117700', required = False, help = 'Coordenada superior do ponto de aplicação do estímulo no eixo y ')
parser.add_argument('--min_z', action = 'store', dest = 'min_z', default = '100', required = False, help = 'Coordenada inferior do ponto de aplicação do estímulo no eixo z ')
parser.add_argument('--max_z', action = 'store', dest = 'max_z', default = '100', required = False, help = 'Coordenada superior do ponto de aplicação do estímulo no eixo z ')
parser.add_argument('--ps1', action = 'store', dest = 'period_stim1', default = '400', required = False, help = 'Intervalo entre aplicações sucessivas do primeiro estímulo')
parser.add_argument('--ns1', action = 'store', dest = 'num_stim1', default = '8', required = False, help = 'Número de aplicações do primeiro estímulo')
parser.add_argument('--os', action = 'store', dest = 'output_dir_save', default = 'save/', required = False, help = 'Diretório onde os arquivos do save_state vão ser armazenados')
parser.add_argument('--or', action = 'store', dest = 'output_dir_restore', default = 'restore/', required = False, help = 'Diretório onde os arquivos do restore_state vão ser armazenados')
parser.add_argument('--dt_pde', action = 'store', dest = 'dt_pde', default = '0.02', required = False, help = 'Passo de tempo das EDPs')
parser.add_argument('--dt_ode', action = 'store', dest = 'dt_ode', default = '0.02', required = False, help = 'Passo de tempo das EDOs')
parser.add_argument('--nf', action = 'store', dest = 'nome_arquivo', default = 'results.csv', required = False, help = 'Nome do arquivo onde são salvos os resultados do protocolo')
parser.add_argument('--gpu', action = 'store', dest = 'use_gpu', default = 'yes', required = False, help = 'Setar execução em GPU (yes) ou CPU (no)')
parser.add_argument('--dp', action = 'store', dest = 'dir_protocolo', default = './outputs/protocolo/', required = False, help = 'Diretório onde os .ini finais encontrados vão ser armazenados, junto com os resultados do protocolo')
parser.add_argument('--sc', action = 'store', dest = 'sigma_c', default = '1.00', required = False, help = 'Porcentagem de condutividade')
parser.add_argument('--d', action = 'store', dest = 'discretization', default = '200.0', required = False, help = 'Discretização da malha')
parser.add_argument('--nef', action = 'store', dest = 'num_extra_fields', default = '5', required = False, help = 'Número de colunas extras no .alg')
parser.add_argument('--mfd', action = 'store', dest = 'main_function_domain', default = 'initialize_grid_with_hu_mesh_with_scar', required = False, help = 'Função de domínio')
parser.add_argument('--mfam', action = 'store', dest = 'main_function_assembly_matrix', default = 'anisotropic_sigma_assembly_matrix_for_hu_mesh', required = False, help = 'Função de montagem da matriz')
parser.add_argument('--fm', action = 'store', dest = 'fibers_in_mesh', default = 'true', required = False, help = 'Malha com fibras (true) ou não (false)')
parser.add_argument('--pm', action = 'store', dest = 'phenotypes_in_mesh', default = 'true', required = False, help = 'Malha com diferentes fenótipos (true) ou não (false)')

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
min_z = int(arguments.min_z)
max_z = int(arguments.max_z)
period_stim1 = int(arguments.period_stim1)
num_stim1 = int(arguments.num_stim1)
output_dir_save = arguments.output_dir_save
output_dir_restore = arguments.output_dir_restore
dt_pde = float(arguments.dt_pde)
dt_ode = float(arguments.dt_ode)
nome_arquivo = arguments.nome_arquivo
use_gpu = arguments.use_gpu
dir_protocolo = arguments.dir_protocolo
sigma_c = float(arguments.sigma_c)
discretization = float(arguments.discretization)
num_extra_fields = int(arguments.num_extra_fields)
main_function_domain = arguments.main_function_domain
main_function_assembly_matrix = arguments.main_function_assembly_matrix
fibers_in_mesh = arguments.fibers_in_mesh
phenotypes_in_mesh = bool(arguments.phenotypes_in_mesh)

# Número Máximo de Estímulos
stim_max = 4

# Definição dos Sigma_Factor Avaliados
sigmas_factor = [sigma_factor_0]
fator = 1

delete_dir(dir_protocolo)
create_dir(dir_protocolo)

caminho_arquivo = dir_protocolo + "/" + nome_arquivo
 
with open(caminho_arquivo, mode = 'w', newline = '') as csv_file:
  csv_writer = csv.writer(csv_file, delimiter = ',')
  csv_writer.writerow(['Sigma_Factor', 'Sigma', 'Sigma_C', 'Stimulation_Index', 'Interval', 'Element_Reentry_Rate', 'Element_Block_Rate', 'Element_Normal_Rate', 'Event_Type', 'Runtime'])

for sigma_factor in sigmas_factor:
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

  while not end:

      if save:
          simulation_time = stim[-1] + 100

          save_state = '[save_state]\nmain_function = save_simulation_state_with_activation_times\nlibrary_file = ./shared_libs/libdefault_save_state.so\noutput_dir = ' +dir_protocolo+ output_dir_save
          restore_state = ';[restore_state]\n;main_function = restore_simulation_state_with_activation_times\n;library_file = ./shared_libs/libdefault_restore_state.so\n;input_dir = '+dir_protocolo + output_dir_save

          output_dir = dir_protocolo + output_dir_save

          delete_dir(output_dir)

          create_dir(output_dir)

          if phenotypes_in_mesh:
              extra_data = '[extra_data]\nlibrary_file = shared_libs/libdefault_extra_data.so\nmain_function = set_extra_data_for_scv_mesh'
          else:
              extra_data = ';[extra_data]\n;library_file = shared_libs/libdefault_extra_data.so\n;main_function = set_extra_data_for_scv_mesh'

          ini = generateIni(stim, simulation_time, output_dir, save_state, restore_state, print_rate, mesh_print_rate, sigma_factor, sigma, num_volumes, mesh_file, library_file, min_x, max_x, min_y, max_y, min_z, max_z, num_stim1, dt_pde, dt_ode, use_gpu, sigma_c, discretization, num_extra_fields, main_function_domain, main_function_assembly_matrix, fibers_in_mesh, extra_data)

          file = open(output_dir + "protocolo.ini", 'w')
          file.write(ini)
          file.close()

          start_time = time.time()

          cmd = "bin/MonoAlg3D -c " + output_dir + "protocolo.ini"
          print(cmd)

          process = subprocess.Popen(cmd, shell = True)
          process.wait()

          save = False

          end_time = time.time()

          with open(caminho_arquivo, mode = 'a', newline = '') as csv_file:
           csv_writer = csv.writer(csv_file, delimiter = ',')
           csv_writer.writerow([sigma_factor, sigma, sigma_c, '-', '-', '-', '-', '-', '-', (end_time - start_time) / 60])

      else:
          simulation_time = stim[-1] + 800

          save_state = ';[save_state]\n;main_function = save_simulation_state_with_activation_times\n;library_file = ./shared_libs/libdefault_save_state.so\n;output_dir = '+dir_protocolo + output_dir_save
          restore_state = '[restore_state]\nmain_function = restore_simulation_state_with_activation_times\nlibrary_file = ./shared_libs/libdefault_restore_state.so\ninput_dir = ' +dir_protocolo+ output_dir_save

          output_dir = dir_protocolo + output_dir_restore

          delete_dir(output_dir)

          create_dir(output_dir)

          if phenotypes_in_mesh:
              extra_data = '[extra_data]\nlibrary_file = shared_libs/libdefault_extra_data.so\nmain_function = set_extra_data_for_scv_mesh'
          else:
              extra_data = ';[extra_data]\n;library_file = shared_libs/libdefault_extra_data.so\n;main_function = set_extra_data_for_scv_mesh'

          deltas = [stim[-1] + 380 - 10 * i for i in range(19)]
          print(deltas)

          for d in range(len(deltas)):   
              f = output_dir + str(deltas[d]) + '/'
              create_dir(f)

              if d == 0:
                  stim.append(deltas[d])
              else:
                  stim[-1] = deltas[d]

              ini = generateIni(stim, simulation_time, f, save_state, restore_state, print_rate, mesh_print_rate, sigma_factor, sigma, num_volumes, mesh_file, library_file, min_x, max_x, min_y, max_y, min_z, max_z, num_stim1, dt_pde, dt_ode, use_gpu, sigma_c, discretization, num_extra_fields, main_function_domain, main_function_assembly_matrix, fibers_in_mesh, extra_data)

              file = open(f + "protocolo.ini", 'w')
              file.write(ini)
              file.close()

              start_time = time.time()

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
                      index = line.find(" ")
                      value = -1
                      if index != -1:
                          value_part = line[index:].strip()
                          value = float(value_part)
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

              end_time = time.time()

              with open(caminho_arquivo, mode = 'a', newline = '') as csv_file:
               csv_writer = csv.writer(csv_file, delimiter = ',')
               csv_writer.writerow([sigma_factor, sigma, sigma_c, len(stim) - num_stim1 + 1, stim[-1] - stim[-2], taxa_espiral, taxa_bloqueio, taxa_normal, ('Bloqueio' if taxa_bloqueio > 50.0 else 'Propagação_Normal') if taxa_espiral<10 else 'Espiral', (end_time - start_time) / 60])

              if taxa_bloqueio > 50.0:
                  save = True														
                  stim[-1] += 20

                  break
          i += 1

      if i > stim_max:
        end = True