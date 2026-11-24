#pragma once
// Receiver-worker front end only. No additional game pool or renderer scheduler.
#include "ue_game_output_contract.h"
#include "../../../tools/d3d9_proof/game_output_writer.h"
namespace sfc_ue_game {
class Writer {
    GameOutputWriter output;
    Activation activation{};
    bool bound=false,allowReplay=false;
    multi_scene::Frame sourceFrame{};
    sfc_source_view::Frame frame{};
    sfc_ue_export::Handle game;
    sfc_ue_output::Normalizer::Targets targets[2];
    uint32_t targetGeneration=0;
public:
    uint64_t published=0,discarded=0,busy=0;
    explicit Writer(bool replay):allowReplay(replay){
        output.nativePixels=true;
        output.start();check(output.enabled,"UE game pool requires explicit game-output mode");
        check(output.source.prepare()&&output.source.requested,"UE game pool source session missing");
        check(!replacement::requested(),"UE additive output cannot suppress originals");
    }
    bool admit(const sfc_ue_export::Packet& p,output_wire::Packet& packetOut,game_output::Metadata& meta){
        auto* base=reinterpret_cast<BYTE*>(output.source.mailbox)-sfc_calibration::Offset;
        auto* scene=reinterpret_cast<multi_scene::Store*>(base+multi_scene::Offset);
        const auto* live=reinterpret_cast<live_owner::Store*>(base+live_owner::Offset);
        const auto pid=scene->header.pid;
        if(!pid||!multi_scene::valid(scene->header,output.source.session,pid)||!live_owner::header_valid(live->header,output.source.session)||live->header.pid!=pid)return false;
        if(!multi_scene::read(*scene,DWORD(p.identity.frame),p.identity.sequence,sourceFrame))return false;
        if(!bound){
            const uint64_t chosen=uint64_t(InterlockedCompareExchange64(const_cast<volatile LONG64*>(&live->header.selected),0,0));
            const DWORD owner=DWORD(chosen),revision=DWORD(chosen>>32);
            if(!owner||!revision||revision>multi_scene::Assets)return false;
            multi_scene::Asset asset{};
            if(!multi_scene::read(scene->assets[revision-1],asset)||asset.owner!=owner||asset.revision!=revision)return false;
            Activation candidate{};std::memcpy(candidate.session.data(),output.source.session,16);
            candidate.game=pid;candidate.owner=owner;candidate.revision=revision;candidate.model=asset.model;candidate.source=asset.source;
            std::memcpy(candidate.asset.data(),asset.content,32);candidate.generation=1;
            activation=candidate;
        }
        if(pid!=activation.game)return false;
        output_target::Notice target{};
        if(!output_target::read(*reinterpret_cast<output_target::Store*>(base+output_target::Offset),target))return false;
        std::memcpy(&frame,&sourceFrame,sizeof(frame));
        if(!qualifies(p,activation,frame,target,allowReplay)){++discarded;return false;}
        if(!bound){
            game.value=OpenProcess(SYNCHRONIZE,FALSE,pid);check(game.value!=nullptr,"UE output source process");
            BYTE asset[32]{};std::memcpy(asset,activation.asset.data(),32);output.bind(asset,0);bound=true;
        }
        if(WaitForSingleObject(game.value,0)!=WAIT_TIMEOUT)return false;
        packetOut=packet(p);meta=metadata(p);return true;
    }
    int reserve(ID3D11Device* device,const output_wire::Packet& p,const game_output::Metadata& meta,sfc_ue_output::Normalizer& normalizer){
        output.prepare(device,p);const int slot=output.reserve(p,meta);if(slot<0){++busy;return -1;}
        const auto generation=output.pool->reserved[1];
        if(generation!=targetGeneration){for(auto& item:targets)item={};targetGeneration=generation;}
        if(!targets[slot].views[0]){
            ID3D11Texture2D* images[3]{};for(unsigned n=0;n<3;++n)images[n]=output.textures[slot][n].Get();
            targets[slot]=normalizer.bind_targets(images);
        }
        return slot;
    }
    const sfc_ue_output::Normalizer::Targets& target(unsigned slot)const{return targets[slot];}
    ID3D11Texture2D* image(unsigned slot,unsigned plane)const{return output.textures[slot][plane].Get();}
    void publish(int slot,output_wire::Packet p,const game_output::Metadata& meta){
        p.published_qpc=sfc_ue_export::now();output.publish(slot,p,meta);++published;
    }
    bool retire(){
        if(!output.pool)return true;
        if(!output.retire())return false;
        for(auto& item:targets)item={};targetGeneration=0;return true;
    }
};
}
