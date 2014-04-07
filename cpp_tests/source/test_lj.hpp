#include "pele/array.h"
#include "pele/lj.h"
#include <iostream>
#include <stdexcept>
#include <vector>
#include <gtest/gtest.h>
#include <cmath>

using pele::Array;


TEST(LJInteractionTest, Energy_Works){
    double r2 = 1.1;
    double c6 = 1.2;
    double c12 = 2.3;
    pele::lj_interaction ljint(c6, c12);
    ASSERT_NEAR(ljint.energy(r2, 1, 2), 0.39671227804179443, 1e-10);
}

TEST(LJInteractionTest, EnergyGradient_Works){
    double r2 = 1.1;
    double c6 = 1.2;
    double c12 = 2.3;
    pele::lj_interaction ljint(c6, c12);
    double g = 0;
    double e = ljint.energy_gradient(r2, &g, 1, 2);
    ASSERT_NEAR(e, 0.39671227804179443, 1e-10);
    ASSERT_NEAR(g, 9.2454671845389917, 1e-10);
}

class LJTest :  public ::testing::Test
{
public:
    double c6, c12, etrue;
    Array<double> x;
    void SetUp(){
        c6 = 1.2;
        c12 = 2.3;
        x = Array<double>(6);
        x[0]  = 0.1;
        x[1]  = 0.2;
        x[2]  = 0.3;
        x[3]  = 0.44;
        x[4]  = 0.55;
        x[5]  = 1.66;
        etrue = -0.10410023149146598;
    }
};

TEST_F(LJTest, Energy_Works){
    pele::LJ lj(c6, c12);
    double e = lj.get_energy(x);
    ASSERT_NEAR(e, etrue, 1e-10);
}

TEST_F(LJTest, EnergyGradient_Works){
    pele::LJ lj(c6, c12);
    Array<double> g(6);
    double e = lj.get_energy_gradient(x, g);
    ASSERT_NEAR(e, etrue, 1e-10);
    ASSERT_NEAR(g[0], -0.07457726800542995, 1e-10);
    ASSERT_NEAR(g[1], -0.076770717064413199, 1e-10);
    ASSERT_NEAR(g[2], -0.2983090720217198, 1e-10);
    ASSERT_NEAR(g[0], -g[3], 1e-10);
    ASSERT_NEAR(g[1], -g[4], 1e-10);
    ASSERT_NEAR(g[2], -g[5], 1e-10);
}
