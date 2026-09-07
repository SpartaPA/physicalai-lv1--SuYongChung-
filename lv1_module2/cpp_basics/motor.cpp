#include "motor.hpp"
#include <algorithm>  // std::clamp
#include <iostream>

Motor::Motor(const std::string& name, double max_rpm)
    : name_(name), max_rpm_(max_rpm), current_rpm_(0.0) {
    std::cout << "[Motor] " << name_ << " 생성됨 (최대 " << max_rpm_ << " RPM)\n";
}

void Motor::set_speed(double rpm) {
    current_rpm_ = std::clamp(rpm, 0.0, max_rpm_);
    std::cout << "[Motor] " << name_ << " 속도 설정: " << current_rpm_ << " RPM\n";
}

double Motor::get_speed() const {
    return current_rpm_;
}

std::string Motor::get_name() const {
    return name_;
}// modified
