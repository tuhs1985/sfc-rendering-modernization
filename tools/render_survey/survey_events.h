#pragma once
#include "survey_trace.h"
namespace survey_events {
namespace a=reshade::api;namespace b=survey_trace;
inline b::Trace trace;
inline void origin(a::command_list*,uint64_t);
template<class T> uint64_t label(T* p){return reinterpret_cast<uintptr_t>(p);}
inline void device(a::device* p){trace.emit(b::Device,label(p),label(p),{static_cast<uint64_t>(p->get_api())},true);}
inline void deviceEnd(a::device* p){trace.emit(b::DeviceEnd,label(p),label(p),{},true);}
inline void resource(a::device* p,const a::resource_desc& d,const a::subresource_data*,a::resource_usage state,a::resource r){
 std::array<uint64_t,11> v{static_cast<uint64_t>(d.type),static_cast<uint64_t>(d.usage),static_cast<uint64_t>(d.heap),static_cast<uint64_t>(d.flags),static_cast<uint64_t>(state)};
 if(d.type==a::resource_type::buffer){v[5]=d.buffer.size;v[6]=d.buffer.stride;}
 else {v[5]=d.texture.width;v[6]=d.texture.height;v[7]=d.texture.depth_or_layers;v[8]=d.texture.levels;v[9]=static_cast<uint64_t>(d.texture.format);v[10]=d.texture.samples;}
 trace.emit(b::Resource,r.handle,label(p),v,true);
}
inline void resourceEnd(a::device* p,a::resource r){trace.emit(b::ResourceEnd,r.handle,label(p),{},true);}
inline void view(a::device* p,a::resource r,a::resource_usage usage,const a::resource_view_desc& d,a::resource_view v){
 std::array<uint64_t,11> args{r.handle,static_cast<uint64_t>(usage),static_cast<uint64_t>(d.type),static_cast<uint64_t>(d.format)};
 if(d.type==a::resource_view_type::buffer||d.type==a::resource_view_type::acceleration_structure){args[4]=d.buffer.offset;args[5]=d.buffer.size;}
 else {args[4]=d.texture.first_level;args[5]=d.texture.level_count;args[6]=d.texture.first_layer;args[7]=d.texture.layer_count;}
 trace.emit(b::View,v.handle,label(p),args,true);
}
inline void viewEnd(a::device* p,a::resource_view v){trace.emit(b::ViewEnd,v.handle,label(p),{},true);}
inline void command(a::command_list* c){trace.emit(b::Command,label(c),label(c->get_device()),{},true);}
inline void commandEnd(a::command_list* c){trace.emit(b::CommandEnd,label(c),label(c->get_device()),{},true);}
inline void reset(a::command_list* c){trace.emit(b::CommandReset,label(c),label(c->get_device()),{},true);}
inline void targets(a::command_list* c,uint32_t n,const a::resource_view* r,a::resource_view d){
 std::array<uint64_t,11> v{n,d.handle};for(unsigned i=0;i<n&&i<8;++i)v[2+i]=r[i].handle;
 trace.emit(b::Targets,label(c),label(c->get_device()),v,true);
}
inline bool draw(a::command_list* c,uint32_t n,uint32_t instances,uint32_t first,uint32_t fi){const auto seq=trace.emit(b::Draw,label(c),label(c->get_device()),{n,instances,first,fi});origin(c,seq);return false;}
inline bool indexed(a::command_list* c,uint32_t n,uint32_t instances,uint32_t first,int32_t offset,uint32_t fi){const auto seq=trace.emit(b::Indexed,label(c),label(c->get_device()),{n,instances,first,static_cast<uint64_t>(static_cast<int64_t>(offset)),fi});origin(c,seq);return false;}
inline uint64_t bits(float f){uint32_t v;std::memcpy(&v,&f,4);return v;}
inline bool clearDepth(a::command_list* c,a::resource_view v,const float* depth,const uint8_t* stencil,uint32_t n,const a::rect*){trace.emit(b::ClearDepth,label(c),label(c->get_device()),{v.handle,depth?1u:0u,depth?bits(*depth):0,stencil?1u:0u,stencil?*stencil:0u,n});return false;}
inline bool clearColor(a::command_list* c,a::resource_view v,const float color[4],uint32_t n,const a::rect*){trace.emit(b::ClearColor,label(c),label(c->get_device()),{v.handle,bits(color[0]),bits(color[1]),bits(color[2]),bits(color[3]),n});return false;}
inline bool copy(a::command_list* c,a::resource src,a::resource dst){trace.emit(b::Copy,label(c),label(c->get_device()),{src.handle,dst.handle});return false;}
inline bool copyTexture(a::command_list* c,a::resource src,uint32_t si,const a::subresource_box*,a::resource dst,uint32_t di,const a::subresource_box*,a::filter_mode filter){trace.emit(b::CopyTexture,label(c),label(c->get_device()),{src.handle,dst.handle,si,di,static_cast<uint64_t>(filter)});return false;}
inline bool resolve(a::command_list* c,a::resource src,uint32_t si,const a::subresource_box*,a::resource dst,uint32_t di,uint32_t x,uint32_t y,uint32_t z,a::format format){trace.emit(b::Resolve,label(c),label(c->get_device()),{src.handle,dst.handle,si,di,x,y,z,static_cast<uint64_t>(format)});return false;}
inline void viewport(a::command_list* c,uint32_t first,uint32_t n,const a::viewport* v){for(uint32_t i=0;i<n;++i)trace.emit(b::Viewport,label(c),label(c->get_device()),{first+i,bits(v[i].x),bits(v[i].y),bits(v[i].width),bits(v[i].height),bits(v[i].min_depth),bits(v[i].max_depth)});}
inline void pipeline(a::command_list* c,a::pipeline_stage stage,a::pipeline p){trace.emit(b::Pipeline,label(c),label(c->get_device()),{static_cast<uint64_t>(stage),p.handle});}
inline void states(a::command_list* c,uint32_t n,const a::dynamic_state* states,const uint32_t* values){for(uint32_t i=0;i<n;++i)trace.emit(b::States,label(c),label(c->get_device()),{static_cast<uint64_t>(states[i]),values[i]});}
inline void execute(a::command_queue* q,a::command_list* c){trace.emit(b::Execute,label(c),label(q->get_device()),{label(q)});}
inline void present(a::command_queue* q,a::swapchain* s,const a::rect*,const a::rect*,uint32_t,const a::rect*){trace.emit(b::Present,label(q),label(q->get_device()),{label(s),s->get_current_back_buffer().handle});}
#include "survey_extra.h"
inline void events(bool add){
#define B_EVENT(name,fn) if(add)reshade::register_event<reshade::addon_event::name>(fn);else reshade::unregister_event<reshade::addon_event::name>(fn)
 B_EVENT(init_device,device);B_EVENT(destroy_device,deviceEnd);
 B_EVENT(init_resource,resource);B_EVENT(destroy_resource,resourceEnd);
 B_EVENT(init_resource_view,view);B_EVENT(destroy_resource_view,viewEnd);
 B_EVENT(init_command_list,command);B_EVENT(destroy_command_list,commandEnd);B_EVENT(reset_command_list,reset);
 B_EVENT(bind_render_targets_and_depth_stencil,targets);B_EVENT(draw,draw);B_EVENT(draw_indexed,indexed);
 B_EVENT(clear_depth_stencil_view,clearDepth);B_EVENT(clear_render_target_view,clearColor);
 B_EVENT(copy_resource,copy);B_EVENT(copy_texture_region,copyTexture);B_EVENT(resolve_texture_region,resolve);
 B_EVENT(bind_viewports,viewport);B_EVENT(bind_pipeline,pipeline);B_EVENT(bind_pipeline_states,states);
 B_EVENT(execute_command_list,execute);B_EVENT(present,present);extraEvents(add);
#undef B_EVENT
}
}
