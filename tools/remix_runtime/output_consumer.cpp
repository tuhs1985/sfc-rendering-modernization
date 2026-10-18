#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "output_channel.h"
// Thin x86 consumer: no Remix SDK or x64 DLL loaded into this process.
int wmain(int argc,wchar_t** argv){
  if(argc!=3||wcscmp(argv[1],L"--consumer"))return 2;
  try{return output_probe::consume(argv[2]);}catch(...){return 3;}
}
