# cuDNN-sample

Some cuDNN sample codes provided by Nvidia as well as some home-made codes.

## cuDNN static linking

There is no official guide on how to link cuDNN statically. However, I found an official guide on how to [link cuBLAS statically](https://docs.nvidia.com/cuda/cublas/index.html). Actually, nVidia takes the static library as a different library (with a different name).

So, you need to use the following commands to link cuDNN statically.

```bash
nvcc <source> -lcudnn_static -o <target>
```