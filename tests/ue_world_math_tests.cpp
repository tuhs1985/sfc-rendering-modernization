#include "../src/ue_wrapper/Plugins/SFCBridge/Source/SFCBridgeRuntime/Public/SFCSourceMath.h"
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
using namespace SFCSource;
int main() {
    int checks = 0;
    auto expect = [&](bool ok) { ++checks; if (!ok) throw std::runtime_error("world conversion check " + std::to_string(checks)); };
    Matrix model = Identity(), view = Identity();
    model[0][3] = 8; model[1][3] = 3; model[2][3] = -20;
    view[0][0] = 0; view[0][2] = -1; view[2][0] = 1; view[2][2] = 0;
    view[0][3] = 2; view[1][3] = -1;
    const Point local{2, 4, 6, 1};
    const Point original = local;
    const Matrix world = ToUERow(model);
    const Matrix camera = ToUERow(InverseAffine(view));
    const Point ueLocal = Basis(local);
    const auto ueCameraPoint = RowApply(InverseRow(camera), RowApply(world, ueLocal));
    const auto expected = Basis(Apply(view, Apply(model, local)));
    for (int i = 0; i < 4; ++i) expect(std::abs(ueCameraPoint[i] - expected[i]) < 1e-9);
    expect(local == original);
    Matrix other = model; other[0][3] += 19;
    expect(RowApply(ToUERow(other), ueLocal) != RowApply(world, ueLocal));
    expect(RowApply(world, ueLocal) == RowApply(ToUERow(model), ueLocal));
    auto shifted = view; shifted[2][3] += 10;
    expect(ToUERow(model) == world);
    expect(ToUERow(InverseAffine(shifted)) != camera);
    auto projection = Identity(); projection[0][0] = 2; projection[1][1] = 3;
    projection[2][2] = -1.02; projection[2][3] = -2.02;
    projection[3][2] = -1; projection[3][3] = 0;
    auto screen = Project(projection, Point{1,2,-10,1}, {200,30,1720,1020});
    expect(std::abs(screen[0] - 1232) < 1e-9);
    expect(std::abs(screen[1] - 234) < 1e-9);
    const auto ueProjection = ProjectionToUERow(projection);
    auto clip = RowApply(ueProjection, Point{1,2,10,1});
    expect(std::abs(clip[0]/clip[3] - .2) < 1e-9);
    expect(std::abs(clip[1]/clip[3] - .6) < 1e-9);
    expect(std::abs(clip[2]/clip[3] - .091) < 1e-9);
    auto invalid = view; invalid[0][0] = std::numeric_limits<double>::quiet_NaN();
    expect(!ValidAffine(invalid));
    invalid = {}; expect(!ValidAffine(invalid));
    for (int step=0;step<200;++step) {
        const double a=step*.031, b=step*.071;
        Matrix m=Identity(), v=Identity();
        m[0][0]=m[2][2]=std::cos(a); m[0][2]=-std::sin(a); m[2][0]=std::sin(a);
        v[0][0]=v[1][1]=std::cos(b); v[0][1]=-std::sin(b); v[1][0]=std::sin(b);
        m[0][3]=step; m[2][3]=-50;
        v[1][3]=-step*.5;
        const auto actual=RowApply(InverseRow(ToUERow(InverseAffine(v))),RowApply(ToUERow(m),Basis(local)));
        const auto source=Basis(Apply(v,Apply(m,local)));
        for(int i=0;i<4;++i) expect(std::abs(actual[i]-source[i])<1e-8);
        expect(local==original);
    }
    const Point delta{-25,0,8,0};Matrix diagnostic{};
    expect(DiagnosticWorldOffset(model,delta,diagnostic));
    const auto fixedWorld=ToUERow(diagnostic);
    for(int step=0;step<200;++step){
        const double a=step*.031;Matrix cameraView=Identity();
        cameraView[0][0]=cameraView[2][2]=std::cos(a);cameraView[0][2]=-std::sin(a);cameraView[2][0]=std::sin(a);
        const auto nativeOriginal=Apply(model,local),nativeShifted=Apply(diagnostic,local);
        for(int axis=0;axis<4;++axis)expect(std::abs(nativeShifted[axis]-nativeOriginal[axis]-delta[axis])<1e-9);
        const auto displayed=RowApply(InverseRow(ToUERow(InverseAffine(cameraView))),RowApply(ToUERow(diagnostic),Basis(local)));
        const auto correct=Basis(Apply(cameraView,nativeShifted));
        for(int axis=0;axis<4;++axis)expect(std::abs(displayed[axis]-correct[axis])<1e-9);
        expect(ToUERow(diagnostic)==fixedWorld); // Camera cannot mutate the fixed world placement.
    }
    const auto preserved=diagnostic;
    expect(!DiagnosticWorldOffset(model,{1,0,0,1},diagnostic)&&diagnostic==preserved);
    expect(!DiagnosticWorldOffset(model,{std::numeric_limits<double>::infinity(),0,0,0},diagnostic)&&diagnostic==preserved);
    expect(!DiagnosticWorldOffset(Matrix{},delta,diagnostic)&&diagnostic==preserved);
    std::cout << "UE world math PASS " << checks << " checks\n";
}
