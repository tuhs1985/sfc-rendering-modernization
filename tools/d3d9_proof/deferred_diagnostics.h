// Owned worker ONLY. Fixed memory;no per-frame disk/pipe writes or allocation.
// Flush at orderly teardown. A process crash may lose buffered diagnostics.
#pragma once
#include <algorithm>
#include <cstring>
#include <memory>
#include <ostream>
#include <streambuf>
#include <stdexcept>
class DeferredDiagnostics final:public std::streambuf {
 std::ostream& stream;std::streambuf* original=nullptr;
 std::unique_ptr<char[]> data;size_t capacity=0,used=0,dropped=0;
 std::streamsize xsputn(const char* text,std::streamsize count)override{
  if(count<=0)return 0;
  const auto n=static_cast<size_t>(count),keep=(std::min)(n,capacity-used);
  if(keep)std::memcpy(data.get()+used,text,keep);
  used+=keep;dropped+=n-keep;return count;
 }
 int_type overflow(int_type value)override{
  if(traits_type::eq_int_type(value,traits_type::eof()))return traits_type::not_eof(value);
  const char c=traits_type::to_char_type(value);xsputn(&c,1);return value;
 }
 int sync()override{return 0;}
public:
 DeferredDiagnostics(std::ostream& out,bool enabled,size_t bytes=1024*1024):stream(out){
  if(!enabled)return;
  if(!bytes||bytes>2*1024*1024)throw std::invalid_argument("Diagnostic buffer bound");
  data=std::make_unique<char[]>(bytes);capacity=bytes;original=stream.rdbuf(this);
 }
 DeferredDiagnostics(const DeferredDiagnostics&)=delete;
 DeferredDiagnostics& operator=(const DeferredDiagnostics&)=delete;
 void finish(){
  if(!original)return;
  stream.rdbuf(original);
  original->sputn(data.get(),static_cast<std::streamsize>(used));
  if(dropped){const char warning[]="\nDIAGNOSTICS_TRUNCATED fixed_capacity=1\n";original->sputn(warning,sizeof(warning)-1);}
  original->pubsync();
  original=nullptr;
 }
 ~DeferredDiagnostics(){finish();}
 size_t retained()const{return used;}
 size_t discarded()const{return dropped;}
};
