#include <iostream>
#include <cmath>

double compute_stop_distance(double speed, double friction) {
    constexpr double g = 9.81;
    return (speed * speed) / (2.0 * friction * g);
}

int main() {
    double speed, friction;

    std::cout << "속도 [m/s]: ";
    std::cin >> speed;
    std::cout << "마찰계수: ";
    std::cin >> friction;

    if (speed < 0.0 || friction <= 0.0) {
        std::cerr << "오류: 속도 >= 0, 마찰계수 > 0 이어야 합니다. \n";
        return 1;
    }

    double dist = compute_stop_distance(speed, friction);
    std::cout << "정지 거리: " << dist << " m\n";

    return 0;
}