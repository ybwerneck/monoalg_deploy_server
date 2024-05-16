#!/bin/bash

FIND_CUDA () {
	#CUDA RELATED VARIABLES
	CUDA_LIBRARY_PATH="/usr/local/cuda/lib64/"
	CUDA_INCLUDE_PATH="/usr/local/cuda/include/"
	NVCC="/usr/local/cuda/bin/nvcc"
	CUDA_FOUND=""

	if [ -z "$CUDA_LIBRARY_PATH" ]; then
		CUDA_LIBRARY_PATH=$(dirname "$(ldconfig -p | grep libcudart | awk '{print $4}' | head -n 1 | head -c -5)" 2> /dev/null)
	fi

	if [ -z "$CUDA_INCLUDE_PATH" ]; then

		if [ "$OS" == "Manjaro Linux" ]; then
			CUDA_INCLUDE_PATH="/opt/cuda/include"
		elif [ "$OS" == "Fedora" ]; then
			CUDA_INCLUDE_PATH="/usr/local/cuda/include"
			CUDA_LIBRARY_PATH="/usr/local/cuda/lib64"
		else
            if [ "$CI" = true ]; then
			    CUDA_INCLUDE_PATH='/usr/local/cuda/include'
            else
			    CUDA_INCLUDE_PATH='/usr/include/'
            fi
		fi
	fi

	if [ -z "$NVCC" ]; then
		NVCC=$(command -v nvcc | xargs) #in some systems command stops the script
	fi

	if [ ! -d "$CUDA_LIBRARY_PATH" ] || [ ! -d "$CUDA_INCLUDE_PATH" ] || [ ! -f "$NVCC" ]; then

		if [ ! -d "$CUDA_LIBRARY_PATH" ] || [ ! -f "$CUDA_LIBRARY_PATH/libcudart.so" ]; then

			if [ -z "$CUDA_LIBRARY_PATH" ]; then
				PRINT_WARN "CUDA_LIBRARY_PATH variable is empty. CUDA code will not be compiled!"
			else
				PRINT_WARN "CUDA_LIBRARY_PATH set as $CUDA_LIBRARY_PATH is not a valid CUDA library path. CUDA code will not be compiled!"
			fi

			PRINT_WARN "You can change the CUDA_LIBRARY_PATH variable manually in the file $OPTIONS_FILE"
			echo
		fi

		if [ ! -d "$CUDA_INCLUDE_PATH" ] ||  [ ! -f "$CUDA_INCLUDE_PATH/cuda_runtime.h" ]; then

			if [ -z "$CUDA_INCLUDE_PATH" ]; then
				PRINT_WARN "CUDA_INCLUDE_PATH variable is empty. CUDA code will not be compiled!"
			else
				PRINT_WARN "CUDA_INCLUDE_PATH set as $CUDA_INCLUDE_PATH is not a valid CUDA include path. CUDA code will not be compiled!"
			fi

			PRINT_WARN "You can change the CUDA_INCLUDE_PATH variable manually in the file $OPTIONS_FILE"
			echo
		fi

		if [ ! -f "$NVCC" ]; then
			PRINT_WARN "CUDA compiler set as $NVCC not found. CUDA code will not be compiled!"
			PRINT_WARN "You can change the NVCC variable manually in the file $OPTIONS_FILE"
		fi
	else
		CUDA_FOUND='y'
		CUDA_LIBRARIES="cudart"
		export CUDA_FOUND
		export CUDA_LIBRARIES
	fi

}

FIND_LIB() {

	LIB=$1

	PKG_CONFIG=$(command -v pkg-config)

	LIB_NAME=$(printf '%s\n' "$LIB" | awk '{ print toupper($0) }')
    LIB_FOUND="$LIB_NAME"_FOUND
	LIB_LIBRARY_PATH="$LIB_NAME"_LIBRARY_PATH
	LIB_INCLUDE_PATH="$LIB_NAME"_INCLUDE_PATH
	LIB_LIBRARIES="$LIB_NAME"_LIBRARIES

	if [ -z "$PKG_CONFIG" ]; then
	    printf -v "$LIB_FOUND" ""
	else
		if "$PKG_CONFIG" --exists "$LIB"; then
			printf -v "$LIB_FOUND" "y"

			TMP=$($PKG_CONFIG --libs-only-L "$LIB")
			printf -v "$LIB_LIBRARY_PATH" "%s" "${TMP:2}"

			LIB_INCLUDE_PATH=$($PKG_CONFIG --cflags-only-I "$LIB")

			LIBS=$($PKG_CONFIG --libs-only-l "$LIB")

			if [ -n "$LIBS" ]; then
				printf -v "$LIB_LIBRARIES" ""
				for i in $LIBS; do
					i=${i:2}
					printf -v "$LIB_LIBRARIES" "%s" "${!LIB_LIBRARIES} $i"
				done
			fi
		fi
	fi
}

FIND_CRITERION() {
	FIND_LIB "criterion"
}

FIND_MPI () {
	FIND_LIB "ompi"
	MPI_FOUND=$OMPI_FOUND
	MPI_LIBRARIES=$OMPI_LIBRARIES
	MPI_LIBRARY_PATH=$OMPI_LIBRARY_PATH
	MPI_INCLUDE_PATH=$OMPI_INCLUDE_PATH
}
