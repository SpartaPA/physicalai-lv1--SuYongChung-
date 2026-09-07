#ifndef MOTOR_HPP
#define MOTOR_HPP

#include <string>

class Motor {
public:
    Motor(const std::string& name, double max_rpm);
    void set_speed(double rpm);
    double get_speed() const;
    std::string get_name() const;

private:
    std::string name_;
    double max_rpm_;
    double current_rpm_;
};

#endif