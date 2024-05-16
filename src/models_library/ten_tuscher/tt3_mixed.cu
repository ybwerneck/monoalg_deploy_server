#include "../../gpu_utils/gpu_utils.h"
#include "../../monodomain/constants.h"
#include "tt3_mixed.h"
#include <stddef.h>

extern "C" SET_ODE_INITIAL_CONDITIONS_GPU(set_model_initial_conditions_gpu) {

    char *cell_type;
    #ifdef ENDO
        cell_type = strdup("ENDO");
    #endif

    #ifdef EPI
        cell_type = strdup("EPI");
    #endif

    #ifdef MCELL
        cell_type = strdup("MCELL");
    #endif

    log_info("Using ten Tusscher 3 %s GPU model\n", cell_type);

    free(cell_type);

    uint32_t num_volumes = solver->original_num_cells;

    // execution configuration
    const int GRID  = (num_volumes + BLOCK_SIZE - 1)/BLOCK_SIZE;

    size_t size = num_volumes*sizeof(real);

    check_cuda_error(cudaMallocPitch((void **) &(solver->sv), &pitch_h, size, (size_t )NEQ));
    check_cuda_error(cudaMemcpyToSymbol(pitch, &pitch_h, sizeof(size_t)));

    //kernel_set_model_inital_conditions <<<GRID, BLOCK_SIZE>>>(solver->sv, mapping_device, num_volumes);
    kernel_set_model_inital_conditions <<<GRID, BLOCK_SIZE>>>(solver->sv, NULL, num_volumes);

    check_cuda_error( cudaPeekAtLastError() );
    cudaDeviceSynchronize();
    return pitch_h;
}

extern "C" SOLVE_MODEL_ODES(solve_model_odes_gpu) {

    size_t num_cells_to_solve = ode_solver->num_cells_to_solve;
    uint32_t * cells_to_solve = ode_solver->cells_to_solve;
    real *sv = ode_solver->sv;
    real dt = ode_solver->min_dt;
    uint32_t num_steps = ode_solver->num_steps;

    // execution configuration
    const int GRID  = ((int)num_cells_to_solve + BLOCK_SIZE - 1)/BLOCK_SIZE;

    size_t stim_currents_size = sizeof(real)*num_cells_to_solve;
    size_t cells_to_solve_size = sizeof(uint32_t)*num_cells_to_solve;

    real *stims_currents_device;
    check_cuda_error(cudaMalloc((void **) &stims_currents_device, stim_currents_size));
    check_cuda_error(cudaMemcpy(stims_currents_device, stim_currents, stim_currents_size, cudaMemcpyHostToDevice));

    uint32_t *cells_to_solve_device = NULL;
    if(cells_to_solve != NULL) {
        check_cuda_error(cudaMalloc((void **) &cells_to_solve_device, cells_to_solve_size));
        check_cuda_error(cudaMemcpy(cells_to_solve_device, cells_to_solve, cells_to_solve_size, cudaMemcpyHostToDevice));
    }

    real *fibrosis_device;
    real *fibs = NULL;
    int num_extra_parameters = 7;
    real extra_par[num_extra_parameters];

    size_t extra_parameters_size = num_extra_parameters * sizeof(real);

    real *extra_parameters_device;
    real fibs_size = num_cells_to_solve*sizeof(real);

    //struct extra_data_for_fibrosis* extra_data_from_cpu = (struct extra_data_for_fibrosis*)ode_solver->ode_extra_data;

    bool deallocate = false;

    //if(ode_solver->ode_extra_data) {
    if(0){
        //fibs = extra_data_from_cpu->fibrosis;
        //extra_par[0] = extra_data_from_cpu->atpi;
        //extra_par[1] = extra_data_from_cpu->Ko;
        //extra_par[2] = extra_data_from_cpu->Ki;
        //extra_par[3] = extra_data_from_cpu->Vm_modifier;
        //extra_par[4] = extra_data_from_cpu->GNa_multiplicator;
        //extra_par[5] = extra_data_from_cpu->GCaL_multiplicator;
        //extra_par[6] = extra_data_from_cpu->INaCa_multiplicator;
    }
    else {
        extra_par[0] = 6.8f;
        extra_par[1] = 5.4f;
        extra_par[2] = 138.3f;
        extra_par[3] = 0.0;
        extra_par[4] = 1.0f;
        extra_par[5] = 1.0f;
        extra_par[6] = 1.0f;

        fibs = (real*) malloc(fibs_size);

		for(uint64_t i = 0; i < num_cells_to_solve; i++) {
			fibs[i] = 1.0;
		}

        deallocate = true;
    }

    check_cuda_error(cudaMalloc((void **) &extra_parameters_device, extra_parameters_size));
    check_cuda_error(cudaMemcpy(extra_parameters_device, extra_par, extra_parameters_size, cudaMemcpyHostToDevice));

    check_cuda_error(cudaMalloc((void **) &fibrosis_device, fibs_size));
    check_cuda_error(cudaMemcpy(fibrosis_device, fibs, fibs_size, cudaMemcpyHostToDevice));

uint32_t *mapping = NULL;
    uint32_t *mapping_device = NULL;
    if(ode_solver->ode_extra_data) 
    {
	// log_info("-------------   MAPPING!!!    --------------\n\n");
        mapping = (uint32_t*)ode_solver->ode_extra_data;
        check_cuda_error(cudaMalloc((void **)&mapping_device, ode_solver->extra_data_size));
        check_cuda_error(cudaMemcpy(mapping_device, mapping, ode_solver->extra_data_size, cudaMemcpyHostToDevice));
    }
    else 
    {
        log_error_and_exit("You need to specify a mask function when using a mixed model!\n");
    }
if(mapping_device) check_cuda_error(cudaFree(mapping_device));

    solve_gpu<<<GRID, BLOCK_SIZE>>>(dt, sv, stims_currents_device, cells_to_solve_device, num_cells_to_solve, num_steps, fibrosis_device, extra_parameters_device,mapping_device);

    check_cuda_error( cudaPeekAtLastError() );

    check_cuda_error(cudaFree(stims_currents_device));
    check_cuda_error(cudaFree(fibrosis_device));
    check_cuda_error(cudaFree(extra_parameters_device));

    if(cells_to_solve_device) check_cuda_error(cudaFree(cells_to_solve_device));

    if(deallocate) free(fibs);
}

__global__ void kernel_set_model_inital_conditions(real *sv, real*IC, int num_volumes)
{
    // Thread ID
    int threadID = blockDim.x * blockIdx.x + threadIdx.x;

    if(threadID < num_volumes) {

        *((real *) ((char *) sv + pitch * 0) + threadID) = INITIAL_V;   // V;       millivolt
        *((real *) ((char *) sv + pitch * 1) + threadID) = 0.0f; //M
        *((real *) ((char *) sv + pitch * 2) + threadID) = 0.75; //H
        *((real *) ((char *) sv + pitch * 3) + threadID) = 0.75; //J
        *((real *) ((char *) sv + pitch * 4) + threadID) = 0.0f; //Xr1
        *((real *) ((char *) sv + pitch * 5) + threadID) = 0.0f; //Xs
        *((real *) ((char *) sv + pitch * 6) + threadID) = 1.0; //S
        *((real *) ((char *) sv + pitch * 7) + threadID) = 1.0; //F
        *((real *) ((char *) sv + pitch * 8) + threadID) = 1.0; //F2
        *((real *) ((char *) sv + pitch * 9) + threadID) = 0.0; //D_INF
        *((real *) ((char *) sv + pitch * 10) + threadID) = 0.0; //R_INF
        *((real *) ((char *) sv + pitch * 11) + threadID) = 0.0; //Xr2_INF
    }
}

// Solving the model for each cell in the tissue matrix ni x nj
__global__ void solve_gpu(real dt, real *sv, real* stim_currents,
                          uint32_t *cells_to_solve, uint32_t num_cells_to_solve,
                          int num_steps, real *fibrosis, real *extra_parameters,uint32_t *mapping)
{
    int threadID = blockDim.x * blockIdx.x + threadIdx.x;
    int sv_id;

    // Each thread solves one cell model
    if(threadID < num_cells_to_solve) {
        if(cells_to_solve)
            sv_id = cells_to_solve[threadID];
        else
            sv_id = threadID;

        real rDY[NEQ];

        for (int n = 0; n < num_steps; ++n) {


		if (mapping[sv_id] == 0) {
			RHS_gpu(sv, rDY, stim_currents[threadID], sv_id, dt, fibrosis[threadID], extra_parameters,0);
		}
		else if(mapping[sv_id] == 1){
			RHS_gpu(sv, rDY, stim_currents[threadID], sv_id, dt, fibrosis[threadID], extra_parameters,1);
		}
            	else {
			RHS_gpu(sv, rDY, stim_currents[threadID], sv_id, dt, fibrosis[threadID], extra_parameters,2);
		}


            //RHS_gpu(sv, rDY, stim_currents[threadID], sv_id, dt, fibrosis[threadID], extra_parameters);

            *((real*)((char*)sv) + sv_id) = dt*rDY[0] + *((real*)((char*)sv) + sv_id);

            for(int i = 1; i < NEQ; i++) {
                *((real*)((char*)sv + pitch * i) + sv_id) = rDY[i];
            }

        }

    }
}


inline __device__ void RHS_gpu(real *sv_, real *rDY_, real stim_current, int threadID_, real dt, real fibrosis, real *extra_parameters, int type_cell) {

    //fibrosis = 0 means that the cell is fibrotic, 1 is not fibrotic. Anything between 0 and 1 means border zone
    const real svolt = *((real*)((char*)sv_ + pitch * 0) + threadID_);
    const real sm   = *((real*)((char*)sv_ + pitch * 1) + threadID_);
    const real sh   = *((real*)((char*)sv_ + pitch * 2) + threadID_);
    const real sj   = *((real*)((char*)sv_ + pitch * 3) + threadID_);
    const real sxr1 = *((real*)((char*)sv_ + pitch * 4) + threadID_);
    const real sxs  = *((real*)((char*)sv_ + pitch * 5) + threadID_);
    const real ss   = *((real*)((char*)sv_ + pitch * 6) + threadID_);
    const real sf  = *((real*)((char*)sv_ + pitch * 7) + threadID_);
    const real sf2  = *((real*)((char*)sv_ + pitch * 8) + threadID_);
    const real D_INF  = *((real*)((char*)sv_ + pitch * 9) + threadID_);
    const real R_INF  = *((real*)((char*)sv_ + pitch * 10) + threadID_);
    const real Xr2_INF  = *((real*)((char*)sv_ + pitch * 11) + threadID_);

    //FUCK YOU NVCC
    #include "tt3_mixed_common.inc.c"


}
