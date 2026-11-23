#pragma once
#include <array>
#include <cmath>
// Adapter-only conversion. SFC packets remain column-vector, native units.
namespace SFCSource {
using Point = std::array<double, 4>;
using Matrix = std::array<Point, 4>;
inline Matrix Identity() { return {{{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}}}; }
inline Matrix Transpose(const Matrix& a) {
    Matrix b{}; for (int r=0;r<4;++r) for (int c=0;c<4;++c) b[r][c]=a[c][r]; return b;
}
inline Matrix Multiply(const Matrix& a, const Matrix& b) {
    Matrix v{}; for(int r=0;r<4;++r) for(int c=0;c<4;++c) for(int k=0;k<4;++k) v[r][c]+=a[r][k]*b[k][c]; return v;
}
inline Point Apply(const Matrix& a, const Point& p) {
    Point v{}; for(int r=0;r<4;++r) for(int c=0;c<4;++c) v[r]+=a[r][c]*p[c]; return v;
}
inline Point RowApply(const Matrix& a, const Point& p) { return Apply(Transpose(a),p); }
inline Point Basis(const Point& p) { return {-p[2],p[0],p[1],p[3]}; }
inline double Determinant(const Matrix& a) {
    return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);
}
inline bool ValidAffine(const Matrix& a) {
    for(const auto& row:a) for(double n:row) if(!std::isfinite(n)) return false;
    return a[3]==Point{0,0,0,1} && std::abs(Determinant(a))>1e-12;
}
// Call only after ValidAffine at the input boundary.
inline Matrix InverseAffine(const Matrix& a) {
    Matrix b=Identity(); const double d=Determinant(a);
    for(int r=0;r<3;++r) for(int c=0;c<3;++c)
        b[r][c]=(a[(c+1)%3][(r+1)%3]*a[(c+2)%3][(r+2)%3]-a[(c+1)%3][(r+2)%3]*a[(c+2)%3][(r+1)%3])/d;
    for(int r=0;r<3;++r) for(int c=0;c<3;++c) b[r][3]-=b[r][c]*a[c][3];
    return b;
}
inline Matrix InverseRow(const Matrix& a) { return Transpose(InverseAffine(Transpose(a))); }
inline Matrix ToUERow(const Matrix& a) {
    const Matrix basis={{{0,0,-1,0},{1,0,0,0},{0,1,0,0},{0,0,0,1}}};
    return Transpose(Multiply(Multiply(basis,a),Transpose(basis)));
}
inline Matrix ProjectionToUERow(const Matrix& p) {
    Matrix u{}; u[0][0]=p[0][0]; u[1][1]=p[1][1];
    u[2][0]=-p[0][2]; u[2][1]=-p[1][2]; u[2][2]=(1+p[2][2])/2;
    u[2][3]=1; u[3][2]=-p[2][3]/2; return u;
}
inline std::array<double,2> Project(const Matrix& p,const Point& v,const Point& viewport) {
    auto clip=Apply(p,v);
    return {viewport[0]+(1+clip[0]/clip[3])*viewport[2]/2,viewport[1]+(1-clip[1]/clip[3])*viewport[3]/2};
}
}
