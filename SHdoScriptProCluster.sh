#!/bin/bash -l
#SBATCH --job-name="protocolo_paciente_2_2"
#SBATCH --account="d411"
#SBATCH --time=72:00:00
#SBATCH --nodes=1

#SBATCH --account=d411-hector
#SBATCH --partition=gpu
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1

module load nvidia/nvhpc
module load gcc

source /work/d411/d411/rodrigoweber/MonoAlg3D_C/myenv/bin/activate

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export CRAY_CUDA_MPS=1

srun python3 /work/d411/d411/rodrigoweber/MonoAlg3D_C/protocolo.py --sf 0.025 --s 0.0001951219512 --nv 1173012 --mf ./meshes/Paciente_2_500um.alg --min_x 78750 --max_x 80750 --min_y 50250 --max_y 52250 --min_z 58750 --max_z 60750 --ps1 400 --d 500 --nef 11 --dp /work/d411/d411/rodrigoweber/MonoAlg3D_C/Paciente2_400ms_0_025/

