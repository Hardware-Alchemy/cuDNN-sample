#include <cudnn.h>

#include "common.hpp"

int main(int argc, char const *argv[]) {
  
  cudnnHandle_t cudnn;
  checkCUDNN(cudnnCreate(&cudnn));

  printf("Hello World!\n");

  return 0;
}