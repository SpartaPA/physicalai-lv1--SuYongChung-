#include <iostream>
#include <memory>         
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>        
#include <cmath>           

class Sensor {
public:
    Sensor(const std::string& name) : name_(name) {
        std::cout << "[Sensor 생성] " << name_ << "\n";
    }
    virtual ~Sensor() {
        std::cout << "[Sensor 소멸] " << name_ << "\n";
    }

    virtual double read() = 0;
    std::string get_name() const { return name_; }

protected:
    std::string name_;
};

class Lidar : public Sensor {
public:
    Lidar(const std::string& name) : Sensor(name) {}
    ~Lidar() override {
        std::cout << "[Lidar 소멸] " << name_ << "\n";
    }

    double read() override {
        double value = 2.5 + (rand() % 100) / 100.0;
        std::cout << "[Lidar] " << name_ << " 거리: " << value << " m\n";
        return value;
    }
};


class Imu : public Sensor {
public:
    Imu(const std::string& name) : Sensor(name) {}
    ~Imu() override {
        std::cout << "[Imu 소멸] " << name_ << "\n";
    }

    double read() override {
        double value = 9.81 + (rand() % 50) / 100.0;
        std::cout << "[Imu] " << name_ << " 가속도: " << value << " m/s²\n";
        return value;
    }
};

template <typename T>
T my_clamp(T value, T min_val, T max_val) {
    if (value < min_val) return min_val;
    if (value > max_val) return max_val;
    return value;
}

int main() {
    std::cout << "===== 1. 다형성 루프 =====\n";
    std::vector<std::unique_ptr<Sensor>> sensors;
    sensors.push_back(std::make_unique<Lidar>("front_lidar"));
    sensors.push_back(std::make_unique<Imu>("body_imu"));
    sensors.push_back(std::make_unique<Lidar>("rear_lidar"));

    for (auto& s : sensors) {
        s->read();
    }

    std::cout << "\n===== 프로그램 종료, 소멸 순서 관찰 =====\n";

    std::cout << "\n===== 2. 스택 vs 힙 소멸 시점 =====\n";
    {
        std::cout << "-- 블록 시작 --\n";
        Lidar stack_lidar("stack_sensor");         
        auto heap_lidar = std::make_unique<Lidar>("heap_sensor");  
        
        stack_lidar.read();
        heap_lidar->read();
        std::cout << "-- 블록 끝 --\n";
    }  
    std::cout << "-- 블록 바깥 --\n";

    std::cout << "\n===== 3. unordered_map + count_if =====\n";
    std::unordered_map<std::string, double> latest;
    for (auto& s : sensors) {
        latest[s->get_name()] = s->read();
    }

    std::cout << "\n최근 측정값:\n";
    for (auto& [name, value] : latest) {
        std::cout << "  " << name << " = " << value << "\n";
    }

    std::vector<double> distance_log = {
        0.3, 1.2, 0.45, 0.1, 2.5, 0.49, 0.05, 3.1, 0.5, 0.51
    };

    int close_count = std::count_if(
        distance_log.begin(), distance_log.end(),
        [](double d) { return d <= 0.35; }
    );

    std::cout << "\n거리 로그 " << distance_log.size() << "개 중 "
              << "0.35 이내: " << close_count << "개\n";

    std::cout << "\n===== 4. 함수 템플릿 clamp =====\n";
    double speed = 15.7;
    double clamped_speed = my_clamp(speed, 0.0, 10.0);
    std::cout << "속도 " << speed << " → clamp(0~10): " << clamped_speed << "\n";

    int pixel = 300;
    int clamped_pixel = my_clamp(pixel, 0, 255);
    std::cout << "픽셀 " << pixel << " → clamp(0~255): " << clamped_pixel << "\n";

    std::cout << "\n===== 5. 메모리 누수 재현 =====\n";
    std::cout << "--- new로 할당, delete 없이 루프 ---\n";
    for (int i = 0; i < 5; i++) {
        Lidar* raw = new Lidar("leak_lidar_" + std::to_string(i));
        raw->read();
    }
    std::cout << "--- 루프 끝 (소멸 로그 없음 = 누수!) ---\n";

    std::cout << "\n--- make_unique로 수정 ---\n";
    for (int i = 0; i < 5; i++) {
        auto safe = std::make_unique<Lidar>("safe_lidar_" + std::to_string(i));
        safe->read();
    }
    std::cout << "--- 루프 끝 (소멸 로그 있음 = 누수 없음) ---\n";
    return 0;
}