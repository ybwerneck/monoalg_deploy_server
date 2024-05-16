#include <mpi.h>
#include <stdlib.h>
#include <string.h>


#include "3dparty/ini_parser/ini.h"
#include "3dparty/ini_parser/ini_file_sections.h"
#include "3dparty/sds/sds.h"
#include "3dparty/stb_ds.h"
#include "alg/grid/grid.h"
#include "config_helpers/config_helpers.h"
#include "logger/logger.h"
#include "monodomain/monodomain_solver.h"
#include "ode_solver/ode_solver.h"
#include "utils/batch_utils.h"
#include "utils/file_utils.h"

int main(int argc, char **argv) {

    MPI_Init(&argc, &argv);

    int rank, num_proccess, num_max_proc;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_proccess);

    int simulation_number_start;
    int num_simulations = 0;

    char *output_folder;

    bool skip_existing;

    struct batch_options *batch_options;
    batch_options = new_batch_options();

    parse_batch_options(argc, argv, batch_options);

    if (ini_parse(batch_options->batch_config_file, parse_batch_config_file, batch_options) < 0) {
        fprintf(stderr, "Error: Can't load the config file %s\n", batch_options->batch_config_file);
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
    }

    skip_existing = batch_options->skip_existing_run;

    if (rank == 0) {
        create_dir(batch_options->output_folder);
    }

    struct simulation *all_simulations = generate_all_simulations(batch_options->config_to_change,
                                                                  batch_options->num_simulations);

    if(rank == 0)
        print_simulations(all_simulations);

    int total_simulations = arrlen(all_simulations);

    if (num_proccess > total_simulations) {
        num_max_proc = total_simulations;
    } else {
        num_max_proc = num_proccess;
    }

    if (rank < num_max_proc) {
        num_simulations = total_simulations / num_max_proc;
    }

    int last_rank_extra = total_simulations % num_max_proc;

    if (rank == num_max_proc - 1) {
        num_simulations += last_rank_extra;
    }

    simulation_number_start = rank * num_simulations;

    struct user_options *options;
    options = new_user_options();

    struct grid *the_grid;
    struct monodomain_solver *monodomain_solver;
    struct ode_solver *ode_solver;


    ini_parse("dontdelete.ini", parse_config_file, options) ;   // MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
    

    if (!options->save_mesh_config) {
        shput_dup_value(options->save_mesh_config->config_data, "output_dir", "batch_run");
    }

    char *out_dir_name = strdup("./");
    GET_PARAMETER_STRING_VALUE_OR_USE_DEFAULT(out_dir_name, options->save_mesh_config, "output_dir");
    char *initial_out_dir_name = strdup(out_dir_name);

    set_no_stdout(options->quiet);

    output_folder = batch_options->output_folder;
    options->show_gui = false;

    MPI_Barrier(MPI_COMM_WORLD);

    if (num_simulations == 0) {
        MPI_Finalize();
        return EXIT_SUCCESS;
    }

    for (int s = simulation_number_start; s < simulation_number_start + num_simulations; s++) {
        the_grid = new_grid();
        monodomain_solver = new_monodomain_solver();
        ode_solver = new_ode_solver();

        struct simulation simulation = all_simulations[s];
        int config_n = arrlen(simulation.parameters);

        sds new_out_dir_name = sdscatprintf(sdsempty(), "%s/%s_run_%d", output_folder, initial_out_dir_name,
                                            simulation.run_number);

        for (int n = 0; n < config_n; n++) {
            char *new_value = strdup(simulation.parameters[n].value);
            char *tmp = new_value;

            //If we have / on the value we need to change to another char...
            for (; *tmp; tmp++) {
                if (*tmp == '/') *tmp = '_';
            }

            new_out_dir_name = sdscatprintf(new_out_dir_name, "_%s_%s", simulation.parameters[n].name, new_value);
            free(new_value);

        }
       
           char command[200];  // Adjust the size accordingly

        sprintf(command, "echo Executando   %s no rank %d", new_out_dir_name,rank);

        system(command);

        sprintf(command, "mkdir %s", new_out_dir_name);

        system(command);

        sprintf(command, "python  %s --sc %f  --sf %f --os /save --or /restore --nf resultado.csv --dp %s",batch_options->initial_config,
         strtof(simulation.parameters[0].value,NULL),strtof(simulation.parameters[1].value,NULL),  new_out_dir_name);

        system(command);
        free_current_simulation_resources(monodomain_solver, ode_solver, the_grid);
        //a ideia seria chamar aqui o script, apaguei todo o resto ja

    }

    free_batch_options(batch_options);
    free_user_options(options);
    free(initial_out_dir_name);

    MPI_Finalize();

    return EXIT_SUCCESS;
}
