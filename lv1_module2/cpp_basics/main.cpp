#include <iostream>
#include "motor.hpp"

int main() {
    Motor left("left_wheel", 3000.0);
    Motor right("right_wheel", 3000.0);

    left.set_speed(1500.0);
    right.set_speed(5000.0);  // max_rpm 초과 → 3000으로 잘림

    std::cout << "\n=== 모터 상태 ===\n";
    std::cout << left.get_name()  << ": " << left.get_speed()  << " RPM\n";
    std::cout << right.get_name() << ": " << right.get_speed() << " RPM\n";

    return 0;
}