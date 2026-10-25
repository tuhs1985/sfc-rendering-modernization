// Included inside survey_events; only callback-supplied descriptors are read.
enum Extra:uint32_t {Descriptors=24,VertexBuffers,IndexBuffer,Scissor,Sampler,
 PipelineDesc,PipelineEnd,Origin,OriginStats,Tables,Constants};
inline std::atomic<uint64_t> drawOrdinal{0};
inline std::atomic<unsigned> stackBudget{0};
inline std::atomic<uint32_t> originEligible{0},originCaptured{0},originEmpty{0},originBudgetSkipped{0};
inline std::atomic<uint64_t> originTicks{0};
inline void origin(a::command_list* c,uint64_t parent){
 if(!parent)return;
 const auto ordinal=drawOrdinal.fetch_add(1);if(ordinal%8)return;
 ++originEligible;const auto used=stackBudget.fetch_add(1);
 if(used>=64){++originBudgetSkipped;return;}
 const auto began=return_path::now();void* addresses[32]{};const auto count=CaptureStackBackTrace(1,32,addresses,nullptr);originTicks.fetch_add(return_path::now()-began);
 if(!count){++originEmpty;return;}++originCaptured;
 for(unsigned first=0;first<count;first+=8){
  std::array<uint64_t,11> args{parent,first,count};
  for(unsigned i=0;i<8&&first+i<count;++i)args[3+i]=reinterpret_cast<uintptr_t>(addresses[first+i]);
  trace.emit(Origin,label(c),label(c->get_device()),args);
 }
}
inline void stats(a::command_queue* q,a::swapchain*,const a::rect*,const a::rect*,uint32_t,const a::rect*){
 trace.emit(OriginStats,label(q),label(q->get_device()),{originEligible.exchange(0),originCaptured.exchange(0),originEmpty.exchange(0),originBudgetSkipped.exchange(0),originTicks.exchange(0)});
 stackBudget=0;
}
inline void descriptors(a::command_list* c,a::shader_stage stages,a::pipeline_layout layout,uint32_t parameter,const a::descriptor_table_update& u){
 const auto count=(std::min)(u.count,256u);
 for(unsigned i=0;i<count;++i){
  uint64_t first=0,second=0,third=0;
  if(u.type==a::descriptor_type::shader_resource_view||u.type==a::descriptor_type::unordered_access_view)first=static_cast<const a::resource_view*>(u.descriptors)[i].handle;
  else if(u.type==a::descriptor_type::sampler)first=static_cast<const a::sampler*>(u.descriptors)[i].handle;
  else if(u.type==a::descriptor_type::sampler_with_resource_view){const auto& v=static_cast<const a::sampler_with_resource_view*>(u.descriptors)[i];first=v.view.handle;second=v.sampler.handle;}
  else if(u.type==a::descriptor_type::constant_buffer){const auto& v=static_cast<const a::buffer_range*>(u.descriptors)[i];first=v.buffer.handle;second=v.offset;third=v.size;}
  trace.emit(Descriptors,label(c),label(c->get_device()),{static_cast<uint64_t>(stages),layout.handle,parameter,u.binding,u.array_offset+i,static_cast<uint64_t>(u.type),first,second,third,u.count,count});
 }
}
inline void vertices(a::command_list* c,uint32_t first,uint32_t count,const a::resource* buffers,const uint64_t* offsets,const uint32_t* strides){
 for(unsigned i=0;i<(std::min)(count,32u);++i)trace.emit(VertexBuffers,label(c),label(c->get_device()),{first+i,buffers[i].handle,offsets?offsets[i]:0,strides?strides[i]:0,count});
}
inline void indices(a::command_list* c,a::resource buffer,uint64_t offset,uint32_t size){trace.emit(IndexBuffer,label(c),label(c->get_device()),{buffer.handle,offset,size});}
inline void scissors(a::command_list* c,uint32_t first,uint32_t count,const a::rect* values){
 for(unsigned i=0;i<(std::min)(count,16u);++i){const auto& r=values[i];trace.emit(Scissor,label(c),label(c->get_device()),{first+i,static_cast<uint32_t>(r.left),static_cast<uint32_t>(r.top),static_cast<uint32_t>(r.right),static_cast<uint32_t>(r.bottom),count});}
}
inline void sampler(a::device* d,const a::sampler_desc& s,a::sampler h){
 trace.emit(Sampler,h.handle,label(d),{static_cast<uint64_t>(s.filter),static_cast<uint64_t>(s.address_u),static_cast<uint64_t>(s.address_v),static_cast<uint64_t>(s.address_w),bits(s.mip_lod_bias),bits(s.max_anisotropy),static_cast<uint64_t>(s.compare_op),bits(s.min_lod),bits(s.max_lod)},true);
}
inline void pipelineDesc(a::device* d,a::pipeline_layout layout,uint32_t count,const a::pipeline_subobject* objects,a::pipeline p){
 for(unsigned i=0;i<(std::min)(count,64u);++i){const auto& o=objects[i];std::array<uint64_t,11> v{static_cast<uint64_t>(o.type),o.count,layout.handle,count};
  if(o.count==1&&o.data){
   if(o.type==a::pipeline_subobject_type::depth_stencil_state){const auto& s=*static_cast<const a::depth_stencil_desc*>(o.data);v[4]=s.depth_enable;v[5]=s.depth_write_mask;v[6]=static_cast<uint64_t>(s.depth_func);v[7]=s.stencil_enable;}
   else if(o.type==a::pipeline_subobject_type::blend_state){const auto& s=*static_cast<const a::blend_desc*>(o.data);v[4]=s.blend_enable[0];v[5]=static_cast<uint64_t>(s.source_color_blend_factor[0]);v[6]=static_cast<uint64_t>(s.dest_color_blend_factor[0]);v[7]=static_cast<uint64_t>(s.color_blend_op[0]);v[8]=static_cast<uint64_t>(s.source_alpha_blend_factor[0]);v[9]=static_cast<uint64_t>(s.dest_alpha_blend_factor[0]);v[10]=s.render_target_write_mask[0];}
   else if(o.type==a::pipeline_subobject_type::rasterizer_state){const auto& s=*static_cast<const a::rasterizer_desc*>(o.data);v[4]=static_cast<uint64_t>(s.cull_mode);v[5]=static_cast<uint64_t>(s.fill_mode);v[6]=s.front_counter_clockwise;v[7]=bits(s.depth_bias);v[8]=s.scissor_enable;}
   else if(o.type==a::pipeline_subobject_type::primitive_topology)v[4]=static_cast<uint64_t>(*static_cast<const a::primitive_topology*>(o.data));
  }
  // Shader and input-layout contents deliberately never read.
  trace.emit(PipelineDesc,p.handle,label(d),v,true);
 }
}
inline void pipelineEnd(a::device* d,a::pipeline p){trace.emit(PipelineEnd,p.handle,label(d),{},true);}
inline void tables(a::command_list* c,a::shader_stage stages,a::pipeline_layout layout,uint32_t first,uint32_t count,const a::descriptor_table* values){for(unsigned i=0;i<(std::min)(count,32u);++i)trace.emit(Tables,label(c),label(c->get_device()),{static_cast<uint64_t>(stages),layout.handle,first+i,values[i].handle,count});}
inline void constants(a::command_list* c,a::shader_stage stages,a::pipeline_layout layout,uint32_t parameter,uint32_t first,uint32_t count,const void*){
 // Identities/ranges only, never read constant-buffer or other resource contents.
 trace.emit(Constants,label(c),label(c->get_device()),{static_cast<uint64_t>(stages),layout.handle,parameter,first,count});
}
inline void extraEvents(bool add){
#define S_EVENT(name,fn) if(add)reshade::register_event<reshade::addon_event::name>(fn);else reshade::unregister_event<reshade::addon_event::name>(fn)
 S_EVENT(push_descriptors,descriptors);S_EVENT(bind_vertex_buffers,vertices);S_EVENT(bind_index_buffer,indices);S_EVENT(bind_scissor_rects,scissors);S_EVENT(init_sampler,sampler);S_EVENT(init_pipeline,pipelineDesc);S_EVENT(destroy_pipeline,pipelineEnd);S_EVENT(bind_descriptor_tables,tables);S_EVENT(push_constants,constants);S_EVENT(present,stats);
#undef S_EVENT
}
